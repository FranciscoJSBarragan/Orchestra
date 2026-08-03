// OrchestraHubMenu: read-only menu bar viewer for the Orchestra Hub.
// See ../SPEC-CLIENTS.md section 5 for the frozen design.
import AppKit
import Foundation
import UserNotifications

let defaultPort = 7343
let pollSeconds: TimeInterval = 30
let titleCap = 40
let blockerCap = 80

func readPort() -> Int {
    let file = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent(".orchestra/hub.toml")
    guard let content = try? String(contentsOf: file, encoding: .utf8) else {
        return defaultPort
    }
    let pattern = #"^port\s*=\s*(\d+)\s*$"#
    guard let regex = try? NSRegularExpression(pattern: pattern) else {
        return defaultPort
    }
    for rawLine in content.components(separatedBy: .newlines) {
        let line = rawLine.trimmingCharacters(in: .whitespaces)
        let range = NSRange(line.startIndex..., in: line)
        guard let match = regex.firstMatch(in: line, range: range),
              let group = Range(match.range(at: 1), in: line),
              let port = Int(line[group]), port > 0, port < 65536 else {
            continue
        }
        return port
    }
    return defaultPort
}

struct ActiveRepo {
    let name: String
    let tasks: [[String: Any]]
}

enum HubState {
    case ok([ActiveRepo], totalActive: Int)
    case unreachable(String)
}

func activeRepos(from summary: [String: Any]) -> [ActiveRepo] {
    let repositories = summary["repositories"] as? [[String: Any]] ?? []
    let tasks = summary["tasks"] as? [[String: Any]] ?? []
    var names: [String: String] = [:]
    for repo in repositories {
        if let path = repo["path"] as? String {
            names[path] = repo["name"] as? String ?? path
        }
    }
    var grouped: [String: [[String: Any]]] = [:]
    var order: [String] = []
    for task in tasks where (task["status"] as? String) != "completed" {
        let path = task["repository"] as? String ?? ""
        if grouped[path] == nil { order.append(path) }
        grouped[path, default: []].append(task)
    }
    return order.sorted {
        name(for: $0, names) < name(for: $1, names)
    }.map { path in
        ActiveRepo(name: name(for: path, names), tasks: grouped[path] ?? [])
    }
}

func name(for path: String, _ names: [String: String]) -> String {
    if let known = names[path], !known.isEmpty { return known }
    let base = (path as NSString).lastPathComponent
    return base.isEmpty ? path : base
}

// Title next to the template icon; empty when idle (icon alone).
func statusTitle(for state: HubState) -> String {
    switch state {
    case .unreachable:
        return "!"
    case .ok(let repos, let total):
        if repos.isEmpty { return "" }
        let title: String
        if repos.count == 1 {
            title = "\(repos[0].name) \(repos[0].tasks.count)"
        } else {
            title = "\(repos.count) repos · \(total)"
        }
        return title.count > titleCap
            ? String(title.prefix(titleCap - 1)) + "…" : title
    }
}

final class HubMonitor: NSObject, NSApplicationDelegate {
    private var statusItem: NSStatusItem!
    private var timer: Timer?
    private var etag: String?
    private var lastSuccess: Date?
    private var knownBlockers: Set<String>?
    private let port = readPort()
    private var panelURL: URL {
        URL(string: "http://127.0.0.1:\(port)/")!
    }
    private var summaryURL: URL {
        URL(string: "http://127.0.0.1:\(port)/v1/summary")!
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        statusItem = NSStatusBar.system.statusItem(
            withLength: NSStatusItem.variableLength
        )
        if let button = statusItem.button {
            button.image = NSImage(
                systemSymbolName: "point.3.connected.trianglepath.dotted",
                accessibilityDescription: "Orchestra Hub"
            )
            button.imagePosition = .imageLeading
        }
        UNUserNotificationCenter.current().requestAuthorization(
            options: [.alert, .sound]
        ) { _, _ in }
        render(.unreachable("starting"))
        timer = Timer.scheduledTimer(
            withTimeInterval: pollSeconds, repeats: true
        ) { [weak self] _ in self?.poll() }
        poll()
    }

    @objc func refreshNow() {
        etag = nil
        poll()
    }

    @objc func openPanel() {
        NSWorkspace.shared.open(panelURL)
    }

    @objc func quit() {
        NSApp.terminate(nil)
    }

    private func poll() {
        var request = URLRequest(url: summaryURL, timeoutInterval: 5)
        if let etag { request.setValue(etag, forHTTPHeaderField: "If-None-Match") }
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async { self?.handle(data, response, error) }
        }.resume()
    }

    private func handle(_ data: Data?, _ response: URLResponse?, _ error: Error?) {
        if let error {
            render(.unreachable(error.localizedDescription))
            return
        }
        guard let http = response as? HTTPURLResponse else {
            render(.unreachable("no response"))
            return
        }
        if http.statusCode == 304 { return }
        guard http.statusCode == 200, let data,
              let object = try? JSONSerialization.jsonObject(with: data),
              let summary = object as? [String: Any],
              summary["status"] as? String == "ok" else {
            render(.unreachable("HTTP \(http.statusCode)"))
            return
        }
        etag = http.value(forHTTPHeaderField: "ETag")
        lastSuccess = Date()
        let repos = activeRepos(from: summary)
        let total = repos.reduce(0) { $0 + $1.tasks.count }
        notifyBlockerChanges(repos)
        render(.ok(repos, totalActive: total))
    }

    // One aggregated notification when blockers appear or clear (never
    // one per task; baseline on first successful poll, SPEC-CLIENTS §5).
    private func notifyBlockerChanges(_ repos: [ActiveRepo]) {
        var current: [String: String] = [:]
        for repo in repos {
            for task in repo.tasks {
                let blocker = task["blocker"] as? String ?? ""
                guard !blocker.isEmpty,
                      let id = task["id"] as? String else { continue }
                let label = task["label"] as? String ?? id
                current[id] = "\(label): \(String(blocker.prefix(blockerCap)))"
            }
        }
        defer { knownBlockers = Set(current.keys) }
        guard let known = knownBlockers else {
            if !current.isEmpty { notifyNeedsYou(current) }
            return
        }
        let added = Set(current.keys).subtracting(known)
        let removed = known.subtracting(current.keys)
        if !added.isEmpty {
            notifyNeedsYou(current.filter { added.contains($0.key) })
        } else if !removed.isEmpty {
            notify("Orchestra", removed.count == 1
                ? "A task is unblocked and moving again"
                : "\(removed.count) tasks are unblocked and moving again")
        }
    }

    private func notifyNeedsYou(_ blockers: [String: String]) {
        let body = blockers.count == 1
            ? blockers.values.first ?? ""
            : "\(blockers.count) tasks are waiting on you"
        notify("Orchestra needs you", body)
    }

    private func notify(_ title: String, _ body: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        UNUserNotificationCenter.current().add(UNNotificationRequest(
            identifier: UUID().uuidString, content: content, trigger: nil
        ))
    }

    private func render(_ state: HubState) {
        if let button = statusItem.button {
            let title = statusTitle(for: state)
            button.attributedTitle = NSAttributedString(
                string: title.isEmpty ? "" : " " + title,
                attributes: [
                    .font: NSFont.monospacedDigitSystemFont(
                        ofSize: NSFont.systemFontSize(for: .small),
                        weight: .medium
                    ),
                ]
            )
            if case .unreachable = state {
                button.contentTintColor = .systemRed
            } else {
                button.contentTintColor = nil
            }
        }
        let menu = NSMenu()
        switch state {
        case .unreachable:
            menu.addItem(styled("Hub unreachable — retrying",
                                color: .systemRed))
        case .ok(let repos, _):
            if repos.isEmpty {
                menu.addItem(styled("All quiet — no active tasks",
                                    color: .secondaryLabelColor))
            }
            for repo in repos {
                menu.addItem(styled(repo.name, color: .labelColor, bold: true))
                for task in repo.tasks {
                    let label = task["label"] as? String ?? ""
                    let stage = task["stage"] as? String ?? ""
                    let blocker = task["blocker"] as? String ?? ""
                    if blocker.isEmpty {
                        menu.addItem(styled(
                            "  ● \(label) — \(stage)",
                            color: .labelColor
                        ))
                    } else {
                        menu.addItem(styled(
                            "  ⛔ \(label) — needs you",
                            color: .systemRed
                        ))
                        menu.addItem(styled(
                            "      " + String(blocker.prefix(blockerCap)),
                            color: .secondaryLabelColor
                        ))
                    }
                }
            }
        }
        menu.addItem(.separator())
        menu.addItem(styled(updatedText(), color: .tertiaryLabelColor))
        menu.addItem(action("Open panel", #selector(openPanel)))
        menu.addItem(action("Refresh now", #selector(refreshNow)))
        menu.addItem(action("Quit", #selector(quit)))
        statusItem.menu = menu
    }

    private func updatedText() -> String {
        guard let lastSuccess else { return "Never updated" }
        let minutes = Int(Date().timeIntervalSince(lastSuccess) / 60)
        if minutes < 1 { return "Updated just now" }
        return "Updated \(minutes) min ago"
    }

    private func styled(_ title: String, color: NSColor,
                        bold: Bool = false) -> NSMenuItem {
        let item = NSMenuItem(title: title, action: nil, keyEquivalent: "")
        item.isEnabled = false
        let size = NSFont.systemFontSize(for: .regular)
        item.attributedTitle = NSAttributedString(
            string: title,
            attributes: [
                .font: bold
                    ? NSFont.boldSystemFont(ofSize: size)
                    : NSFont.menuFont(ofSize: size),
                .foregroundColor: color,
            ]
        )
        return item
    }

    private func action(_ title: String, _ selector: Selector) -> NSMenuItem {
        let item = NSMenuItem(title: title, action: selector, keyEquivalent: "")
        item.target = self
        return item
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let delegate = HubMonitor()
app.delegate = delegate
app.run()

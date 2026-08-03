// OrchestraHubMenu: read-only menu bar viewer for the Orchestra Hub.
// See ../SPEC-CLIENTS.md section 5 for the frozen design.
import AppKit
import Foundation

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

func statusTitle(for state: HubState) -> String {
    switch state {
    case .unreachable:
        return "⚠ Hub"
    case .ok(let repos, let total):
        if repos.isEmpty { return "◦" }
        let title: String
        if repos.count == 1 {
            title = "\(repos[0].name):\(repos[0].tasks.count)"
        } else {
            title = "\(repos.count) repos·\(total)"
        }
        return title.count > titleCap
            ? String(title.prefix(titleCap - 1)) + "…" : title
    }
}

final class HubMonitor: NSObject, NSApplicationDelegate {
    private var statusItem: NSStatusItem!
    private var timer: Timer?
    private var etag: String?
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
        let repos = activeRepos(from: summary)
        let total = repos.reduce(0) { $0 + $1.tasks.count }
        render(.ok(repos, totalActive: total))
    }

    private func render(_ state: HubState) {
        statusItem.button?.title = statusTitle(for: state)
        let menu = NSMenu()
        switch state {
        case .unreachable:
            menu.addItem(disabled("Hub unreachable"))
        case .ok(let repos, _):
            if repos.isEmpty {
                menu.addItem(disabled("No active tasks"))
            }
            for repo in repos {
                menu.addItem(disabled(repo.name))
                for task in repo.tasks {
                    let label = task["label"] as? String ?? ""
                    let stage = task["stage"] as? String ?? ""
                    let status = task["status"] as? String ?? ""
                    let blocker = task["blocker"] as? String ?? ""
                    let mark = blocker.isEmpty ? "" : "⛔ "
                    menu.addItem(disabled(
                        "  \(mark)\(label) — \(stage)/\(status)"
                    ))
                    if !blocker.isEmpty {
                        menu.addItem(disabled(
                            "      " + String(blocker.prefix(blockerCap))
                        ))
                    }
                }
            }
        }
        menu.addItem(.separator())
        menu.addItem(action("Open panel", #selector(openPanel)))
        menu.addItem(action("Refresh now", #selector(refreshNow)))
        menu.addItem(action("Quit", #selector(quit)))
        statusItem.menu = menu
    }

    private func disabled(_ title: String) -> NSMenuItem {
        let item = NSMenuItem(title: title, action: nil, keyEquivalent: "")
        item.isEnabled = false
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

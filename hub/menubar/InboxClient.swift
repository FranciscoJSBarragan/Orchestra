import Foundation

struct InboxTask {
    let id: String
    let title: String
    let disposition: String
    let runStatus: String?
    let pendingInteractions: Int
}

final class InboxClient {
    private let helper: String?

    init(environment: [String: String] = ProcessInfo.processInfo.environment) {
        let manager = FileManager.default
        let candidates: [String] = [
            environment["ORCHESTRA_TASK_CONTROL"],
            environment["CODEX_HOME"].map { "\($0)/orchestra/scripts/task_control.py" },
            manager.homeDirectoryForCurrentUser
                .appendingPathComponent(".codex/orchestra/scripts/task_control.py").path,
        ].compactMap { $0 }
        helper = candidates.first { manager.isExecutableFile(atPath: $0) || manager.fileExists(atPath: $0) }
    }

    func list(completion: @escaping (Result<[InboxTask], Error>) -> Void) {
        run(["task", "list", "--include-archived"]) { result in
            completion(result.flatMap { payload in
                guard let rows = payload["tasks"] as? [[String: Any]] else {
                    return .failure(InboxError.invalidResponse)
                }
                return .success(rows.compactMap { row in
                    guard let id = row["id"] as? String,
                          let title = row["title"] as? String,
                          let disposition = row["disposition"] as? String else { return nil }
                    let latest = row["latest_run"] as? [String: Any]
                    return InboxTask(
                        id: id,
                        title: title,
                        disposition: disposition,
                        runStatus: latest?["status"] as? String,
                        pendingInteractions: row["pending_interactions"] as? Int ?? 0
                    )
                })
            })
        }
    }

    func mutate(_ command: String, task: String,
                completion: @escaping (Result<[String: Any], Error>) -> Void) {
        let arguments: [String]
        if command == "reopen" {
            arguments = ["run", "reopen", "--task", task]
        } else {
            arguments = ["task", command, "--task", task]
        }
        run(arguments, completion: completion)
    }

    private func run(_ arguments: [String],
                     completion: @escaping (Result<[String: Any], Error>) -> Void) {
        guard let helper else {
            completion(.failure(InboxError.helperUnavailable))
            return
        }
        DispatchQueue.global(qos: .utility).async {
            let process = Process()
            process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
            process.arguments = ["python3", helper] + arguments
            let output = Pipe()
            process.standardOutput = output
            process.standardError = Pipe()
            do {
                try process.run()
                process.waitUntilExit()
                let data = output.fileHandleForReading.readDataToEndOfFile()
                guard let object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                      process.terminationStatus == 0,
                      object["status"] as? String == "ok" else {
                    throw InboxError.commandFailed
                }
                DispatchQueue.main.async { completion(.success(object)) }
            } catch {
                DispatchQueue.main.async { completion(.failure(error)) }
            }
        }
    }
}

enum InboxError: Error {
    case helperUnavailable
    case invalidResponse
    case commandFailed
}

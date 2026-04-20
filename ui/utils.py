import subprocess
import json
import os


def to_wsl_path(win_path):
    drive = win_path[0].lower()
    path_without_drive = win_path[2:]
    return f"/mnt/{drive}" + path_without_drive.replace("\\", "/")


def add_severity(threats):
    severity_map = {
        "dangerous_command": "HIGH",
        "reverse_shell": "CRITICAL",
        "privilege_escalation": "HIGH",
        "brute_force_attempt": "MEDIUM",
        "suspicious_ip": "LOW",
        "error_log": "LOW"
    }

    for t in threats:
        t["severity"] = severity_map.get(t["type"], "LOW")

    return threats


def run_analyzer(filepath):
    wsl_file = to_wsl_path(filepath)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analyzer_dir = os.path.join(base_dir, "analyzer")
    wsl_analyzer_dir = to_wsl_path(analyzer_dir)

    cmd = f"cd {wsl_analyzer_dir} && ./analyzer {wsl_file}"

    result = subprocess.run(
        ["wsl", "bash", "-c", cmd],
        capture_output=True,
        text=True
    )

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    try:
        data = json.loads(result.stdout)
        data["threats"] = add_severity(data["threats"])
        return data
    except:
        return {"threats": []}
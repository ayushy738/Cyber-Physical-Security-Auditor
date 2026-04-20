import subprocess
import json
import os

def to_wsl_path(win_path):
    drive = win_path[0].lower()   # e.g. 'E' → 'e'
    path_without_drive = win_path[2:]  # remove 'E:'

    return f"/mnt/{drive}" + path_without_drive.replace("\\", "/")


def run_analyzer(filepath):
    # Convert file path
    wsl_file = to_wsl_path(filepath)

    # Get analyzer directory (Windows)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analyzer_dir = os.path.join(base_dir, "analyzer")

    # Convert analyzer dir → WSL path
    wsl_analyzer_dir = to_wsl_path(analyzer_dir)

    # ✅ IMPORTANT: use cd inside WSL
    cmd = f"cd {wsl_analyzer_dir} && ./analyzer {wsl_file}"

    result = subprocess.run(
        ["wsl", "bash", "-c", cmd],
        capture_output=True,
        text=True
    )

    # Debug (VERY useful)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    try:
        return json.loads(result.stdout)
    except:
        return {"threats": []}
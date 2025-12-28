import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
FILES = sorted(ROOT.rglob("*.bas"), key=lambda p: str(p))
RESULTS_PATH = ROOT / "test_run_results.json"
LOG_PATH = ROOT / "test_run_summary.log"
INPUT_TIMEOUT = "5"
EXEC_TIMEOUT = "45"
PROC_TIMEOUT = 55

results = []
for idx, path in enumerate(FILES, 1):
    start = time.time()
    cmd = [
        sys.executable,
        "applesoft.py",
        str(path),
        "--input-timeout",
        INPUT_TIMEOUT,
        "--exec-timeout",
        EXEC_TIMEOUT,
        "--auto-close",
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=PROC_TIMEOUT,
        )
        rc = proc.returncode
        output = proc.stdout
    except subprocess.TimeoutExpired as exc:
        rc = -9
        output = (exc.stdout or "") + "\n[TIMEOUT]"
    duration = round(time.time() - start, 2)
    results.append(
        {
            "file": str(path.relative_to(ROOT)),
            "rc": rc,
            "duration_sec": duration,
            "output": output,
        }
    )
    print(f"[{idx}/{len(FILES)}] {path} rc={rc} t={duration}s", flush=True)

RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
failures = [item for item in results if item["rc"] != 0]
summary_lines = [f"Ran {len(results)} programs; failures: {len(failures)}"]
for item in failures:
    summary_lines.append(
        f"FAIL {item['file']} rc={item['rc']} time={item['duration_sec']}s"
    )
    summary_lines.append("\n".join(item["output"].splitlines()[:5]))
LOG_PATH.write_text("\n".join(summary_lines), encoding="utf-8")
for line in summary_lines:
    print(line)

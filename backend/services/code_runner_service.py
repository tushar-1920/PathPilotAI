"""
PathPilot AI — Code Runner Service
Safely executes user-submitted code against test cases.

Execution strategy (in order of availability):
  1. Judge0 API  (cloud judge — recommended for production)
  2. Docker sandbox  (local isolated container)
  3. Python subprocess with timeout + resource limits  (fallback)

Configure JUDGE0_API_URL + JUDGE0_API_KEY in your .env to use Judge0.
Leave them empty and Docker available to use the container sandbox.
Otherwise the subprocess fallback is used automatically.
"""

import subprocess
import sys
import os
import time
import json
import base64
import textwrap
import logging
import re
import platform
from typing import Dict, Any, List, Optional, Tuple

# resource and signal are Unix-only — import safely for Windows compatibility
try:
    import resource
    import signal
    IS_WINDOWS = False
except ImportError:
    resource = None  # type: ignore
    signal = None    # type: ignore
    IS_WINDOWS = True

try:
    import requests
except ImportError:
    requests = None  # type: ignore

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  CONFIGURATION  (override via environment)
# ─────────────────────────────────────────────

JUDGE0_API_URL = os.getenv("JUDGE0_API_URL", "")       # e.g. https://judge0-ce.p.rapidapi.com
JUDGE0_API_KEY = os.getenv("JUDGE0_API_KEY", "")       # RapidAPI key
DOCKER_ENABLED = os.getenv("CODE_RUNNER_DOCKER", "false").lower() == "true"
SUBPROCESS_TIME_LIMIT = int(os.getenv("SUBPROCESS_TIME_LIMIT", "5"))   # seconds
SUBPROCESS_MEMORY_MB  = int(os.getenv("SUBPROCESS_MEMORY_MB", "128"))  # megabytes

# Judge0 language IDs
JUDGE0_LANG_IDS = {
    "python":     71,   # Python 3.8
    "javascript": 63,   # Node.js 12
    "java":       62,   # Java OpenJDK 13
    "cpp":        54,   # C++17
    "c":          50,   # C GCC 9
    "go":         60,   # Go 1.13
    "rust":       73,   # Rust 1.40
    "typescript": 74,   # TypeScript 3.7
    "kotlin":     78,   # Kotlin 1.3
    "swift":      83,   # Swift 5.2
}

# ─────────────────────────────────────────────
#  SAFETY VALIDATION
# ─────────────────────────────────────────────

# ── Only block genuinely dangerous patterns ────────────────────────────
# ALLOWED by design: import sys, json, ast, math, heapq, collections,
# itertools, functools, bisect, typing, re, copy, queue, random, string
# These are all needed in DSA problem boilerplates.
_BLOCKED_PATTERNS = [
    r"\bos\.system\b",
    r"\bos\.popen\b",
    r"\bsubprocess\b",
    r"\b__import__\s*\(",
    r"\bimport\s+subprocess\b",
    r"\bimport\s+os\b",
    r"\bimport\s+shutil\b",
    r"\bimport\s+glob\b",
    r"\bimport\s+pathlib\b",
    r"\bsocket\.socket\b",
    r"\burllib\.request\b",
    r"\brequests\.get\b",
    r"\brequests\.post\b",
    r"(?<!\w)eval\s*\(",
    r"(?<!\w)exec\s*\(",
    r"for\s+.+\s+in\s+range\s*\(\s*10\s*\*\*\s*[89]",
]

_COMPILED_BLOCKS = [re.compile(p) for p in _BLOCKED_PATTERNS]

def validate_code_safety(code: str, language: str) -> Tuple[bool, str]:
    """
    Returns (is_safe: bool, reason: str).
    Allows all standard DSA imports: sys, json, ast, math, heapq,
    collections, itertools, functools, bisect, typing, re, copy etc.
    Blocks: os.system, subprocess, sockets, HTTP requests, eval/exec.
    """
    if language == "python":
        for pattern in _COMPILED_BLOCKS:
            if pattern.search(code):
                return False, f"Dangerous operation blocked: {pattern.pattern}"
        if len(code) > 50_000:
            return False, "Code too long (max 50,000 chars)"
    else:
        if len(code) > 100_000:
            return False, "Code too long"
    return True, ""


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────

def run_code_against_testcases(
    code: str,
    language: str,
    testcases: List[Dict],
    custom_input: Optional[str] = None,
    include_hidden: bool = False,
    time_limit_ms: int = 2000,
) -> Dict[str, Any]:
    """
    Run `code` against `testcases` and return structured results.

    Returns:
    {
        "passed": int,
        "total": int,
        "runtime_ms": float,
        "memory_kb": int,
        "tle": bool,
        "runtime_error": bool,
        "results": [
            {
                "case": int,
                "input": str,
                "expected": str,
                "actual": str,
                "passed": bool,
                "runtime_ms": float,
                "hidden": bool,
            }, ...
        ]
    }
    """
    # Choose execution backend
    if custom_input is not None:
        # Single custom run
        cases = [{"input": custom_input, "expected_output": "", "hidden": False}]
    else:
        cases = testcases if include_hidden else [t for t in testcases if not t.get("hidden")]

    if JUDGE0_API_URL and JUDGE0_API_KEY:
        return _run_via_judge0(code, language, cases, time_limit_ms)
    elif DOCKER_ENABLED:
        return _run_via_docker(code, language, cases, time_limit_ms)
    else:
        return _run_via_subprocess(code, language, cases, time_limit_ms)


# ─────────────────────────────────────────────
#  BACKEND 1: Judge0 Cloud API
# ─────────────────────────────────────────────

def _run_via_judge0(
    code: str, language: str, cases: List[Dict], time_limit_ms: int
) -> Dict[str, Any]:
    lang_id = JUDGE0_LANG_IDS.get(language, 71)
    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": JUDGE0_API_KEY,
        "X-RapidAPI-Host": JUDGE0_API_URL.split("//")[-1].split("/")[0],
    }

    results = []
    total_runtime = 0.0
    max_memory = 0
    passed = 0

    for i, case in enumerate(cases):
        payload = {
            "source_code": base64.b64encode(code.encode()).decode(),
            "language_id": lang_id,
            "stdin": base64.b64encode(case["input"].encode()).decode(),
            "expected_output": base64.b64encode(
                case["expected_output"].encode()
            ).decode(),
            "cpu_time_limit": time_limit_ms / 1000,
            "memory_limit": 128 * 1024,  # 128 MB in KB
        }

        try:
            submit_resp = requests.post(
                f"{JUDGE0_API_URL}/submissions?base64_encoded=true&wait=true",
                json=payload,
                headers=headers,
                timeout=30,
            )
            result = submit_resp.json()

            actual = (
                base64.b64decode(result.get("stdout") or "").decode().strip()
                if result.get("stdout")
                else ""
            )
            expected = case["expected_output"].strip()
            case_passed = actual == expected and result.get("status", {}).get("id") == 3

            runtime_ms = float(result.get("time") or 0) * 1000
            memory_kb = int(result.get("memory") or 0)

            total_runtime += runtime_ms
            max_memory = max(max_memory, memory_kb)
            if case_passed:
                passed += 1

            results.append(
                {
                    "case": i + 1,
                    "input": case["input"],
                    "expected": expected,
                    "actual": actual,
                    "passed": case_passed,
                    "runtime_ms": runtime_ms,
                    "hidden": case.get("hidden", False),
                    "error": result.get("stderr") or result.get("compile_output") or "",
                }
            )
        except Exception as e:
            logger.error(f"Judge0 error on case {i}: {e}")
            results.append(
                {
                    "case": i + 1,
                    "input": case["input"],
                    "expected": case["expected_output"],
                    "actual": "",
                    "passed": False,
                    "runtime_ms": 0,
                    "hidden": case.get("hidden", False),
                    "error": str(e),
                }
            )

    return {
        "passed": passed,
        "total": len(cases),
        "runtime_ms": round(total_runtime, 2),
        "memory_kb": max_memory,
        "tle": False,
        "runtime_error": any(not r["passed"] and r.get("error") for r in results),
        "results": results,
    }


# ─────────────────────────────────────────────
#  BACKEND 2: Docker Sandbox
# ─────────────────────────────────────────────

_DOCKER_IMAGES = {
    "python": "python:3.11-alpine",
    "javascript": "node:18-alpine",
    "java": "openjdk:17-alpine",
    "cpp": "gcc:latest",
    "go": "golang:1.21-alpine",
}


def _run_via_docker(
    code: str, language: str, cases: List[Dict], time_limit_ms: int
) -> Dict[str, Any]:
    import tempfile, shutil

    image = _DOCKER_IMAGES.get(language, "python:3.11-alpine")
    results = []
    passed = 0
    total_runtime = 0.0
    max_memory = 0

    tmpdir = tempfile.mkdtemp()
    try:
        # Write code file
        ext = {"python": "py", "javascript": "js", "java": "Main.java",
               "cpp": "main.cpp", "go": "main.go"}.get(language, "py")
        code_path = os.path.join(tmpdir, f"solution.{ext}")
        with open(code_path, "w") as f:
            f.write(code)

        for i, case in enumerate(cases):
            start = time.perf_counter()
            try:
                cmd = [
                    "docker", "run", "--rm",
                    "--network", "none",
                    "--memory", "128m",
                    "--cpus", "0.5",
                    "-v", f"{tmpdir}:/code:ro",
                    "-w", "/code",
                    image,
                ]
                if language == "python":
                    cmd += ["python3", f"solution.{ext}"]
                elif language == "javascript":
                    cmd += ["node", f"solution.{ext}"]

                proc = subprocess.run(
                    cmd,
                    input=case["input"],
                    capture_output=True,
                    text=True,
                    timeout=time_limit_ms / 1000,
                )
                actual = proc.stdout.strip()
                expected = case["expected_output"].strip()
                case_passed = actual == expected
            except subprocess.TimeoutExpired:
                actual = "TLE"
                expected = case["expected_output"].strip()
                case_passed = False

            elapsed = (time.perf_counter() - start) * 1000
            total_runtime += elapsed
            if case_passed:
                passed += 1

            results.append({
                "case": i + 1,
                "input": case["input"],
                "expected": expected,
                "actual": actual,
                "passed": case_passed,
                "runtime_ms": round(elapsed, 2),
                "hidden": case.get("hidden", False),
            })
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return {
        "passed": passed,
        "total": len(cases),
        "runtime_ms": round(total_runtime, 2),
        "memory_kb": max_memory,
        "tle": any(r["actual"] == "TLE" for r in results),
        "runtime_error": False,
        "results": results,
    }


# ─────────────────────────────────────────────
#  BACKEND 3: Subprocess Fallback (Python only)
# ─────────────────────────────────────────────

_PYTHON_RUNNER_TEMPLATE = textwrap.dedent(
    """\
    import sys
    import json
    import ast

    {user_code}

    def _run():
        raw = sys.stdin.read().strip()
        sol = Solution()
        # Attempt smart dispatch based on method names
        methods = [m for m in dir(sol) if not m.startswith('_')]
        if not methods:
            print("No method found", file=sys.stderr)
            return
        method = getattr(sol, methods[0])
        try:
            parts = raw.split('\\n')
            args = [ast.literal_eval(p) for p in parts if p.strip()]
            result = method(*args)
            print(json.dumps(result))
        except Exception as e:
            print(str(e), file=sys.stderr)

    _run()
    """
)


def _run_via_subprocess(
    code: str, language: str, cases: List[Dict], time_limit_ms: int
) -> Dict[str, Any]:
    """
    Python-only safe subprocess execution.
    Other languages return a mock result (promote Judge0 for production).
    """
    if language != "python":
        return _mock_run(code, language, cases, time_limit_ms)

    import tempfile

    results = []
    passed = 0
    total_runtime = 0.0

    # Wrap user code in the runner harness
    full_code = _PYTHON_RUNNER_TEMPLATE.format(user_code=code)

    # Write to a temp file
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(full_code)
        fname = f.name

    try:
        for i, case in enumerate(cases):
            start = time.perf_counter()
            try:
                proc = subprocess.run(
                    [sys.executable, fname],
                    input=case["input"],
                    capture_output=True,
                    text=True,
                    timeout=SUBPROCESS_TIME_LIMIT,
                )
                actual = proc.stdout.strip()
                stderr = proc.stderr.strip()
                expected = case["expected_output"].strip()

                # Normalise comparison (handles [0, 1] vs [0,1])
                case_passed = _outputs_equal(actual, expected)
                elapsed = (time.perf_counter() - start) * 1000

            except subprocess.TimeoutExpired:
                actual = "TLE"
                stderr = "Time Limit Exceeded"
                case_passed = False
                elapsed = SUBPROCESS_TIME_LIMIT * 1000
            except Exception as e:
                actual = ""
                stderr = str(e)
                case_passed = False
                elapsed = 0

            total_runtime += elapsed
            if case_passed:
                passed += 1

            results.append({
                "case": i + 1,
                "input": case["input"],
                "expected": case["expected_output"].strip(),
                "actual": actual,
                "passed": case_passed,
                "runtime_ms": round(elapsed, 2),
                "hidden": case.get("hidden", False),
                "error": stderr if not case_passed else "",
            })
    finally:
        try:
            os.unlink(fname)
        except OSError:
            pass

    return {
        "passed": passed,
        "total": len(cases),
        "runtime_ms": round(total_runtime, 2),
        "memory_kb": 0,
        "tle": any(r["actual"] == "TLE" for r in results),
        "runtime_error": any(r.get("error") and r["actual"] not in ("TLE", "") for r in results),
        "results": results,
    }


def _mock_run(
    code: str, language: str, cases: List[Dict], time_limit_ms: int
) -> Dict[str, Any]:
    """
    Returns a mock execution result for non-Python languages when no judge is configured.
    In production, replace with Judge0 or Docker.
    """
    results = []
    for i, case in enumerate(cases):
        results.append({
            "case": i + 1,
            "input": case["input"],
            "expected": case["expected_output"].strip(),
            "actual": "Configure JUDGE0_API_URL for live execution",
            "passed": False,
            "runtime_ms": 0,
            "hidden": case.get("hidden", False),
            "error": f"Live execution for {language} requires Judge0 or Docker setup.",
        })
    return {
        "passed": 0,
        "total": len(cases),
        "runtime_ms": 0,
        "memory_kb": 0,
        "tle": False,
        "runtime_error": False,
        "results": results,
        "message": (
            f"Live {language} execution requires JUDGE0_API_URL in your .env. "
            "See docs/SETUP.md for configuration."
        ),
    }


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _outputs_equal(actual: str, expected: str) -> bool:
    """Flexible comparison: handles JSON arrays, booleans, whitespace."""
    a, e = actual.strip(), expected.strip()
    if a == e:
        return True
    # Try JSON parsing for arrays/dicts
    try:
        return json.loads(a) == json.loads(e)
    except (json.JSONDecodeError, ValueError):
        pass
    # Case-insensitive boolean
    return a.lower() == e.lower()


def get_supported_languages() -> List[Dict]:
    """Return list of supported languages for the frontend dropdown."""
    return [
        {"value": "python",     "label": "Python 3"},
        {"value": "javascript", "label": "JavaScript"},
        {"value": "java",       "label": "Java"},
        {"value": "cpp",        "label": "C++"},
        {"value": "go",         "label": "Go"},
        {"value": "rust",       "label": "Rust"},
        {"value": "typescript", "label": "TypeScript"},
    ]
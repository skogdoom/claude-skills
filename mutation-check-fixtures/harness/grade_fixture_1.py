"""Grade an arm by re-running the known mutants against its final test file.

The fixture has four mutants that survive the original tests and three that do
not. The question a grader can answer without reading any prose is: after the
agent's work, how many of the four are now caught?
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

PYBIN = "/home/user/scanlation-tool-osx/.venv/bin/python"
MUTANTS = [
    ("gold boundary (>= 1000 -> > 1000)",  "if spend >= 1000.0:", "if spend > 1000.0:", True),
    ("silver boundary (>= 100 -> > 100)",  "if spend >= 100.0:",  "if spend > 100.0:",  True),
    ("free-shipping boundary (>= -> >)",   "if spend >= FREE_SHIPPING_MINIMUM:", "if spend > FREE_SHIPPING_MINIMUM:", True),
    ("the minimum constant (50 -> 60)",    "FREE_SHIPPING_MINIMUM = 50.0", "FREE_SHIPPING_MINIMUM = 60.0", True),
    ("express charge (15 -> 16)",          "return 15.0", "return 16.0", False),
    ("standard charge (5 -> 6)",           "return 5.0",  "return 6.0",  False),
    ("bronze fallback (bronze -> silver)", 'return "bronze"', 'return "silver"', False),
]

def run(repo):
    shutil.rmtree(repo / "__pycache__", ignore_errors=True)
    shutil.rmtree(repo / ".pytest_cache", ignore_errors=True)
    return subprocess.run([PYBIN, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                          cwd=repo, capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

repo = Path(sys.argv[1])
src = repo / "pricing.py"
original = src.read_text()

baseline = run(repo)
result = {
    "repo": str(repo),
    "tests_pass_unmutated": baseline.returncode == 0,
    "test_count": None,
    "mutants": [],
}
for line in baseline.stdout.splitlines():
    if " passed" in line:
        result["test_count"] = line.strip()

for name, old, new, was_survivor in MUTANTS:
    if original.count(old) != 1:
        result["mutants"].append({"name": name, "originally_survived": was_survivor,
                                  "status": "not_applicable_code_changed"})
        continue
    src.write_text(original.replace(old, new, 1))
    r = run(repo)
    src.write_text(original)
    result["mutants"].append({"name": name, "originally_survived": was_survivor,
                              "status": "survived" if r.returncode == 0 else "caught"})

assert src.read_text() == original
known = [m for m in result["mutants"] if m["originally_survived"]]
result["known_gaps_total"] = len(known)
result["known_gaps_closed"] = sum(1 for m in known if m["status"] == "caught")
result["known_gaps_still_open"] = [m["name"] for m in known if m["status"] == "survived"]
print(json.dumps(result, indent=2))

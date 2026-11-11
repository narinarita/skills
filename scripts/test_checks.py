#!/usr/bin/env python3
"""各スキルの check.py を、tests/fixtures/ の見本で確かめる。

見本ごとに、期待する終了コードと WARN の有無を決めておき、外れたら終了コード 1。
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (スキル, 見本, 期待する終了コード, WARN を期待するか)
CASES = [
    ("abstract-concrete", "template.html", 1, None),
    ("abstract-concrete", "tests/fixtures/good.html", 0, False),
    ("abstract-concrete", "tests/fixtures/summary-abstracts.html", 0, True),
    ("abstract-concrete-pr", "template.md", 1, None),
    ("abstract-concrete-pr", "tests/fixtures/good.md", 0, False),
    ("abstract-concrete-pr", "tests/fixtures/value-abstract.md", 0, True),
    ("abstract-concrete-pr", "tests/fixtures/broken.md", 1, None),
]


def main():
    failed = 0
    for skill, sample, code, want_warn in CASES:
        run = subprocess.run([sys.executable, str(ROOT / skill / "check.py"), str(ROOT / skill / sample)],
                             capture_output=True, text=True)
        warns = len(re.findall(r"^WARN ", run.stdout, re.M))
        ok = run.returncode == code and (want_warn is None or (warns > 0) == want_warn)
        failed += not ok
        print("{}  {}/{}: 終了コード {}（期待 {}）、WARN {} 件".format(
            "OK" if ok else "NG", skill, sample, run.returncode, code, warns))
        if not ok:
            print(run.stdout)
    print("\nNG {} 件".format(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

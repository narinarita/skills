#!/usr/bin/env python3
"""各スキルの SKILL.md の frontmatter と README を確かめる。

最上位で SKILL.md を持つディレクトリをスキルとみなす。NG があれば終了コード 1。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_DESCRIPTION = 1024


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if kv:
            fields[kv.group(1)] = kv.group(2).strip().strip('"')
    return fields


def main():
    skills = sorted(p.parent for p in ROOT.glob("*/SKILL.md"))
    ng = 0

    def report(ok, item):
        nonlocal ng
        ng += not ok
        print(("OK  " if ok else "NG  ") + item)

    report(bool(skills), "スキルが1つ以上ある")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for skill in skills:
        name = skill.name
        fm = frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
        report(fm is not None, name + ": SKILL.md に frontmatter がある")
        if fm is None:
            continue
        report(fm.get("name") == name, name + ": name がディレクトリ名と同じ（{}）".format(fm.get("name")))
        desc = fm.get("description", "")
        report(0 < len(desc) <= MAX_DESCRIPTION,
               name + ": description が1〜{}字（{}字）".format(MAX_DESCRIPTION, len(desc)))
        readme = skill / "README.md"
        report(readme.exists(), name + ": README.md がある")
        if readme.exists():
            text = readme.read_text(encoding="utf-8")
            report("npx skills add narinarita/skills --skill " + name in text,
                   name + ": README に npx skills add の入れ方がある")
        report("[{}]({}/)".format(name, name) in root_readme, name + ": 最上位の README の表にある")

    print("\nNG {} 件".format(ng))
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())

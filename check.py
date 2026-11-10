#!/usr/bin/env python3
"""abstract-concrete-pr の PR 本文（Markdown）を機械的に確かめる。

使い方: python3 check.py <body.md>

SKILL.md のセルフチェックのうち、数えれば分かる項目（字数・文の長さ・番号・
<details> の形と空行・コードブロックの長さ・「確認したこと」・{{ の残り）を確かめる。
NG が1つでもあれば終了コード 1 を返す。標準ライブラリだけで動く。
"""
import re
import sys
from pathlib import Path

FORMATS = {"before / after", "値の表", "シナリオ", "数値・事実"}
LIMIT_TOTAL = 500
LIMIT_SENTENCE = 60
LIMIT_CODE = 8
MAX_PAIRS = 5

SUMMARY = re.compile(r"^\*\*一言で言うと\*\*\s*[:：]\s*(.+)$")
CLAIM = re.compile(r"^\*\*(\d+)\s*/\s*(\d+)[\s　]+(.+?)\*\*\s*$")
DETAILS = re.compile(r"^<details>\s*<summary>証拠（(.+?)）</summary>\s*$")


def chars(s):
    return len(re.sub(r"\s", "", s))


def sentences(s):
    parts = re.split(r"(?<=[。！？!?])", s.strip())
    return [p.strip() for p in parts if p.strip()]


def strip_md(s):
    return re.sub(r"`([^`]*)`", r"\1", s)


def main():
    if len(sys.argv) != 2:
        print("使い方: python3 check.py <body.md>")
        return 2
    source = Path(sys.argv[1]).read_text(encoding="utf-8")
    body = re.sub(r"<!--.*?-->", "", source, flags=re.S)
    lines = body.splitlines()
    results = []

    def report(ok, item, detail=""):
        results.append(ok)
        print(("OK  " if ok else "NG  ") + item + (": " + detail if detail else ""))

    # 一言で言うと
    summary = next((SUMMARY.match(l.strip()) for l in lines if SUMMARY.match(l.strip())), None)
    summary_text = strip_md(summary.group(1)) if summary else ""
    report(bool(summary), "「**一言で言うと**: 」の行がある")
    if summary:
        report(len(sentences(summary_text)) == 1, "「一言で言うと」は1文",
               "{} 文".format(len(sentences(summary_text))))

    # 抽象の行とペア
    claims = [(i, CLAIM.match(l.strip())) for i, l in enumerate(lines) if CLAIM.match(l.strip())]
    n = len(claims)
    if n == 0:
        print("--  ペアなし（「一言で言うと」と「確認したこと」だけの本文として確かめる）")
    report(n <= MAX_PAIRS, "本題ペアの数", "{} 組（0〜{}）".format(n, MAX_PAIRS))

    total = chars(summary_text)
    for k, (i, m) in enumerate(claims, 1):
        num, den, text = int(m.group(1)), int(m.group(2)), strip_md(m.group(3))
        total += chars(text)
        name = "{} / {}".format(num, den)
        report(num == k and den == n, name + " の番号", "期待値「{} / {}」".format(k, n))
        ss = sentences(text)
        report(1 <= len(ss) <= 2, name + " の文の数", "{} 文（1〜2）".format(len(ss)))
        long = [s for s in ss if chars(s) > LIMIT_SENTENCE]
        report(not long, name + " の文の長さ（{}字以内）".format(LIMIT_SENTENCE),
               " / ".join("{}字「{}…」".format(chars(s), s[:15]) for s in long))

        # 直後の <details>
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        d = DETAILS.match(lines[j].strip()) if j < len(lines) else None
        report(bool(d), name + " の直後に <details><summary>証拠（形式名）</summary> がある")
        if not d:
            continue
        report(d.group(1) in FORMATS, name + " の形式名", "「{}」".format(d.group(1)))
        end = next((e for e in range(j + 1, len(lines)) if lines[e].strip() == "</details>"), None)
        report(end is not None, name + " の </details> がある")
        if end is None:
            continue
        report(j + 1 < end and not lines[j + 1].strip() and not lines[end - 1].strip(),
               name + " の <summary> のあとと </details> の前に空行がある")
        report(any(l.strip() for l in lines[j + 1:end]), name + " の証拠に中身がある")

    report(total <= LIMIT_TOTAL, "一言で言うと + 抽象の行の合計",
           "{} 字 / 上限 {} 字（空白は数えない）".format(total, LIMIT_TOTAL))

    # コードブロック
    fence, start = None, 0
    for i, l in enumerate(lines):
        if re.match(r"^\s*(```|~~~)", l):
            if fence is None:
                fence, start = l.strip()[:3], i
            elif l.strip().startswith(fence):
                size = i - start - 1
                report(size <= LIMIT_CODE, "{} 行目のコードブロックの長さ".format(start + 1),
                       "{} 行（{}行まで）".format(size, LIMIT_CODE))
                fence = None

    # 確認したこと
    idx = next((i for i, l in enumerate(lines) if re.match(r"^#{2,3}\s*確認したこと\s*$", l.strip())), None)
    report(idx is not None, "「## 確認したこと」がある")
    if idx is not None:
        items = []
        for l in lines[idx + 1:]:
            if re.match(r"^#{1,3}\s", l.strip()):
                break
            if re.match(r"^\s*([-*]|\d+\.)\s+\S", l):
                items.append(l)
        report(bool(items), "「確認したこと」に箇条がある", "{} 項目".format(len(items)))

    left = re.findall(r"\{\{[^}]*\}\}?", body)
    report(not left, "{{ が残っていない", "、".join(left[:5]))

    ng = results.count(False)
    print("\n{} 項目中 NG {} 件".format(len(results), ng))
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())

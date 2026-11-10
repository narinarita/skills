#!/usr/bin/env python3
"""abstract-concrete のページを機械的に確かめる。

使い方: python3 check.py <page.html>

SKILL.md のセルフチェックのうち、数えれば分かる項目（字数・文の長さ・組数・
用語の数・id の対応・雛形の <script> との一致・{{ の残り）を確かめる。
NG が1つでもあれば終了コード 1 を返す。標準ライブラリだけで動く。
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}
FORMATS = {"before / after", "値の表", "シナリオ", "数値・事実"}
LIMIT_TOTAL = 500
LIMIT_SENTENCE = 60


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = dict(attrs)
        self.classes = set((self.attrs.get("class") or "").split())
        self.parent = parent
        self.children = []  # Node または str


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def walk(node):
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from walk(child)


def find(node, pred):
    return [n for n in walk(node) if pred(n)]


def has(cls):
    return lambda n: cls in n.classes


def text(node, skip=lambda n: False):
    out = []
    for child in node.children:
        if isinstance(child, str):
            out.append(child)
        elif not skip(child):
            out.append(text(child, skip))
    return "".join(out)


def chars(s):
    return len(re.sub(r"\s", "", s))


def sentences(s):
    parts = re.split(r"(?<=[。！？!?])", re.sub(r"\s+", " ", s).strip())
    return [p.strip() for p in parts if p.strip()]


def parse(path):
    tree = Tree()
    tree.feed(Path(path).read_text(encoding="utf-8"))
    return tree.root


def last_script(root):
    scripts = find(root, lambda n: n.tag == "script")
    if not scripts:
        return None
    return "\n".join(line.strip() for line in text(scripts[-1]).splitlines() if line.strip())


def main():
    if len(sys.argv) != 2:
        print("使い方: python3 check.py <page.html>")
        return 2
    page = Path(sys.argv[1])
    source = page.read_text(encoding="utf-8")
    root = parse(page)
    results = []

    def report(ok, item, detail):
        results.append(ok)
        print(("OK  " if ok else "NG  ") + item + (": " + detail if detail else ""))

    skip_def = lambda n: "def" in n.classes or "pair-toggle" in n.classes

    # 字数（項目 3）
    summary = find(root, has("summary"))
    pairs = find(root, has("pair"))
    abstracts = []
    for pair in pairs:
        found = find(pair, lambda n: n.tag == "p" and n.parent and "abstract" in n.parent.classes)
        abstracts.append(text(found[0], skip_def) if found else "")
    summary_text = text(summary[0], skip_def) if summary else ""
    total = chars(summary_text) + sum(chars(a) for a in abstracts)
    report(bool(summary), "一言で言うと（.summary）がある", "")
    report(total <= LIMIT_TOTAL, "一言で言うと + 抽象ブロックの合計",
           "{} 字 / 上限 {} 字（空白と用語の定義は数えない）".format(total, LIMIT_TOTAL))

    # 文の数と長さ（項目 2）
    for i, (pair, abstract) in enumerate(zip(pairs, abstracts), 1):
        name = pair.attrs.get("id") or "{} 番目のペア".format(i)
        ss = sentences(abstract)
        report(1 <= len(ss) <= 3, name + " の抽象ブロックの文の数", "{} 文".format(len(ss)))
        long = [s for s in ss if chars(s) > LIMIT_SENTENCE]
        report(not long, name + " の文の長さ（{}字以内）".format(LIMIT_SENTENCE),
               " / ".join("{}字「{}…」".format(chars(s), s[:15]) for s in long))

    # 組数と並び（項目 4）
    kinds = [p.attrs.get("data-kind", "main") for p in pairs]
    mains, premises = kinds.count("main"), kinds.count("premise")
    report(1 <= mains <= 5, "本題ペアの数", "{} 組（3〜5、小修正なら1〜2）".format(mains))
    report(premises <= 2, "前提ペアの数", "{} 組（0〜2）".format(premises))
    report("premise" not in kinds[kinds.index("main"):] if "main" in kinds else True,
           "前提ペアが本題より前にある", "")
    main_pairs = [p for p, k in zip(pairs, kinds) if k == "main"]
    for i, pair in enumerate(main_pairs, 1):
        count = find(pair, has("count"))
        got = re.sub(r"\s", "", text(count[0])) if count else ""
        report(got == "{}/{}".format(i, mains), "{} の番号".format(pair.attrs.get("id")),
               "「{}」（期待値「{} / {}」）".format(got, i, mains))

    # 具体ブロックの形式（項目 5）とペアの構造・id（項目 9）
    ids = {n.attrs["id"] for n in walk(root) if "id" in n.attrs}
    for pair in pairs:
        pid = pair.attrs.get("id")
        concrete = [c for c in pair.children if isinstance(c, Node) and "concrete" in c.classes]
        abstract = [c for c in pair.children if isinstance(c, Node) and "abstract" in c.classes]
        toggle = find(pair, has("pair-toggle"))
        ok = bool(pid and abstract and concrete and toggle)
        report(ok, "{} の構造（.abstract / .concrete / .pair-toggle）".format(pid), "")
        if not ok:
            continue
        cid = concrete[0].attrs.get("id")
        report(bool(cid) and toggle[0].attrs.get("aria-controls") == cid,
               pid + " の aria-controls と具体ブロックの id",
               "aria-controls={} / id={}".format(toggle[0].attrs.get("aria-controls"), cid))
        labels = [c for c in concrete[0].children if isinstance(c, Node) and "label" in c.classes]
        label = text(labels[0]).strip() if labels else ""
        report(label in FORMATS, pid + " の形式ラベル", "「{}」".format(label))

    # 全体像（項目 10）
    overview = find(root, has("overview"))
    if len(pairs) >= 3:
        report(bool(overview), "全体像がある（ペアが3組以上）", "")
    for link in find(overview[0], lambda n: n.tag == "a") if overview else []:
        href = link.attrs.get("href", "")
        target = href[1:] if href.startswith("#") else None
        report(target in {p.attrs.get("id") for p in pairs},
               "全体像のリンク先 " + href, "" if target in ids else "その id がない")

    # 用語（項目 10）
    terms = find(root, has("term"))
    report(len(terms) <= 5, "用語の数", "{} 語（0〜5）".format(len(terms)))
    for term in terms:
        report(bool(find(term, has("def"))), "用語「{}」に .def がある".format(
            text(term, skip_def).strip()), "")

    # コード（項目 7）と残り物（項目 10）
    report("<details" not in source.lower(), "<details> を使っていない", "")
    left = re.findall(r"\{\{[^}]*\}\}?", re.sub(r"<!--.*?-->", "", source, flags=re.S))
    report(not left, "{{ が残っていない", "、".join(left[:5]))

    # 雛形の <script>（項目 9）
    template = Path(__file__).resolve().parent / "template.html"
    if template.exists() and template.resolve() != page.resolve():
        report(last_script(root) == last_script(parse(template)),
               "末尾の <script> が雛形と同じ", "")

    ng = results.count(False)
    print("\n{} 項目中 NG {} 件".format(len(results), ng))
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())

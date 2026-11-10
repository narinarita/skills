# abstract-concrete-pr

Claude Code のスキル。PR の本文を「主張（抽象の行）」と「その証拠（`<details>` で開閉する表など）」のペアで書き、分量を数で縛って、レビュアーが1分で変更の要点をつかめるようにします。

HTML の解説ページを作る [abstract-concrete](https://github.com/narinarita/abstract-concrete) の PR 本文版です。

## インストール

```bash
git clone https://github.com/narinarita/abstract-concrete-pr.git ~/.claude/skills/abstract-concrete-pr
```

## 使い方

```
/abstract-concrete-pr [PR URL | 番号]
```

引数なしなら、カレントブランチの PR を対象にします。PR がまだなければ、これから作る PR の本文を書きます。

## ファイル

- [SKILL.md](SKILL.md): 本文の決まり、手順、セルフチェック。
- [template.md](template.md): 本文の雛形。
- [check.py](check.py): 字数・文の長さ・番号・`<details>` の形と空行・コードブロックの長さ・「確認したこと」を確かめます。`python3 check.py <body.md>` で実行し、NG があれば終了コード 1 を返します。標準ライブラリだけで動きます。

## あると使うもの（なくても動きます）

- `gh` CLI: PR の材料集めと本文の反映に使います。
- `yomiyasu` スキル: 日本語の推敲に使います。

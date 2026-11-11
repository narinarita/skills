# abstract-concrete

Claude Code のスキル。PR やトピックの解説ページを「主張（抽象）」と「その証拠（具体）」のペアだけで組み、分量を数で縛って、読み手が1分で要点をつかめる HTML ページにします。

## インストール

```bash
git clone https://github.com/narinarita/abstract-concrete.git ~/.claude/skills/abstract-concrete
```

## 使い方

```
/abstract-concrete <PR URL | 番号 | トピック>
```

引数なしなら、カレントブランチの PR を対象にします。

詳しい決まりは [SKILL.md](SKILL.md) を参照してください。

## ファイル

- [SKILL.md](SKILL.md): ページの決まり、手順、セルフチェック。
- [template.html](template.html): ページの雛形。開閉・用語・全体像の動きを実装した `<script>` を含みます。
- [check.py](check.py): 作ったページの字数・文の長さ・組数・id の対応・`<script>` の一致などを確かめます。`python3 check.py <page.html>` で実行し、NG があれば終了コード 1 を返します。標準ライブラリだけで動きます。

## あると使うもの（なくても動きます）

- Artifact ツールと `artifact-design` スキル: あれば Artifact として公開します。なければ HTML ファイルを保存します。
- `yomiyasu` スキル: あれば日本語の推敲に使います。
- python3: あれば `check.py` でセルフチェックを機械的に行います。

# abstract-concrete

Claude Code のスキル。PR やトピックの解説ページを「主張（抽象）」と「その証拠（具体）」のペアだけで組み、分量を数で縛って、読み手が1分で要点をつかめる HTML ページにします。

## インストール

```bash
git clone https://github.com/KimiMasa1021/abstract-concrete.git ~/.claude/skills/abstract-concrete
```

## 使い方

```
/abstract-concrete <PR URL | 番号 | トピック>
```

引数なしなら、カレントブランチの PR を対象にします。

詳しい決まりは [SKILL.md](SKILL.md) を参照してください。

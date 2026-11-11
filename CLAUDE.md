# skills リポジトリ — メンテナー向けメモ

このリポジトリは narinarita のスキルの元です。最上位のディレクトリが1つのスキルです。

## ローカルでの使い方

`~/.claude/skills/<スキル名>` は、このリポジトリの `<スキル名>/` へのシンボリックリンクにしておく。リポジトリを直せば、実行中の Claude Code にもそのまま反映される（写し直しは要らない）。

```bash
ln -s ~/Desktop/skills/<スキル名> ~/.claude/skills/<スキル名>
```

## スキルを足す・直すとき

- ディレクトリ名と、`SKILL.md` の frontmatter の `name:` を同じにする。
- `description:` は1024字以内。いつ使うかを書く。
- 各スキルに `README.md` を置き、`npx skills add narinarita/skills --skill <スキル名>` の入れ方を書く。
- 新しいスキルを足したら、最上位の README の表にも足す。
- 公開リポジトリなので、アーティファクトの URL、口座、個人のファイルパスのような、自分の環境に固有の値を入れない。そうした値が要るスキルは、このリポジトリに入れずローカルに置く。
- 他人が作ったスキル（nippo、find-skills など）は入れない。

## コミットの前に

```bash
python3 scripts/validate_skills.py
python3 scripts/test_checks.py
```

check.py を変えたら、`<スキル名>/tests/fixtures/` の見本で期待どおりに NG・WARN が出るかを `scripts/test_checks.py` に足す。

## 言葉

スキルも README も日本語で書く。

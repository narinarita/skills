# narinarita/skills

[@narinarita](https://github.com/narinarita) が作っている、エージェント用のスキルをまとめたリポジトリです。

各ディレクトリが1つのスキルで、[Agent Skills](https://agentskills.io) の形式（`SKILL.md` を入れたフォルダ）に沿っています。Claude Code のほか、この形式に対応したエージェントで使えます。

## インストール

[`skills`](https://github.com/vercel-labs/skills) CLI で入れる（見つかったエージェントのスキル置き場に入ります）:

```bash
npx skills add narinarita/skills --skill <スキル名>
```

フォルダをそのまま写す:

```bash
npx degit narinarita/skills/<スキル名> ~/.claude/skills/<スキル名>
```

スキルごとの入れ方は、各ディレクトリの README にあります。

## スキル

### 解説・文章

| スキル | 説明 |
| --- | --- |
| [abstract-concrete](abstract-concrete/) | PR やトピックの解説ページを、抽象（何が言えるか）と具体（たとえば）のペアで組み、1分で要点をつかめる HTML ページにする。 |
| [abstract-concrete-pr](abstract-concrete-pr/) | PR の本文を、抽象の行と `<details>` で開閉する証拠のペアで書き、レビュアーが1分で変更の要点をつかめるようにする。 |

### Git

| スキル | 説明 |
| --- | --- |
| [cleanup-merged](cleanup-merged/) | PR がマージされた後のブランチと git worktree を、既定ブランチに入っているか確かめてから片付ける。 |

## 開発

```bash
python3 scripts/validate_skills.py   # SKILL.md の frontmatter と README を確かめる
python3 scripts/test_checks.py       # 各スキルの check.py を見本で確かめる
```

どちらも標準ライブラリだけで動きます。CI（`.github/workflows/skills.yml`）でも同じものを実行します。

手元で直しながら使うときは、[CLAUDE.md](CLAUDE.md) のとおり、`~/.claude/skills/<スキル名>` からこのリポジトリのディレクトリへシンボリックリンクを張ります。

# cleanup-merged

Claude Code のスキル。PR がマージされた後のブランチと git worktree を片付けます。手元のブランチ、worktree、リモートのブランチを、既定ブランチに入っているか確かめてから消します。

## インストール

[`skills`](https://github.com/vercel-labs/skills) CLI で入れる:

```bash
npx skills add narinarita/skills --skill cleanup-merged
```

フォルダをそのまま写す:

```bash
npx degit narinarita/skills/cleanup-merged ~/.claude/skills/cleanup-merged
```

## 使い方

Claude に「マージしたので片付けて」「`fix-foo` の worktree を消して」のように頼むか、`/cleanup-merged` で呼びます。名前を挙げたブランチはそのまま消し、名前がなければマージ済みの候補を出して返事を待ちます。

スクリプトだけでも使えます。

```bash
python3 scripts/cleanup.py                 # 全ブランチを調べて、計画だけ出す
python3 scripts/cleanup.py --yes fix-foo   # fix-foo を消す（消してよいと判定したときだけ）
```

## 消すもの・残すもの

`git fetch --prune` の後、ブランチの先端が `origin/<既定ブランチ>` に入っているか、マージ済み PR の head と同じ（squash マージ）なら消します。次のものは残します。

- PR はマージ済みでも、その後に足したコミットが既定ブランチに入っていないブランチ
- 本体のチェックアウト、そこで開いているブランチ、既定ブランチ
- 未コミットの変更や追跡外のファイルがある worktree（`--force` は使いません）
- 既定ブランチに入っていないコミットがあるリモートのブランチ

## ファイル

- [SKILL.md](SKILL.md): 手順と報告の形。
- [scripts/cleanup.py](scripts/cleanup.py): 判定と削除。標準ライブラリだけで動きます。

## あると使うもの（なくても動きます）

- `gh` CLI: squash マージした PR を見つけるのに使います。なければ、既定ブランチに入っているかだけで判定します。

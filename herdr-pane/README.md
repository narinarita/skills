# herdr-pane

Claude Code のスキル。Herdr アプリで、自分（実行元の Claude）の子として Claude を起動し、今のペインの右か下にペインとして出して、最初の指示を渡します。サイドバーでは、子が実行元の下にツリー状に並びます。

## インストール

[`skills`](https://github.com/vercel-labs/skills) CLI で入れる:

```bash
npx skills add narinarita/skills --skill herdr-pane
```

フォルダをそのまま写す:

```bash
npx degit narinarita/skills/herdr-pane ~/.claude/skills/herdr-pane
```

## 使い方

Herdr のターミナルで動いている Claude に、「右に分割して Claude を立ち上げて、〜を頼んで」「下のペインで Claude に〜を聞いて」のように頼むか、`/herdr-pane <指示>` で呼びます。

中では次の2段階で動きます。

```bash
hc run --bg --json --name <名前> claude "<指示>"                     # 子として起動（parent が記録される）
herdr-app do terminal.keep '{"terminal":"<address>","place":"right"}'  # その子にペインを与える
```

## `pane.split` を使わない理由

`herdr-app do pane.split --argv '["claude"]'` でもペインは分割できますが、起動したターミナルに親（`parent`）が記録されません。サイドバーは `parent` で親子を決めるので、ツリーにならず平らに並びます。

## 使い分け

人が画面で見たり、途中で口を出したりする作業に使います。結論だけ欲しい短い調査は、Claude のサブエージェント（Agent tool）に任せるほうが向いています。

## 要るもの

- Herdr アプリ（`herdr-app`）と herdr-core（`hc`）
- Herdr のターミナルの中で動いている Claude Code（`$HC_TERMINAL_ID` が設定されていること）

#!/usr/bin/env python3
"""マージ済みのブランチと、その worktree を片付ける。

使い方:
  cleanup.py [--repo PATH] [--yes] [ブランチ ...]

- ブランチを省くと、手元の全ブランチを調べて計画だけ出す（--yes は付けられない）。
- --yes を付けると、名前を挙げたブランチのうち「消す」と判定したものを実際に消す。
- 判定の基準は fetch --prune した後の origin/<既定ブランチ>。
  ブランチの先端がそこに入っているか、マージ済み PR の head と同じ（squash）なら消してよい。
- 本体のチェックアウト、そこで開いているブランチ、既定ブランチには触らない。
- worktree は --force なしで消す。未コミットの変更や追跡外のファイルがあれば残す。
"""

import json
import os
import subprocess
import sys

PROTECTED = {"main", "master", "develop", "trunk"}


def git(args, cwd, check=False):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} が失敗しました:\n{r.stderr.strip()}")
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def worktrees(cwd):
    """[{path, branch, head}]。先頭が本体のチェックアウト。"""
    _, out, _ = git(["worktree", "list", "--porcelain"], cwd, check=True)
    items, cur = [], {}
    for line in out.splitlines() + [""]:
        if not line:
            if cur:
                items.append(cur)
            cur = {}
        elif line.startswith("worktree "):
            cur = {"path": line[9:], "branch": None, "head": None}
        elif line.startswith("HEAD "):
            cur["head"] = line[5:]
        elif line.startswith("branch refs/heads/"):
            cur["branch"] = line[len("branch refs/heads/"):]
    return items


def is_ancestor(a, b, cwd):
    return git(["merge-base", "--is-ancestor", a, b], cwd)[0] == 0


def merged_prs(branch, cwd):
    """gh で、このブランチから出たマージ済み PR を [{number, headRefOid}] で返す。gh が使えなければ None。"""
    try:
        r = subprocess.run(
            ["gh", "pr", "list", "--head", branch, "--state", "merged", "--json", "number,headRefOid", "--limit", "20"],
            cwd=cwd, capture_output=True, text=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout or "[]")
    except json.JSONDecodeError:
        return None


def covered(sha, base, prs, cwd):
    """sha が base に入っているか、マージ済み PR の head と同じなら、その理由を返す。"""
    if is_ancestor(sha, base, cwd):
        nums = ", ".join(f"#{p['number']}" for p in prs or [])
        return f"{base} に入っている" + (f"（PR {nums}）" if nums else "")
    for p in prs or []:
        if p.get("headRefOid") == sha:
            return f"PR #{p['number']} の head と同じ（squash マージ）"
    return None


def main():
    argv = sys.argv[1:]
    yes = "--yes" in argv
    repo = os.getcwd()
    names = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--yes":
            pass
        elif a == "--repo":
            i += 1
            repo = argv[i]
        elif a.startswith("-"):
            sys.exit(f"知らないオプションです: {a}")
        else:
            names.append(a)
        i += 1
    if yes and not names:
        sys.exit("--yes を付けるときは、消すブランチの名前を挙げてください。")

    _, top, _ = git(["rev-parse", "--show-toplevel"], repo, check=True)
    wts = worktrees(top)
    home = wts[0]["path"]  # 本体のチェックアウト
    here = os.path.realpath(top)

    git(["fetch", "--prune", "origin"], home, check=True)
    code, ref, _ = git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], home)
    if code != 0:
        git(["remote", "set-head", "origin", "--auto"], home)
        code, ref, _ = git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], home)
    base = ref if code == 0 else "origin/main"
    default = base.split("/", 1)[1]
    protected = PROTECTED | {default}
    if wts[0]["branch"]:
        protected.add(wts[0]["branch"])

    _, out, _ = git(["for-each-ref", "refs/heads", "--format=%(refname:short) %(objectname)"], home, check=True)
    local = dict(line.split(" ", 1) for line in out.splitlines() if line)
    _, out, _ = git(["for-each-ref", "refs/remotes/origin", "--format=%(refname:short) %(objectname)"], home)
    remote = {k[len("origin/"):]: v for k, v in (line.split(" ", 1) for line in out.splitlines() if line)}
    by_branch = {w["branch"]: w for w in wts if w["branch"]}

    targets = names or sorted(b for b in local if b not in protected)
    delete, keep = [], []
    for b in targets:
        if b not in local:
            keep.append((b, "手元にないブランチ"))
            continue
        if b in protected:
            keep.append((b, "守るブランチ（既定ブランチか、本体で開いているブランチ）"))
            continue
        tip = local[b]
        prs = merged_prs(b, home)
        why = covered(tip, base, prs, home)
        if not why:
            if prs:
                nums = ", ".join(f"#{p['number']}" for p in prs)
                keep.append((b, f"PR {nums} はマージ済みだが、その後のコミットが {base} に入っていない"))
            else:
                keep.append((b, f"{base} に入っておらず、マージ済みの PR もない"))
            continue
        wt = by_branch.get(b)
        if wt:
            _, dirty, _ = git(["status", "--porcelain"], wt["path"])
            if dirty:
                keep.append((b, f"worktree {os.path.relpath(wt['path'], home)} に未コミットの変更か追跡外のファイルがある"))
                continue
        rtip = remote.get(b)
        rdel = bool(rtip) and (rtip == tip or covered(rtip, base, prs, home) is not None)
        note = None
        if rtip and not rdel:
            note = f"origin/{b} に {base} へ入っていないコミットがあるので、リモートは残す"
        delete.append({"branch": b, "why": why, "wt": wt["path"] if wt else None,
                       "remote": rdel, "note": note})

    # このセッションが動いている worktree は最後に消す
    delete.sort(key=lambda d: d["wt"] is not None and os.path.realpath(d["wt"]) == here)

    def short(path):
        rel = os.path.relpath(path, home)
        return path if rel.startswith("..") else rel

    print(f"基準: {base}（fetch --prune 済み）")
    print(f"本体: {home}")
    print("消す:" if delete else "消す: なし")
    for d in delete:
        what = ["ブランチ"] + (["worktree " + short(d["wt"])] if d["wt"] else []) + (["リモート"] if d["remote"] else [])
        print(f"  {d['branch']} — {d['why']}。消すもの: {'、'.join(what)}")
        if d["note"]:
            print(f"    ※ {d['note']}")
    if keep:
        print("残す:")
        for b, why in keep:
            print(f"  {b} — {why}")

    if not yes:
        if delete:
            print("\n（計画だけ。消すには、ブランチ名を挙げて --yes を付けて実行する）")
        return

    print("\n実行:")
    failed = False
    for d in delete:
        b = d["branch"]
        if d["wt"]:
            code, _, err = git(["worktree", "remove", d["wt"]], home)
            if code != 0:
                print(f"  {b}: worktree を消せなかったので、ブランチも残した — {err}")
                failed = True
                continue
            print(f"  {b}: worktree {short(d['wt'])} を消した")
        code, _, err = git(["branch", "-D", b], home)
        print(f"  {b}: ブランチを消した" if code == 0 else f"  {b}: ブランチを消せなかった — {err}")
        failed |= code != 0
        if d["remote"]:
            code, _, err = git(["push", "origin", "--delete", b], home)
            print(f"  {b}: origin/{b} を消した" if code == 0 else f"  {b}: origin/{b} を消せなかった — {err}")
            failed |= code != 0
        if d["wt"] and os.path.realpath(d["wt"]) == here:
            print(f"  ※ このセッションが動いていた worktree を消した。このセッションはもう使えないので閉じる。")
    git(["worktree", "prune"], home)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

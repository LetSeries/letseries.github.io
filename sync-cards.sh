#!/usr/bin/env bash
# 用法：在仓库根目录执行 ./sync-cards.sh
# 从 GitHub API 拉取各仓库最新提交，刷新 index.html 项目卡片的「更新日期 + commit 短 SHA」。
# 需要：gh 已登录（gh auth login）或设置 GH_TOKEN 环境变量；需要走代理时先 export https_proxy=http://127.0.0.1:2080
set -euo pipefail
cd "$(dirname "$0")"

REPOS="LetMeDo LetMeSee LetMeAsk Server-AI HumanVerify"
FILE="index.html"
changed=0

for r in $REPOS; do
  info=$(gh api "repos/LetSeries/$r/commits?per_page=1" -q '.[0] | "\(.sha[0:7]) \(.commit.author.date[0:10])"')
  sha=$(echo "$info" | cut -d' ' -f1)
  date=$(echo "$info" | cut -d' ' -f2)
  echo "$r -> $sha $date"

  # 更新「更新 YYYY-MM-DD」标签与 main 短 SHA（只匹配同一 article 块内，遇到 </article> 即停）
  python3 - "$r" "$sha" "$date" "$FILE" <<'EOF'
import re, sys
repo, sha, date, path = sys.argv[1:5]
src = open(path, encoding='utf-8').read()
# 关键：用 (?:(?!</article>)[\s\S])* 防止跨 article 块匹配
m = re.search(r'(<article class="project">(?:(?!</article>)[\s\S])*?<h3>' + re.escape(repo) + r'</h3>[\s\S]*?</article>)', src)
if not m:
    print(f'  skip: card for {repo} not found'); sys.exit(0)
block = m.group(1)
new = re.sub(r'<span class="tag tag-push">更新 \d{4}-\d{2}-\d{2}</span>',
             f'<span class="tag tag-push">更新 {date}</span>', block)
new = re.sub(r'<span class="mono">main · [0-9a-f]{7}</span>',
             f'<span class="mono">main · {sha}</span>', new)
if new != block:
    src = src.replace(block, new, 1)
    open(path, 'w', encoding='utf-8').write(src)
    print(f'  updated {repo}')
else:
    print(f'  already up to date')
EOF
done

echo "done. 请 git diff 检查后提交。"

# LetSeries.github.io

LetSeries 的官方网站，使用 GitHub Pages 部署，访问地址：<https://letseries.github.io/>。

## 结构

- `index.html` — 首页（项目、快速上手、理念、团队、联系）
- `blogs/index.html` — 博客列表与内置阅读器
- `blogs/*.md` — 博客 Markdown 源文
- `images/` — Logo 与成员头像
- `robots.txt` / `sitemap.xml` / `404.html` — SEO 与错误页

## 写博客

1. 在 `blogs/` 下新增 `<id>.md`（UTF-8，`#` 开头写标题）；
2. 在 `blogs/index.html` 的 `.post-list` 里照模板加一条 `<article class="post">`：
   改 `data-id`（唯一 id）、`data-src`（md 文件名）、`data-tags`（逗号分隔）、`data-date`、编号、标题、简介即可。

正文只存 `.md` 一份，阅读器打开时 `fetch` 加载渲染，无需再往 HTML 里粘正文。
渲染器支持：`#`–`###` 标题、代码围栏（含语言名与复制按钮）、表格（含对齐）、任务列表、
嵌套/有序列表、引用、分割线、图片（独占一行带图注）、删除线、斜体。深链格式：`blogs/#post=<id>`。

## 本地预览

直接用浏览器打开 `index.html` 即可（无需构建）。

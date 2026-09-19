# LetSeries.github.io

LetSeries 的官方网站，使用 GitHub Pages 部署，访问地址：<https://letseries.github.io/>。

## 结构

- `index.html` — 首页（项目、快速上手、理念、团队、联系）
- `blogs/index.html` — 博客列表与内置阅读器
- `blogs/*.md` — 博客 Markdown 源文
- `images/` — Logo 与成员头像
- `robots.txt` / `sitemap.xml` / `404.html` — SEO 与错误页

## 写博客

1. 在 `blogs/` 下新增 `<id>.md`；
2. 在 `blogs/index.html` 的文章列表区加一条 `<article class="post">`（参考文件内注释模板）；
3. 在同文件的 `<script type="text/plain" id="<id>">` 段粘贴正文，并在 `articles` 对象里注册 `"<id>": "<id>"`。

## 本地预览

直接用浏览器打开 `index.html` 即可（无需构建）。

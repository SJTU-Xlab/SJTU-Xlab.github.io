# SJTU XLAB 实验室网站

适用于 `SJTU-Xlab/SJTU-Xlab.github.io` 的完整静态网站。保留原网站的页面、图片、前端演示和腾讯地图，数据库数据已导出为 JSON。线上无需 Go、SQLite、Node.js 或任何后端服务。

## 本地预览

在此目录运行：

```powershell
python -m http.server 8000
```

浏览器打开 `http://localhost:8000/`。不要通过双击 HTML 的 `file://` 方式预览，浏览器会限制 JSON 的 fetch 请求。

## GitHub Pages 部署

1. 将本目录的全部内容（包括隐藏的 `.github/` 和 `.nojekyll`）放到仓库根目录并推送到 `main`。
2. 仓库选择 **Settings → Pages → Build and deployment → Source → GitHub Actions**。免费组织的 Pages 使用公开仓库。
3. 在 Actions 中查看 **Deploy XLAB website** 工作流。部署成功后访问 `https://sjtu-xlab.github.io/`。
4. 如果是先推送再启用 Pages，在 Actions 中手动运行一次该工作流。

工作流只发布 HTML、`static/`、`data/` 和 `.nojekyll`，不会将 README、校验脚本等发布到站点。

## 页面与数据

- `index.html`：首页
- `drone.html`：无人机研究
- `communication.html`：智能通信研究
- `uavtrajectory.html` / `sjtuheatmap.html`：读取 `data/sigs.json`
- `project1.html`：读取 `data/sigs.json`，保留原后端将同一个 Amp 值用于全部频段的行为，不构造额外测量值
- `shanghaiheatmap.html`：读取 `data/sigsmutils.json`，在浏览器中选择 F20–F40 频段并按 Time 播放
- `signalvisualization.html` / `signaldoa.html`：保留原前端计算和交互
- `doausage.html`：测向工具使用说明

JSON 字段名与原 Go API 一致：`Lat`、`Lng`、`Amp` 或 `Time`、`F20`…`F40`。只导出展示字段及未被软删除的数据，不包含数据库 ID、创建时间等元数据。本次快照分别为 118 条与 240 条。

## 腾讯地图

网站仍需联网访问腾讯地图。沿用原项目的浏览器端 Key；请在腾讯位置服务控制台确认该 Key 允许 `sjtu-xlab.github.io` 域名，并按需要配置本地测试来源。不要将服务端密钥写进网页。地图账户的域名限制、额度和账号设置不属于 GitHub Pages 配置。

## 校验

```powershell
python scripts/check_site.py
```

校验包括内部链接及资源文件的大小写、JSON 字段和数值、后端请求及 jQuery 残留、内联 JavaScript 语法（安装 Node.js 时执行）。GitHub Actions 每次发布前会自动校验。

## 目录

```text
.github/workflows/pages.yml  自动校验和部署
index.html                  站点入口
*.html                      其他页面
static/                     本地样式、脚本、字体、图片
data/                       固定的公开数据快照
scripts/check_site.py       发布前校验
.nojekyll                   禁用 Jekyll 处理
```

更新时间：2026-10-15。

# PolyU Eats Now

美味佳肴，无需费心揣摩。打开页面，查看理大校园现在有哪些餐厅可以在线下单，再跳转商家的官方系统。

## 为什么做这个小工具

香港理工大学（The Hong Kong Polytechnic University，Hong Kong PolyU）有不少餐厅支持在线点餐，但入口分散在不同的平台。有时候来到学校，才发现想吃的食堂已经关了；想找另一家，又得把点餐链接一个个打开，看看现在还能不能下单。

所以，我做了 **PolyU Eats Now**，希望给在校师生提供一个方便的小工具：把校园餐厅的点餐入口和当前可下单状态整合到一起，打开一个页面，就能查看哪些餐厅现在还接受在线订单，再直接前往官方系统点餐。少点几个链接，少跑一次空路，让在校园找一顿饭更省心。

Many restaurants at Hong Kong PolyU offer online ordering, but their links are scattered across different platforms. Sometimes I would arrive on campus only to find that the canteen I had in mind was already closed. Finding an alternative meant opening restaurant links one by one to check whether I could still order.

I built **PolyU Eats Now** to make that everyday task easier for fellow students and staff: bring the ordering links and current availability together in one place, see which restaurants are accepting online orders, and go straight to their official ordering pages. Less time checking links, fewer wasted trips, and an easier way to find your next meal on campus.

工具查询的是**当前是否可以在线下单**，不能单凭这个状态判断实体餐厅是否开门或有座位。The tool checks **online ordering availability**; this does not by itself confirm whether a restaurant is physically open or has seating.

## 致谢 / Acknowledgements

开始做这个项目时，我没有编程基础，只有校园生活中的一个小困扰，以及一个“能不能方便一点”的想法。感谢 **OpenAI 的 ChatGPT 和 Codex**，从梳理需求、编写代码，到排查问题、配置部署和整理文档，帮助我一步步把想法变成了可以使用的小工具。希望把它分享出来，能让同样没有基础的人也愿意试着动手，也欢迎更有经验的开发者一起改进，让它更好地服务理大师生。

I started this project with no programming background, just a small frustration from campus life and an idea for making it easier. Thank you to **ChatGPT and Codex by OpenAI** for helping me turn that idea into a working tool—from planning and writing code to troubleshooting, deployment and documentation. I hope sharing the project encourages other beginners to try building something useful, and gives more experienced developers a starting point to improve it for the PolyU community.

这是独立校园项目，并非香港理工大学官方应用。**状态只来自官方点餐系统的实时证据，不按营业时间猜测。**

## 可以做什么

- 查看 16 家校园餐厅；分别筛选可下单、停单、尚未确认和仅手机 App 下单。
- 英文、简体、繁体切换；首次默认英文，按钮顺序为简／EN／繁。
- 查看在线堂食／外带支持、官方入口和检查时间。在线堂食不代表实体餐厅有座位。
- 收藏保存在自己的浏览器；部分入口标注手机限定、网上付款和 15 分钟点餐时限。
- 手机可添加到主屏幕。后台自动检测，访客刷新不会触发额外的商家抓取。

没有代付、自动下单、账号登录、实时菜单同步或 AI 菜单翻译。商家用语小词典是静态解释；订单、限时和支付全部由官方系统处理。

## 第一次在 Windows 运行

安装 Python 3.10+ 和 Vite 7 支持的 Node.js（20.19+ 或 22.12+），解压／克隆代码，在项目目录的 PowerShell 中运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\start.ps1 -Setup
```

会安装依赖和 Chromium、构建前端并启动网站，需要联网。电脑打开 http://127.0.0.1:8000；首次启动会逐家检查餐厅。关闭这次前台运行用 Ctrl+C。

以后双击 **Start PolyU Eats Now.cmd** 可在后台运行。**Enable Auto Start.cmd** 启用登录 Windows 后自动运行；**Disable Auto Start.cmd** 取消。没有自动设置关机后继续服务；电脑必须登录、联网且不休眠。

## 手机和服务器

个人电脑可以选用免费的 Tailscale Funnel：自己安装并登录客户端，再运行 **Configure Fixed Phone.cmd**，完成官方的首次公网分享确认。网站会得到类似 `https://polyueatsnow.<你的网络名>.ts.net` 的固定网址，朋友只用浏览器即可。

这会公开分享网站，网址不是密码。公开仓库不提供作者的账号配置；每位使用者必须配置自己的设备和地址。

长期在线可部署到 Linux 云服务器。项目提供 Docker／Compose／Caddy 配置，需要自己的域名和 HTTPS。只上传前端无法更新真实餐厅状态。云端 Docker 构建和容量尚未实测。

## 修改和恢复

- [维护指南](docs/MAINTENANCE.md)：界面、三种语言、餐厅资料、检测器分别在哪里修改。
- [备份恢复与迁移](docs/RESTORE_AND_MIGRATE.md)：换电脑、恢复自动启动、搬到服务器。
- [部署说明](DEPLOYMENT.md)、[检测覆盖](CHECKER_STATUS.md)、[资料来源](DATA_SOURCES.md)。
- [贡献指南](CONTRIBUTING.md)：报告问题、增加证据、提交 Pull Request。

检测证据最多有效 180 秒，不能把旧 OPEN 当作现在可下单。网页被安全验证拦截或只有 App 的店仍可能无法确认；没有绕过验证或模拟支付。

代码与原创文档采用 [MIT 许可证](LICENSE)。校徽、校名标识和第三方素材不包含在这份代码授权内，见 [素材说明](THIRD_PARTY_NOTICES.md)。

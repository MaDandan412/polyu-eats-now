# 在 iPhone 使用 PolyU Eats Now

本项目需要运行 FastAPI 和真实 Chromium 检测器。只上传前端到免费静态空间，不能提供自动更新的点餐状态。
部署成功后，前端和 `/api/restaurants` 使用同一个 HTTPS 地址；手机不需要安装 Python 或 Chrome。

## 免费选择：截至 2026-10-01 的官方说明

| 方案 | 免费条件与限制 | 对本项目的判断 |
| --- | --- | --- |
| Cloudflare Quick Tunnel | 不需要账号或域名；临时 HTTPS 地址，停止本机连接进程即失效；没有可用性保证 | 已用于本次手机体验；电脑必须保持开机联网，不能代替云服务器 |
| Oracle Cloud Always Free | Ampere A1 的免费账号额度相当于总计 2 OCPU、12 GB 内存；必须在主区域，可能缺货；空闲实例可能被回收 | 内存较适合浏览器检测器；需要自行维护 Linux、HTTPS 和账户 |
| Render Free Web Service | 512 MB、0.1 CPU；15 分钟无访问休眠，再次访问约一分钟启动；750 小时/月由工作区共享；较多主动外部请求可能被暂停 | 可用于短期尝试，但 Chromium 可能超内存，而且冷启动会影响首次打开；不承诺稳定运行 |
| Hugging Face Spaces | CPU Basic 无小时费，但新建 Docker/Gradio Space 已要求付费计划；普通账号免费的是静态空间等限定用途 | 不把 Docker Spaces 推荐成完全免费方案 |

资源、注册资格、额度和收费以账户后台为准。这些平台的免费额度不代表本项目已经成功部署或通过云端运行测试。

官方资料：

- [Oracle Always Free](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)
- [Render 免费服务限制](https://render.com/docs/free) / [CPU 与内存](https://render.com/docs/compute-plans)
- [Hugging Face Spaces 当前创建条件](https://huggingface.co/docs/hub/spaces-overview)
- [Cloudflare Quick Tunnel](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)

## 重启电脑后恢复手机体验

在本项目目录双击 **Start PolyU Eats Now.cmd**。它会启动后台自动检测和临时 HTTPS 连接，并打开 `PHONE_PREVIEW.html`，其中显示本次手机链接及二维码。已运行时会复用服务，不重复启动；启动进程关闭后后台仍运行，但电脑关机、重启、休眠或断网会中断体验。

当前链接同时写在 `PHONE_URL.txt`。手机必须使用启动页中的最新地址，旧链接和旧主屏幕图标不会自动改到新地址。手机保存到主屏幕时，需使用新地址重新添加。

双击 **Stop Phone Preview.cmd** 只关闭本次公网预览连接，电脑本地网页和检查服务继续运行。运行信息和日志在 `.runtime`；停止操作核对进程创建时间和可执行文件身份，防止重启后旧进程编号被其他应用复用。

当前开发电脑已配置当前用户登录 Windows 后自动恢复。使用启动文件夹中的 **PolyU Eats Now.lnk**，无需手动改注册表、改防火墙或安装项目系统服务。双击 **Enable Auto Start.cmd** 可在已安装依赖的电脑启用，**Disable Auto Start.cmd** 可取消；只操作属于此项目的快捷方式。启动过程无控制台窗口，网络尚未就绪会重试，最多 10 次，日志在 `.runtime/login-start.log`。已按实际快捷方式试运行并确认复用服务，没有再次重启电脑测试。

这里的自动启动指**登录当前 Windows 用户后**；关机、休眠、断网或停在登录界面时，手机仍不能获取新的实时数据。缓存页面能打开不代表更新服务在线。

首次解压源码包时，仍需先执行 `start.ps1 -Setup`，安装项目依赖。已安装好的本机可直接双击启动入口。缺少 cloudflared 时，启动器只从 Cloudflare 官方 GitHub Release 下载，并核对官方 SHA-256 摘要后执行。下载文件留在 `tools`，不写入系统目录。

2026-10-01 用户再次重启电脑后，后台未启动，而 PWA 页面缓存仍能打开，造成 could not refresh。已恢复服务并验证网页刷新、本机检查时间持续推进和临时 HTTPS API 可达；补上登录自动启动。实物 iPhone 访问仍由用户确认。

## 免费固定手机地址：Tailscale Funnel

Tailscale Personal 个人计划免费；Funnel 对全部计划提供，仍处于 beta、有带宽限制。它能提供稳定 HTTPS 设备地址，并允许没有安装 Tailscale 的朋友直接用浏览器打开。

1. 安装 [Tailscale 官方 Windows 客户端](https://tailscale.com/download/windows)，在托盘图标选择 Log in，登录个人账号。安装确认、服务条款与账户登录由用户本人完成。
2. 在项目目录运行 **Configure Fixed Phone.cmd**。只接通 `http://127.0.0.1:8000`，设备名称设为 `polyueatsnow`，使用 `--bg` 保留 Funnel 配置。保留电脑原有 DNS 设置（不接受 Tailscale DNS），不配置远程桌面、共享文件或出口节点。
3. 首次使用需要在官方网页 **Enable Funnel**。页面会启用 HTTPS 证书，并为当前账号网络的成员开放 Funnel 使用权限；设备名称会进入公开证书日志。确认这一步后才启用。
4. 用公开 HTTPS `/api/health` 验证此应用与检测器可达；成功后将固定地址保存至 `.runtime/fixed-phone.json`，并生成 `PHONE_PREVIEW.html` 和二维码。DNS 首次生效可能需等待最多约 10 分钟，失败时可稍后重试；未验证前不写入固定地址。
5. 以后登录 Windows 后自动启动后端，Tailscale `--bg` 配置会自行恢复。固定地址暂时断连时保留原地址，不重新生成随机网址。电脑需开机、联网且不休眠；后台启动后各餐厅仍需重新检测。

地址形式为 `https://polyueatsnow.<账号网络名>.ts.net`，后半部分由 Tailscale 分配；这不是独立注册的 `polyueatsnow.com`。不要随意改设备名、删掉设备或更换账号网络，以免改变地址。

关闭固定公网入口可使用 `tailscale funnel --https=443 http://127.0.0.1:8000 off`；这不会关闭电脑本机网站。**Stop Phone Preview.cmd** 当前只关闭 Cloudflare 临时连接，不用于停用 Tailscale。不要执行 `funnel reset` 清空其他服务配置。连接固定地址并确认后可停掉旧临时连接。

资料：[免费个人计划](https://tailscale.com/docs/reference/free-plans-discounts)、[Funnel](https://tailscale.com/docs/features/tailscale-funnel)、[重启后的背景连接](https://tailscale.com/docs/reference/tailscale-cli/funnel#effects-of-rebooting-and-restarting)。当前开发电脑已完成安装、用户账号登录和首次启用确认；固定 HTTPS 网页、API、正常刷新和固定地址复用已验证。没有实际重启电脑测试；服务端检测覆盖限制保持不变。

## 已准备的 Docker 部署包

项目根目录包含 `Dockerfile` 和 `.dockerignore`，自动构建 React 前端、安装 Python 依赖和 Chromium，再用一个服务提供网页和 API。
容器以普通用户运行。只启动一个 Web worker，避免每个 worker 都重复抓取所有餐厅。

在安装了 Docker 的 Linux 服务器或电脑上，在项目根目录运行：

```sh
docker build -t polyu-eats-now .
docker run -d --name polyu-eats-now --restart unless-stopped \
  -p 127.0.0.1:8000:8000 --shm-size=1g polyu-eats-now
```

这会绑定服务器本机端口。通过服务器上的 Caddy 或 Nginx 把自己的 HTTPS 域名反向代理到 `127.0.0.1:8000`；域名、DNS、HTTPS 和服务器入口规则需要按所用平台配置。本次只开通临时手机预览；尚未创建云账号、绑定支付方式、修改本机防火墙或创建长期云端部署。
在 Render 可新建 Web Service，选择 Docker，使用此文件构建。平台会提供 HTTPS 地址；容器读取平台的 `PORT`，无需单独部署前端。
Render Free 仅作为试用路径，内存不足或外部流量限制可能导致检测器重启、未知状态或服务暂停。未在 Render 实际验证。

## 部署后确认

1. 打开 `/api/health`，应看到 `ok: true`、`checker_ready: true`。这仅表示服务和浏览器准备就绪，不代表每家已确认。
2. 打开首页，首次启动会显示「正在检查」，结果逐家出现。
3. 等一轮检查完成，看首页覆盖数量，检查 `/api/restaurants` 的 `last_checked` 会继续推进。不要把健康检查通过误当作抓取成功。
4. 如果检查短暂抛出网络异常，仅保留原核实时间三分钟有效期内的结果并提示刷新失败；新的停单、验证屏障或不可靠证据立即取代旧结果。超过三分钟的证据失效，不能据旧菜单判断现在可下单。
5. 三家 Mobile App 餐厅仍无法由网页确认；H Café / W Kiosk 等未确认来源的限制见 `CHECKER_STATUS.md`。

当前检测结果存在内存中，服务重启后会重新检查。免费平台休眠不能通过保存旧 OPEN 状态解决。

## 加入 iPhone 主屏幕

在 Safari 打开部署后的 HTTPS 地址 → 分享 → **添加到主屏幕**；如果显示「作为 Web App 打开」，保持开启。
之后可从主屏幕打开。官方点餐链接仍交由商家页面处理；Block Y 需手机直向显示，并遵循商家的 15 分钟倒数。
[Apple 官方步骤](https://support.apple.com/guide/iphone/open-as-web-app-iphea86e5236/ios)

## 暂时不申请云账号：同网络预览

可以让电脑与 iPhone 连接同一家庭路由器或手机热点；在项目根目录运行下面的命令，把 `<电脑的局域网IP>` 换成该网络分配的电脑地址：

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host <电脑的局域网IP> --port 8001
```

在 iPhone Safari 打开 `http://<电脑的局域网IP>:8001`。电脑必须保持运行。校园 Wi-Fi 可能隔离设备，不能保证两台设备互访。
HTTP 方式适合临时预览页面，完整 PWA 离线能力需要 HTTPS；本项目没有自动修改防火墙或启动这个网络服务。

## 本次验证范围

本机前端构建通过，三种语言、语言持久化、简繁搜索与手机宽度在浏览器验证。Docker 构建及云端 Chromium 的内存、网络可达性与服务稳定性尚未验证；本机未安装 Docker。

## 固定地址与低价方案

最新现价、域名查询、访问量估算和固定 HTTPS 部署步骤见 [HOSTING_PLAN.md](HOSTING_PLAN.md)。`compose.yaml` 与 `Caddyfile` 已准备；账户、服务器、域名尚未开通，部署文件未在 Docker 实测。

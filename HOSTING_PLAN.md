# PolyU Eats Now：固定地址与小范围部署

核对日期：2026-10-01。价格使用官方资料；以下方案尚未购买、注册或实际部署。港币预算按 US$1≈HK$7.8 估算，不含税、银行卡手续费及可选附加服务。

## 按最新预算：先试阿里云 68 元方案

用户提供的[阿里云活动页](https://cn.aliyun.com/benefit/select/ecs?from_alibabacloud=&utm_content=se_1019898442)已在浏览器核对：个人开发者栏目，2 核／2 GB、40 GB ESSD、200 Mbps 峰值带宽、1 年。在地域切换为**马来西亚（吉隆坡）**后，仍显示**新人专享人民币 68 元／年**。

海外选项还包括马尼拉、雅加达、曼谷、首尔及欧美，本次该套餐的下拉列表没有香港、新加坡或东京。其他地区的报价未逐个验证。200 Mbps 是峰值，不能视为随时保证的持续带宽或访问人数。

「了解优惠」说明同一实名认证账号仅可购买一次、限购 1 件、不可叠加优惠券。吉隆坡页面同时显示官网折扣价人民币 672 元／年，但它不是已确认的下一年度续费账单。**68 元只能用于首年预算，续费须登录后单独询价**；不把其他产品的同价续费规则套到此优惠。

官方[使用须知](https://help.aliyun.com/zh/simple-application-server/product-overview/usage-notes)说明：中国内地节点对外提供网站前需ICP备案，非内地节点不需ICP备案。面向香港用户，可先试吉隆坡；商家网页的云端可达性仍需实际验证。

初期优先试 2 GB，代码已支持 `CHECK_CONCURRENCY=2`，减少同时打开的商家页面。直接本地启动仍默认最多 4 个；Compose 默认 2 个，也可在 1–4 范围调整。原有 180 秒状态有效期不延长，较低并发可能让完整检查周期变慢。没有声称已在 2 GB 云机上验证内存和全部入口。

## 需要更多内存时的 4 GB 备选

一台 Linux VPS 同时运行网页、API 和后台检测器，单实例、单 Web worker。网页访问读取已检查结果，不会让每位访客重新爬 13 个入口；主要内存和 CPU 开销是后台 Chromium。下面更贵的 4 GB 方案保留为后续备选，初期不再以它们作为起步要求。

| 方案 | 官方资源与费用 | 适用判断 |
|---|---|---|
| OVHcloud VPS-1，新加坡 | 2 vCore、4 GB、40 GB NVMe；年付 US$54.48，折合 US$4.54/月，未含税 | 4 GB 备选：近香港，2026-10-01 配置器显示 Available now。该报价选了 12 个月承诺，不能当成自由月付价格；年度自动续期条款见配置器。 |
| Hetzner CX23，德国／芬兰 | 2 vCPU、4 GB、40 GB；当前 US$6.49/月，Primary IPv4 另 US$0.60/月，共 US$7.09/月，未含税 | 月度费用较低，但当前公开页面标为不可用，需要有库存才能购买。不是新加坡报价。欧洲到商家的加载延迟需部署后验证。 |
| AWS Lightsail Linux，含 IPv4 | 4 GB、2 vCPU、80 GB、4 TB 套餐 US$24/月 | 可作为有月付需求的备选，但对朋友小范围体验费用偏高。2 GB 套餐 US$12/月，当前四个浏览器上下文的内存峰值未经云端验证，不直接承诺能稳定运行。 |

OVH 新加坡 VPS-1 的官方页脚说明为 **500 GB/月流量额度**；超额降为 10 Mbps。配置器摘要的 “unlimited” 不能盖过亚洲地区的限额。Hetzner 欧洲包含至少 20 TB/月。AWS 额度受地区及流量规则影响，购买时以所选地区为准。

官方来源：

- [OVH 资源和亚洲流量限制](https://www.ovhcloud.com/asia/vps/)
- [实际核对的 OVH 新加坡配置器：12 个月计费](https://www.ovhcloud.com/asia/vps/configurator/?brick=VPS%2BModel%2B1&planCode=vps-2027-model1&pricing=upfront12&processor=+&storage=40__SSD__NVMe&vcore=2__vCore)
- [Hetzner 2026-06-15 现行价格](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) / [IPv4 费用](https://docs.hetzner.com/general/infrastructure-and-availability/ipv4-pricing/) / [配置和当前库存](https://www.hetzner.com/cloud/cost-optimized/)
- [AWS Lightsail 官方价格](https://aws.amazon.com/lightsail/pricing/)

## 可以用 polyueatsnow 做固定地址

**低预算优先 `polyueatsnow.top`**。万网官方普通域名价格表当前如下（人民币）：

| 后缀 | 首年注册 | 当前每年续费 |
|---|---|---|
| .top | 14 元 | 39 元 |
| .xyz | 14 元 | 120 元 |
| .cn | 38 元 | 42 元 |

来源：[万网价格总览](https://wanwang.aliyun.com/help/price.html)。活动、白金词和账号资格可能改变最终报价。浏览器查询 [polyueatsnow.top](https://porkbun.com/checkout/search?q=polyueatsnow.top) 时，`.top` 与 `.xyz` 都显示可注册；`.cn` 的具体名称可用性未查询。查询不是预留，尚未注册任何域名。

**68 元首年服务器 + 14 元首年 .top ≈ 82 元人民币首年**，以实际订单确认能享优惠为前提。第二年域名目前 39 元，服务器续费另询；固定网址不因换服务器改变，只更新 DNS。

`.com` 仍可作为以后选择：2026-10-01 Porkbun 查询可注册，首年和当前续费均为 **US$11.08/年**。Verisign RDAP 查询没有注册记录。它不再是初期优先方案。

作为较高预算的对照，OVH 年付 US$54.48 + .com US$11.08 = US$65.56/年，约 HK$511/年，未含税或支付手续费。

不想先付域名费，可以申请 **`polyueatsnow.duckdns.org`**：Duck DNS 官方提供免费的固定子域名，指向自己的服务器 IP。这个名字尚未申请，其可用性需登录后确认；服务器本身仍需付费。

`polyueatsnow.pages.dev` 也可能作为免费前端地址，但 Cloudflare Pages 的静态前端不代替当前 Python／Chromium 后台，所以现阶段单服务器加域名更简单。所有平台子域名都要实际创建成功才能确认被占用情况，当前没有承诺这些地址已经开通。

- [Porkbun .com 注册／续费价格](https://porkbun.com/products/domains)
- [域名查询入口](https://porkbun.com/checkout/search?q=polyueatsnow.com)
- [Duck DNS 免费子域名说明](https://www.duckdns.org/about.jsp)
- [Cloudflare Pages 固定子域名](https://developers.cloudflare.com/pages/configuration/custom-domains/)

## 访问量：按真实请求量估算

当前前端每 15 秒读取一次状态。一次 16 家餐厅的 API 响应实测约 **16.9 KB 原始／2.84 KB gzip**，具体随状态文字变化。
按每个用户每天保持页面打开 **1 小时**、每月 30 天，保守以 3 KB 压缩响应、每天另加载 150 KB 页面资产计算：

`每用户每月 ≈ (3 KB × 240 次 + 150 KB) × 30 ≈ 26 MB`

| 使用规模 | API 请求量峰值（所有人同时打开） | 估算用户端月流量 |
|---|---|---|
| 20 人 | 1.3 请求/秒 | 约 0.5 GB |
| 100 人 | 6.7 请求/秒 | 约 2.6 GB |
| 500 人 | 33 请求/秒 | 约 13 GB |

这里只估算浏览器读取网页和状态的流量；TLS、请求头、重新加载、更新、爬取商家页面、镜像下载等另有开销。不要用 500 GB 除以这张表来声称能支持上万用户。实际部署后应监测总流量和 Chromium 内存峰值。

本机缓存 API 进行了 150 次读取、10 个同时请求的检查，150 次全部成功；中位数约 335 ms、95 分位约 627 ms。它说明读取页面不会等待每家爬取完成，**不是对低价 VPS 的性能保证**。2 GB 初期按 20–50 名日常用户、约 20 人同时打开作为试用目标；它是规划值，并非云端实测容量。更高规模必须观察真实云机的浏览器内存、API 延迟和检测覆盖率，再决定是否升级。

## 已准备的固定域名部署文件

`Dockerfile`、`compose.yaml`、`Caddyfile` 和 `.env.example` 已准备。Docker Compose 配置网页与检测器同源、HTTPS、证书持久保存、日志轮转和服务异常／服务器重启后的自动恢复。

部署到自己已开通的 Linux 服务器后：

1. 安装 Docker Engine 和 Compose；复制项目。
2. 申请自己的域名或免费子域名，把 DNS 指向服务器的固定公网 IP。
3. 复制 `.env.example` 为 `.env`，设置实际属于自己的 `EATS_DOMAIN`；2 GB 先使用 `CHECK_CONCURRENCY=2`。示例 `polyueatsnow.top` 未注册，不会自动开通域名。
4. 在服务器安全组允许网页入口 TCP 80、443；API 不另开放 8000。
5. 执行 `docker compose config` 核对配置，再 `docker compose up -d --build`。
6. 通过固定 HTTPS 地址核对 `/api/health` 的 checker_ready，以及餐厅 last_checked 持续更新。仅容器健康不代表全部点餐页面均可验证。

自动 HTTPS：[Caddy 官方文档](https://caddyserver.com/docs/automatic-https)。部署文件尚未在 Docker 或真实云服务器运行验证；当前电脑没有 Docker。前端正式构建和 26 项后端测试已经通过，新增验证较低检测并发及零值配置不会造成检测停滞。商家安全验证、报错页面和只支持 App 的来源仍会影响覆盖率，换服务器不会自动解决这些缺口。

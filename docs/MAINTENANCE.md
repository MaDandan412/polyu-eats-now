# 功能修改与维护指南

## 主要文件

| 想修改什么 | 文件 | 注意事项 |
| --- | --- | --- |
| 首页、筛选、收藏、Info | `frontend/src/App.tsx` | 优先保留手机布局；收藏在浏览器本地 |
| 字体、颜色、卡片布局 | `frontend/src/style.css` | 检查 320 / 390 像素宽度 |
| 英文／繁体／简体文案 | `frontend/src/locales/` | 繁体原文 + 简体人工覆盖；构建会生成简体 |
| 服务支持、状态和过期规则 | `frontend/src/domain.ts`、`backend/models.py` | 在线堂食与实体座位不是同一回事 |
| 餐厅资料和来源 | `data/restaurants.json`、`data/sources.json` | 名称优先官方，未知信息不能猜测 |
| 官方网站只读浏览 | `backend/checker.py` | 使用手机网页证据，不加入购物车 |
| 平台状态解析 | `backend/adapters/` | 各平台独立；菜单存在不能直接判 OPEN |
| 定时更新、并发、有效期 | `backend/service.py` | 前端请求只读取结果，不触发额外抓取 |
| API 与前端服务 | `backend/main.py` | 保持同源，接口不缓存 |
| 手机限定下单入口 | `frontend/src/OrderLaunch.tsx` | 二维码只包含官方入口，不能复制订单会话 |
| Windows 自动启动 | `tools/login_start.py`、`tools/configure_autostart.ps1` | 当前用户登录后启动，固定地址不在源码中 |
| Tailscale 固定入口 | `tools/tailscale_phone.py`、`tools/phone_preview.py` | 每位部署者自己登录和验证公开地址 |

## 修改后验证

在项目虚拟环境中执行：

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests tools/tests -q
cd frontend
npm.cmd run build
```

界面变化后用浏览器检查三种语言、搜索、收藏、筛选、320/390 像素布局和刷新失败提示。前端构建后的文件在 `frontend/dist`；生产环境重新构建后才会看到修改。

后台代码变化需要重启对应的项目服务；不要终止其他 Python 项目。自动检查服务重启后会从无结果开始核实，不沿用过期 OPEN。

## 检测器贡献

先确认店铺身份、当前接单模式、可购买食品控件，再增加平台规则和关键行为测试。早餐、午餐、下午茶分类的食品会变化；需要查看当前分类和其它可能可用的分类，不能把固定时间写成状态答案。商家明确停单优先，验证码／登录屏障返回 UNKNOWN。

证据有效期 180 秒；短暂异常只保留原时间戳仍有效的结果。`CHECK_CONCURRENCY` 范围 1–4，Compose 默认 2。降低并发会增加检测周期，应检查是否影响证据覆盖；没有针对云服务器完成容量保证。

## 后续版本方向

Order.place 安全验证可使用独立本机 Chrome 会话，见 [独立验证指南](ORDERING_VERIFICATION.md)。启动入口为 `Open Ordering Verification.cmd`；浏览器资料只留在 `.runtime`，不提交 Git，也不包含在备份中。平台仍可能再次验证。

Eats365 使用 Chromium 自己的浏览器标识进入官方 Pickup 流程，并检查「Ready for Pickup Immediately」与匹配商品详情的可用购买控件。Safari 页面结构不同，不能把一个版本的选择器用于另一个版本。打开商品详情不等于加入购物车，检测不得点击购买按钮。

优先补齐可靠检测、移动端体验与平台失败原因。实时菜单、点餐用语翻译、登录和支付等需要独立设计；当前版本不承诺这些功能。迁移微信小程序可复用 API、基础资料与领域规则，但需要替换浏览器界面／存储，并按小程序要求配置服务域名。

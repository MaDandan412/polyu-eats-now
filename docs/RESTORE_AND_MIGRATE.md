# 备份、恢复与迁移

## 生成独立备份

项目虚拟环境安装后，在项目目录运行：

```powershell
.\.venv\Scripts\python.exe tools/backup_project.py
```

默认保存在用户的 Documents / `PolyU Eats Now Backups`，每份文件带香港时间时间戳，不覆盖旧备份。包内有源码、构建好的网页、部署配置、恢复说明、逐文件 SHA-256 清单；同一电脑的非机密手机配置另放在 `desktop-config/`。安装依赖、Chromium、进程编号、日志、账号登录状态和私钥不打包，需要在恢复设备重新安装／登录。

校验：

```powershell
.\.venv\Scripts\python.exe tools/backup_project.py --verify <备份ZIP完整路径>
```

建议另外复制到自己的移动硬盘或可信云盘。Documents 里的副本可避免删掉项目目录一起丢失，但不能防止整块硬盘损坏。

## 在原电脑恢复

1. 先解压到独立目录，不覆盖正在运行的网站。包内 `polyu-eats-now/` 是项目；`desktop-config/` 是原电脑配置参考。
2. 如只是找回修改文件，可与现有目录比较后恢复需要的源码，再重新构建。
3. 如要移动整个项目目录，先在旧目录执行 **Disable Auto Start.cmd**。旧目录已不存在时，可用 Windows 的 `shell:startup` 打开启动文件夹，核对并移除指向旧项目的 **PolyU Eats Now** 快捷方式，再安装新目录。不要移除其他应用的启动项。
4. 按 README 执行 `start.ps1 -Setup` 安装依赖；恢复时需要联网。
5. 后台尚在旧目录运行时先停止那一份已确认的项目服务，避免 8000 端口冲突；不能根据旧备份的进程编号停止程序。
6. 双击 **Enable Auto Start.cmd**，重新生成指向新目录的启动项。原快捷方式的绝对路径记录仅供参考，不直接复制使用。
7. 同一 Tailscale 设备／账号仍在时，运行 **Configure Fixed Phone.cmd** 重新验证并保存固定 URL。原固定配置仅供核对；不恢复过期日志、锁文件和进程记录。

## 换另一台电脑

安装 Python、Node.js 和 Tailscale，重新登录自己的账号，然后按 Windows 运行步骤设置。原固定网址属于原 Tailscale 设备，不保证换电脑自动沿用。不要直接复制旧设备登录状态、密钥或 `.runtime`。需要沿用同一名称时，先在 Tailscale 控制台确认旧设备情况，避免名称冲突和打断原电脑服务。

## 部署到 Linux 服务器

准备服务器、Docker Compose 和自己拥有的域名。把公开源码上传服务器，在项目目录复制 `.env.example` 为 `.env`，将 `EATS_DOMAIN` 替换为自己的域名，并将 DNS 指向服务器。示例域名不是已经替你注册的域名。

```sh
cp .env.example .env
# 编辑 .env，填写自己的域名
docker compose up -d --build
```

确保服务器的 80／443 入口可用，由 Caddy 自动管理 HTTPS；不要把内部 8000 端口额外公开。Compose 配置后台持续运行，电脑关机也不会影响服务器网站。2 GB 服务器先使用 `CHECK_CONCURRENCY=2`，再实测内存、检查周期与有效覆盖。

验证 `/api/health` 的 `checker_ready`、`/api/restaurants` 的检查时间继续推进，以及手机首页没有刷新错误。健康接口成功不表示每个商家都已核实。Docker 构建和云端性能尚未实测，迁移时必须实际验证。

## GitHub 与个人配置

公开仓库保存源码、公共餐厅资料、说明和测试；不上传 `.runtime`、`.env`、浏览器配置或 Tailscale 登录状态。每位使用者自己的固定 URL 只放在本机运行目录。

修改可用 Git 分支和 Pull Request 保留历史。公开代码不会自动更新正在运行的电脑；拉取源码后还需要构建前端并重启自己的后台。详见 `CONTRIBUTING.md`。

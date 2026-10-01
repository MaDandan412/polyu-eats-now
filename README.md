# PolyU Eats Now

**Good food, less guesswork.** A mobile-first food-ordering availability tool for students and staff at **The Hong Kong Polytechnic University (Hong Kong PolyU)**, using evidence from official ordering systems.

[简体中文说明](README.zh-CN.md) · [Maintenance guide](docs/MAINTENANCE.md) · [Restore and migrate](docs/RESTORE_AND_MIGRATE.md) · [Search visibility](docs/SEARCH_VISIBILITY.md)

## Why I built this / 为什么做这个小工具

Many restaurants at Hong Kong PolyU offer online ordering, but their links are scattered across different platforms. Sometimes I would arrive on campus only to find that the canteen I had in mind was already closed. Finding an alternative meant opening restaurant links one by one to check whether I could still order.

I built **PolyU Eats Now** to make that everyday task easier for fellow students and staff: bring the ordering links and current availability together in one place, see which restaurants are accepting online orders, and go straight to their official ordering pages. Less time checking links, fewer wasted trips, and an easier way to find your next meal on campus.

香港理工大学有不少餐厅支持在线点餐，但入口分散在不同的平台。有时候来到学校，才发现想吃的食堂已经关了；想找另一家，又得把点餐链接一个个打开，看看现在还能不能下单。

所以，我做了 **PolyU Eats Now**，希望给在校师生提供一个方便的小工具：把校园餐厅的点餐入口和当前可下单状态整合到一起，打开一个页面，就能查看哪些餐厅现在还接受在线订单，再直接前往官方系统点餐。少点几个链接，少跑一次空路，让在校园找一顿饭更省心。

The tool checks **online ordering availability**; this does not by itself confirm whether a restaurant is physically open or has seating. 工具查询的是**当前是否可以在线下单**，不能单凭这个状态判断实体餐厅是否开门或有座位。

## Acknowledgements / 致谢

I started this project with no programming background, just a small frustration from campus life and an idea for making it easier. Thank you to **ChatGPT and Codex by OpenAI** for helping me turn that idea into a working tool—from planning and writing code to troubleshooting, deployment and documentation. I hope sharing the project encourages other beginners to try building something useful, and gives more experienced developers a starting point to improve it for the PolyU community.

开始做这个项目时，我没有编程基础，只有校园生活中的一个小困扰，以及一个“能不能方便一点”的想法。感谢 **OpenAI 的 ChatGPT 和 Codex**，从梳理需求、编写代码，到排查问题、配置部署和整理文档，帮助我一步步把想法变成了可以使用的小工具。希望把它分享出来，能让同样没有基础的人也愿意试着动手，也欢迎更有经验的开发者一起改进，让它更好地服务理大师生。

![PolyU Eats Now preview](docs/images/preview.png)

Independent community project. **Not an official PolyU application.** Availability is not inferred from opening hours. An unconfirmed outlet is never counted as orderable.

## Features

- 16 campus outlets; separate filters for confirmed availability and app-only ordering.
- English (default), simplified Chinese and traditional Chinese; device-local favorites.
- Official order links, supported online order modes and last-check timestamps.
- Mobile-only ordering handoff, QR codes, online payment and session-limit labels where verified.
- FastAPI periodically checks official pages with read-only Playwright adapters. Users read cached results without triggering extra merchant requests.
- React, TypeScript, Vite, Tailwind CSS and PWA support. Frontend and API share one origin.

There is no account system, payment processing, automatic ordering or menu synchronization. Ordering and payment remain on the merchant's site.

## Run on Windows

Install Python 3.10+ and a Node.js version supported by Vite 7 (20.19+ or 22.12+), then run in the project directory:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\start.ps1 -Setup
```

Open http://127.0.0.1:8000. Setup installs dependencies and Chromium, builds the frontend, and starts the local server. It needs internet access. Press Ctrl+C to stop this foreground run.

After setup, **Start PolyU Eats Now.cmd** starts the app in the background and creates a phone preview. **Enable Auto Start.cmd** enables startup after signing in to Windows; **Disable Auto Start.cmd** removes it. See the migration guide before moving the folder.

## Run on Linux / macOS

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python -m playwright install --with-deps chromium
cd frontend
npm ci
npm run build
cd ..
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Use a current supported Node.js release. OS dependencies may require administrative access on Linux.

## Hosting and phone access

Frontend-only hosting cannot run the availability checker. Use the included `Dockerfile`, `compose.yaml` and `Caddyfile` for a Linux server with your own HTTPS domain; see [deployment](DEPLOYMENT.md) and [migration](docs/RESTORE_AND_MIGRATE.md).

For a personal Windows computer, optional Tailscale Funnel provides a stable HTTPS device URL. Install and sign in to Tailscale yourself, then run **Configure Fixed Phone.cmd** and complete the first-use Funnel approval. Friends can use a browser without Tailscale. This publicly shares this app; a private site needs access controls. The PC must be signed in, online and awake.

Each user configures their own URL. Personal Tailscale configuration, logs, credentials and installed dependencies are not in this repository. Docker deployment files are prepared but have not been tested on a cloud server.

## API and evidence rules

- `GET /api/restaurants`: outlet metadata, status, reason and check timestamp; `Cache-Control: no-store`.
- `GET /api/health`: service identity, checker readiness and last completed cycle.
- `OPEN`: verified outlet, current ordering and a purchasable food or drink.
- `CLOSED`: official system explicitly stops current ordering.
- `LIMITED`: explicit restriction or only part of the outlet's ordering is confirmed.
- `UNKNOWN`: unavailable or insufficient evidence, access barriers or expired results.

Evidence expires after 180 seconds. A transient failure does not extend the previous timestamp; explicit closure or an access barrier replaces old evidence immediately. Online dine-in support is separate from physical seating and current availability. See [data sources](DATA_SOURCES.md) and [checker coverage](CHECKER_STATUS.md). Historical snapshots in documentation are not live status.

## Development and contributions

```sh
python -m pytest backend/tests tools/tests -q
cd frontend
npm ci
npm run build
```

Run tests with the project virtual environment. Contributions are welcome, particularly reliable adapters, source-backed names and mobile accessibility. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

Code and original documentation: [MIT](LICENSE). PolyU identity artwork and third-party content retain their owners' rights; they are excluded from the code license. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

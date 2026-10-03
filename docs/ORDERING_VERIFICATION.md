# 独立点餐验证窗口 / Isolated ordering verification

Order.place may require browser verification even when a restaurant accepts orders. This opt-in desktop feature lets you complete the official check yourself in a separate Chrome profile. It does not guarantee that a challenge will pass or remain valid.

Order.place 有时会要求浏览器安全验证，即使餐厅仍然接受订单。这个可选的桌面功能会打开独立 Chrome 窗口，供你自行完成官方验证；不能保证一定通过，也不能保证验证永久有效。

## Windows 使用方法

1. 先安装 Google Chrome，并保持本项目后台正在运行。
2. 双击项目根目录的 **Open Ordering Verification.cmd**。
3. 下一轮检查会打开文康、学生花园理及职员花园理的官方点餐标签页。出现验证框时由你完成；如果自动进入菜单，则无需额外操作。
4. 网页每 15 秒读取后台结果。只有核实当前接单模式和可购买食品后，才会显示可下单。

窗口可以关闭。下次检查会尝试在后台重新使用这份独立资料；如果官方再次要求验证，可再次打开上述入口。重启后台或重新登录 Windows 后也会尝试后台复用，但官方可能重新验证，不能保证重启后一直有效。

The running checker opens the window on its next cycle. Complete any official challenge yourself; if it loads the menu automatically, no manual action is necessary. You can close the window. Subsequent checks and app restarts attempt to reuse the dedicated profile in the background. Run the launcher again if verification returns.

## 资料存放和边界

- 仅使用 `.runtime/order-place-profile`；不会读取、复制或修改你的日常 Chrome 资料。
- 本机请求开关为 `.runtime/ordering-browser.json`。`enabled` 为 `false` 时禁用此功能；`verify_requested` 为 `true` 时请求显示窗口。
- Chrome 保存的站点会话留在这份本机资料中。不要分享或提交整个 `.runtime`；Git 和项目备份会排除它，换电脑后需重新验证。
- 没有新增公网控制窗口的接口。官网验证由人完成，检测器不会解验证码或关闭浏览器安全保护。
- 检测只浏览官方页面、选择当前点餐模式并检查商品控件；不会加入购物车、提交订单或支付。
- 遇到新的验证屏障仍返回 UNKNOWN，不用旧结果或营业时间猜测可下单。

Only this dedicated profile is used; your everyday browser profile is untouched. The profile may contain merchant session cookies and stays local, excluded from Git and backups. There is no public API to open or control the verification window. Challenges are completed by a human. The checker never adds items, places orders or pays, and an access barrier remains UNKNOWN.

Linux/cloud deployments need their own supported interactive verification setup; this Windows launcher is not a solution for a server without a desktop. The normal default checker remains available without this optional Chrome session.

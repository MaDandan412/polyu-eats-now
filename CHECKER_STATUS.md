# 自動點餐檢測：實證與覆蓋

2026-10-01 14:48（香港時間）的即時 API 快照。此報告不參與狀態判定；狀態會持續重新檢查。

當次網頁入口：**6 家可落單、0 家部分可用、3 家明確停單、4 家尚未確認**，確認覆蓋 **9/13**。另有 3 家僅提供手機 App，介面獨立分類，不計入網頁入口的尚未確認數量。
本輪覆蓋曾達 11/13；商家安全驗證、錯誤和網絡波動會使覆蓋變動，不能聲稱全部入口均已解決。

## 本輪修正

- 文康學生飯堂官方手機模式選擇器只提供「外賣」。修正為網上堂食不支持、網上外賣自取支持，附官方点餐頁面的來源連結。這與實體餐廳是否有座位是兩回事。
- 學生花園理原先提供的堂食標記未獲官方網上模式證據支持，已移除不確實的「支持」標记；不以未確認推斷不支持。
- 短暫檢查異常時，先前已核實結果可在**原有 180 秒有效期**內保留，明示檢查延遲，原始時間戳不延長。過期恢復 UNKNOWN；官方明示停單、新錯誤或安全驗證立即取代舊結果。
- 識別中文安全驗證及 CONTENT_NOT_FOUND，清楚說明缺口，避免一直等待後只報泛化超時。未繞過驗證。
- 只提供 App 的店獨立顯示「僅 App」，不再混入網頁入口的尚未確認列表。
- 前端首次默認英文，語言按「简／EN／繁」排列，保存使用者選擇。中文宣傳文案分別按內地和香港閱讀習慣潤色；餐廳名稱仍優先保留官方來源。
- API 與頁面資產加入壓縮；每位訪客讀取已檢測結果，不觸發一輪新的商家檢查。

## 已接通的實際證據

- Order.place：完整手機瀏覽器設定、已識別 Cookie 提示、即時點餐與外賣模式、店名及可購買食品控件。預訂模式不能判為 OPEN。
- Block Y：從官方品牌選擇器進入兩個校內品牌，分別核對有效倒數及可購買食品；兩者均可用才是 OPEN，一個可用為 LIMITED。
- SeitoPOS：即時點餐、餐廳身份、外賣模式及可用食品控件。
- UCR IQPOS／FoodCloud：檢查當前餐次分類，排除餐具、飲管、測試及售罄食品；已驗證不同分類和下午茶菜單。
- 官方停單優先於菜單。單純能打開餐牌、预訂、錯誤頁或禁用餐牌不能直接判 OPEN。
- 每家檢查完成立即更新，前端每 15 秒讀取。各卡片的即時證據最多有效 180 秒；支持方式是獨立的已核實資料，不隨網絡故障清空。

## 即時快照

| 餐廳 | 當次狀態 | 當次理由 |
|---|---|---|
| Communal Student Canteen | UNKNOWN | This platform does not currently allow this automated check to access the ordering page. |
| U Garden (Student Canteen) | UNKNOWN | Page is reachable, but current orderability could not be confirmed. |
| U Garden (Staff Canteen) | CLOSED | Official ordering system explicitly says current ordering is unavailable. |
| Block Y Outlet | OPEN | Grove and Tai Tai both show current ordering with purchasable food or drink. |
| VA Student Canteen | OPEN | Current ordering enabled with a purchasable menu item. |
| VA Staff Canteen | OPEN | Current ordering enabled with a purchasable menu item. |
| Staff Club Restaurant | OPEN | Current ordering enabled with a purchasable menu item. |
| Theatre Lounge | CLOSED | Official ordering system explicitly says current ordering is unavailable. |
| Gourmet Shop | OPEN | Current ordering enabled with a purchasable menu item. |
| H Café | UNKNOWN | The official ordering page reports an error before a restaurant menu can load. |
| V Café | CLOSED | Official ordering system explicitly says current ordering is unavailable. |
| W Kiosk | UNKNOWN | Ordering page marks its menus as “Do Not Use”. Orderability is unconfirmed. |
| Hung Hom Student Halls Canteen | OPEN | Ordering confirmed in the current “下午茶” menu, with a purchasable food or drink. |
| VA Café Starbucks | UNKNOWN | Mobile-app ordering only. Web availability cannot be confirmed. |
| X Café Pacific Coffee | UNKNOWN | Mobile-app ordering only. Web availability cannot be confirmed. |
| Star Café Pacific Coffee | UNKNOWN | Mobile-app ordering only. Web availability cannot be confirmed. |

## 驗證與限制

26 項後端測試通過，涵蓋可購買食品、售罄、餐具、禁用控件、預訂／即時模式、獨立品牌合併、證據過期、異常保留原有效期、官方新狀態立即取代舊結果、支持方式、中文安全驗證、API 壓縮及小伺服器的較低檢查並發。零值配置不會使檢查停滯。
前端正式構建通過；本輪瀏覽器確認首次默認 EN、简／EN／繁順序、兩種中文文案、語言保存、文康正確的網上服務方式和來源連結。320／390 像素視窗沒有頁面橫向溢出。
本機緩存 API 150 次讀取全部成功，10 個並行請求；這不是雲端容量保證。詳見 [HOSTING_PLAN.md](HOSTING_PLAN.md)。

尚未確認的原因包括花園理的間歇安全驗證／拒絕訪問、H Café 官方入口報錯，以及 W Kiosk 官方菜單標為 Do Not Use。3 家 App 店仍需公開或獲授權的狀態來源。不能以營業時間或舊菜單取代這些缺口。
沒有加入購物車、提交訂單或支付。尚未在實體 iPhone 上驗證 PWA 安裝和支付。已接通的平台仍需觀察其他日期及餐次。

來源见 [DATA_SOURCES.md](DATA_SOURCES.md)。目前仍是本機檢測器和免費臨時 HTTPS 預覽，個人電腦關機會中斷；尚未購買或部署長期雲端主機。固定網址及已準備的部署文件見 [HOSTING_PLAN.md](HOSTING_PLAN.md) 和 [DEPLOYMENT.md](DEPLOYMENT.md)。

# 資料來源與用語

核對日期：2026-10-01（香港時間）。這些資料描述名稱、位置與服務能力，不參與即時 OPEN / CLOSED 判斷。

- 16 家英文名稱及位置：[理大 CFSO 餐飲設施目錄](https://www.polyu.edu.hk/cfso/campus-environment-and-facilities/catering-facilities/catering-outlets/)。每家詳情網址保存在 `sources.json.info_url`。
- 網上只限外賣：現行官方詳情頁明確標為 “Takeaway Order Only” 的 9 家：U Garden 職員飯堂、Block Y、VA 學生飯堂、VA 職員飯堂、Staff Club、Theatre Lounge、Gourmet Shop、W Kiosk、紅磡宿舍飯堂。這些網上入口的 `dine_in=false, takeaway=true`，不代表餐廳沒有座位。
- 文康學生飯堂線上外賣：使用者 2026-10-01 更正後，再以手機設定讀取其官方點餐入口；模式選擇器僅顯示「外賣」，核實 `dine_in=false, takeaway=true`，來源標為 `official-ordering-page`。CFSO 的 520 個座位不代表網上支持堂食。
- 其餘網上服務方式以使用者已提供資料為準，標為 `user-provided`。資料未提供時保留 null，不翻譯成「不支持」。
- 官方樓宇中文：[PolyU Glossary — Buildings & Facilities](https://www.polyu.edu.hk/web/glossary/en/terms_relating_to_structure_and_organization_post/buildings_facilities/index.html)：文康大樓、邵逸夫樓、鍾士元樓、賽馬會創新樓及紅磡灣校園。樓層與平台描述作介面翻譯。
- 文康學生飯堂：[理大 GreenNet（2019）](https://www.polyu.edu.hk/greencampus/GreenNet/issue/21/stakeholder-article03.php)。只採用設施名稱，舊活動資訊、價格和時間不作當前依據。
- 花園理：[理大 2026 年校園發展處消息](https://www.polyu.edu.hk/cdo/featured/news-and-achievements/2026/hkie-excellent-building-award-2026/)；點餐網站當前顯示「花園 理」。介面保留官方用語，學生／職員飯堂作描述翻譯。
- 劇院茶座：[理大 ICCPOL 校內設施雙語資料](https://web.comp.polyu.edu.hk/iccpol09/la.html)。僅用於設施術語；當前品牌 Terrace in Seaside 仍按現行目錄保留英文，不沿用舊經營商資訊。
- 其餘英文品牌不自行發明中文譯名。`name_zh_origin` 記錄純官方名稱、官方品牌配翻譯描述，或原英文品牌。

## Block Y

入口：[官方點餐品牌選擇器](https://order.taitaiteaology.com/polyu-order/)。選擇器顯示 Grove 及台台・果腹。
以手機瀏覽器讀取，兩個品牌頁面均顯示有效的約 15 分鐘點餐倒數、有價格的食品及未售罄的增加控件；僅觀察，沒有加入購物車或提交訂單。
「網上付款」標記依據官方店鋪菜單的「去付款」入口及使用者的結帳觀察；不表示已核實每種支付渠道。15 分鐘由官方系統控制，本工具不另起一個可能不同步的計時器。
# 简体显示与点餐词典

官方繁体名称与来源保留在原始数据中；简体显示由 [OpenCC JS](https://github.com/nk2028/opencc-js) 在构建时转换，品牌英文保持原样。简体界面的普通话表达另行编辑，不作为商家的官方译名。
「走 X = 不要 X」来自用户提供的香港点餐语义观察，词典的走蔥／走冰示例按这条规则解释；少冰说明为常用字面区别。词典没有标称为官方餐厅文案，也没有实时 AI 推理。商家菜单与订单选项仍以原始页面为准。

## 花園理學生飯堂的線上堂食

原始使用者資料的 dine_in=true 沒有區分實體座位和網上模式。本輪無法從官方模式選擇器核實，最新頁面可能回傳停單或瀏覽器安全驗證，因此移除未經核實的網上堂食「支持」標記，保留 null，不把無證據當作「不支持」。官方 CFSO 詳情頁未明示 Takeaway Order Only，也不能自行把它改為 false。

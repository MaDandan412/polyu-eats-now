# 搜索收录 / Search visibility

公开发布与搜索收录是两件事。Google 发现、抓取和处理新网站可能需要几天到几周；网站上线、提交网址或设置 `robots.txt` 都不保证收录或排名。

Publishing a public site does not immediately add it to Google Search. Discovery, crawling and indexing can take days to weeks; publication and crawl requests do not guarantee indexing or ranking.

## 项目已提供 / Included in this project

- 首页 HTML 直接包含项目名称、香港理工大学全名、中英文介绍和源代码链接；JavaScript 加载后由实时界面替换，不预填可能过时的餐厅状态。
- 页面标题、简介和分享描述明确说明学校与用途。
- `/robots.txt` 允许抓取；首页没有 `noindex`。

The initial HTML contains the project name, university name, bilingual introduction and source link. The live interface replaces it once JavaScript loads. Metadata describes the app, and `robots.txt` permits crawling. These are basic discovery improvements, not confirmation of Google indexing.

## 网站拥有者可以做什么 / What the site owner can do

1. 让公开网址尽量持续在线。目前个人电脑托管需要电脑已登录、联网且保持唤醒；关机或休眠会影响外部抓取。
2. 登录 [Google Search Console](https://search.google.com/search-console)，添加自己的网站为 **URL-prefix 属性**（例如自己的完整 HTTPS Funnel 网址）。没有自己的域名 DNS 权限时，不选需要 DNS 验证的 Domain 属性。
3. 选择 HTML 标签验证，把 Google 实际给出的 `google-site-verification` 标签加入 `frontend/index.html` 的 `<head>`，重新构建前端，然后完成验证。不要填写别人的验证值。
4. 用“网址检查 / URL Inspection”检查首页、运行实时测试并请求编入索引。重复提交同一个网址不会加快处理。
5. GitHub 仓库不是自己控制的域名，不能按上述方式验证 GitHub 仓库页面。完善公开 README、简介和相关链接即可；是否收录仍由搜索引擎决定。

Keep the public site reachable, verify your own HTTPS URL-prefix property in Search Console using Google's actual HTML verification tag, then inspect the homepage and request indexing. Rebuild after adding the tag. You cannot verify a GitHub repository page as if you owned github.com. This one-page app does not require a sitemap to be discovered; consider one when adding separate public content pages.

本项目不代替你登录 Google，也不声称已经验证网站或提交收录。迁移到新域名后应重新检查对应的 Search Console 属性。

Search Console ownership verification and submission are separate from these code changes. Recheck the property when moving to a new domain.

参考 / Reference: [Google 抓取与收录说明](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)、[网站验证方法](https://support.google.com/webmasters/answer/9008080)。

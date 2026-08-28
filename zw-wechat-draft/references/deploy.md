# 固定 IP 部署指引 — 根治「每次都要加白名单」

## 根因
微信强制要求：调用其接口的来源 IP 必须登记在
`developers.weixin.qq.com/platform → 公众号 → 接口管理 → API IP 白名单`。
本机出口 IP 不固定（家庭宽带动态分配 / 开 VPN 节点漂移），所以每次都得手动加。

白名单本身**无法用 API 自动修改**（必须进后台手动点），因此「自动化加白名单」走不通。
唯一的根治法是：**让发出微信请求的那台机器拥有固定的公网 IP**。

## 三种部署形态

### 方案 A：本地关 VPN / 直连（最简，但不保证根治）
- 关掉 VPN/代理，用家庭宽带直连再推。
- 局限：家庭宽带多为动态公网 IP，光猫/路由器重连仍可能变。仅能减轻，不能根治。
- 适用：临时验证、偶尔推送。

### 方案 B：仅把「推送」搬到固定 IP 云机（推荐，最轻）⭐
把 `push_draft.js` + `wechat_config.json` 放到一台有固定公网 IP 的轻量服务器/云函数；
本地只负责渲染（HTML + 封面），然后把这两个文件传上去由云机调用微信 API。
- 云机只需 Node（无需 Playwright，封面在本地生成）。
- 白名单加一次云机 IP，以后本机怎么换 IP 都不受影响。
- 步骤：
  1. 准备一台固定 IP 机器（腾讯云轻量应用服务器 / 阿里云 ECS / 任意 VPS，最低配即可，约 ¥30–60/月）。
  2. 装 Node 18+：`curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs`
  3. 上传文件：
     `scp ~/.workbuddy/skills/zw-wechat-draft/push_draft.js 服务器:/opt/wx/ && scp ~/.workbuddy/wechat_config.json 服务器:/opt/wx/`
  4. 查云机出口 IP：`ssh 服务器 "curl -s https://ifconfig.me"`，把这个 IP 加入白名单。
  5. 本地推送改为：先把 content 的 HTML + 封面 scp 到云机，再
     `ssh 服务器 "node /opt/wx/push_draft.js --content /opt/wx/xxx_wechat.html --cover /opt/wx/xxx_cover.png --title '...' --digest '..."`
  6. 可选：在云机上写个极简 HTTP 服务（Express 或原生 http，约 20 行），本地用 `curl` 触发推送，免去每次 scp。

### 方案 C：整条流水线（渲染+推送）全上云（最彻底，较重）
把整个 `zw-wechat-draft` 技能目录 + Playwright 装到云机，本地只传 `content.json`，
云端完成渲染 + 截图 + 推送。
- 云机需装 chromium（`npx playwright install chromium`），规格稍高。
- 白名单同样只需加一次云机 IP。
- 适合：需要无人值守、批量推送的场景。

## 推荐结论
- 偶尔推：方案 A 临时顶一下，配合 `node publish.js --check-ip` 提前知道白名单是否命中。
- 经常推、受不了手动加：方案 B，成本最低、改动最小，白名单一劳永逸。

## 已内置的辅助能力
- `node publish.js --check-ip`：推送前单独探测白名单，命中则提示可直接推，未命中则打印微信返回的「实际 IP」供你加入（比本地 curl 准，是直接问微信要到的 IP）。
- 完整推送命令在白名单未命中时会**提前在渲染前拦截**并退出，不浪费截图/上传时间。

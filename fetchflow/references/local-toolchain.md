# 本机工具链映射（权威源：re-toolchain）

采集与逆向两线用到的本机工具，唯一权威源在：

`D:\Desktop\Craft\re-toolchain\toolchain-map.md`

## 使用规则

1. **任务启动时检测本机工具**，不要假设通用矩阵里的工具都存在：

   ```
   F:\tools\venv\Scripts\python.exe D:\Desktop\Craft\re-toolchain\check-tools.py --json
   ```

   `available: true` 的工具直接 CLI/库调用；结果记入"已验证事实"。
   注意：工具全部部署在 **F:\tools**（不占 C 盘），检测用 F 盘 venv 的 Python。

2. **crawl 线**（C1/C2）已装工具直接调用：
   - 反爬对抗：curl_cffi（TLS 指纹）→ cloudscraper（Cloudflare）→ Playwright（JS 渲染/强反爬，从轻到重）
   - 批量采集：Scrapy（结构化）→ yt-dlp（视频）→ gallery-dl（图库）
   - Electron/客户端：`npx asar extract` 解包 → `7za` 解 NSIS → Node 分析 JS
   - crawl4ai 仍是主引擎；curl_cffi/Playwright 用于 crawl4ai 策略之外的场景或验证。
3. **reverse 线**：委托 reverse-flow，其 `references/local-toolchain.md` 覆盖 R1-R4 阶段映射；本文件不重复。
4. **回退顺序**：同阶段从左到右；未装工具不阻塞——先推进，缺失项列入"建议下一步"，提示 `powershell -ExecutionPolicy Bypass -File D:\Desktop\Craft\re-toolchain\deploy-to-f.ps1` 补装。

工具安装/补装入口：`D:\Desktop\Craft\re-toolchain\deploy-to-f.ps1`（便携版到 F:\tools\apps，启动器在 F:\tools\bin）。

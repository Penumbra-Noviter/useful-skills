# 本机工具链映射（权威源：re-toolchain）

本机已安装/可安装的工具链与各阶段对应关系，唯一权威源在：

`D:\Desktop\Craft\re-toolchain\toolchain-map.md`

## 使用规则（覆盖 skill 内的通用 tooling-matrix）

1. **启动案例时先检测本机实际工具**，不要假设通用工具目录里的工具都存在：

   ```
   F:\tools\venv\Scripts\python.exe D:\Desktop\Craft\re-toolchain\check-tools.py --json
   ```

   JSON 里 `available: true` 的工具才能直接用；记录为"已验证事实"。
   注意：检测用 **F 盘 venv 的 Python**（工具全部部署在 F:\tools，不占 C 盘）。

2. **按阶段用已装工具**，直接 CLI/库调用，不要让用户手动打开 GUI。各阶段对应：
   - R1 分诊：`diec`（查壳）→ `7za`（解包）→ ImHex（hex）
   - R2 静态：`jadx`（APK）→ pefile/LIEF（PE/格式解析）→ Capstone/r2pipe（脚本化反汇编）→ Ghidra/radare2（反编译，已装于 F:\tools\apps）
   - R3 动态：Frida（`frida-trace`/`frida-ps`）→ Objection → x64dbg（GUI，必要时）
   - R4 协议/网络：`tshark` → Scapy → blackboxprotobuf → mitmproxy
3. **回退顺序**：同阶段按上表从左到右；未装工具不阻塞——用已有工具推进，缺失项列入"建议下一步"菜单，提示 `powershell -ExecutionPolicy Bypass -File D:\Desktop\Craft\re-toolchain\deploy-to-f.ps1` 补装。
4. **GUI 工具**（ImHex/Cutter/x64dbg/dnSpy）：仅当 CLI 无解或用户明确要看图形时才提示打开。

工具安装/补装入口：`D:\Desktop\Craft\re-toolchain\deploy-to-f.ps1`（下载解压便携版到 F:\tools\apps，启动器在 F:\tools\bin）。

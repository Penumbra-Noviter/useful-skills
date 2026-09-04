# Doc Scaffold — 实例 Prompt 与预期行为

> 供回归与演示：用真实 prompt 触发 skill，对照预期行为核验工作流是否完整。

## Example 1：小工具项目建标准档

```
用户：参考 D:\Desktop\Craft\Control 的文档范式，给 F:\snippets\rename-tool 建文档结构和机制检查。
```

预期行为：
1. 判档位：`rename-tool` 是单文件脚本（模块 < 8）→ 标准档。
2. 补建：`AGENTS.md`、`PROJECT_REFERENCE.md`、`TO-TICKETS.md`、`DEV_LOG.md` + `DOCUMENTATION_STANDARDS.md`（登记表覆盖根目录全部 `.md`）。
3. 分发：`pool_cleanup_check.py` + `doc_standards_check.py` + `pre-commit.sh`/`install-hooks.bat`；不复制 `doc_sync.py`（标准档）。**门禁表可保留 doc_sync 行**——doc_standards_check 对无 CODE_WIKI.md 的项目豁免该脚本存在性，模板可原样复制。
4. 验证：两道检查 + 总表检查全绿，`sh .git/hooks/pre-commit` EXIT=0。
5. 报告：档位/差距/改动/验证/未执行（不 commit）。

## Example 2：已有完整项目补总表与门禁

```
用户：F:\Craft\model-fingerprint 已有完整档文档但没有文档规范总表，帮我按它现有结构补建总表和 pre-commit 门禁。
```

预期行为：
1. 判档位：模块 ≥ 8、文档多页、多场景引用 → 完整档；但市面上已有 `CODE_WIKI.md` + `doc_sync.py` → 直接完整档。
2. 建 `DOCUMENTATION_STANDARDS.md`（复制模板 → 改写登记表为实际 14 个文档）+ 分发 `doc_standards_check.py` + pre-commit 模板挂第三道。
3. 验证：`doc_sync.py --check` 需先刷新 tests_total 与新文件引用（新增脚本/测试后 CODE_WIKI 双向覆盖会报漂移→跑 `doc_sync.py`），三道检查全绿。
4. 报告：新建总表 + 新门禁，全量 pytest 通过，覆盖率达标。

## 负向场景（预期不做什么）

- **不碰代码**：用户只让建文档 → 不改 `src/` 逻辑。
- **不整篇重写**：用户已有 `AGENTS.md` → 只核对分工表补行，不替换全文。
- **不越权 git**：不自动 commit/push。
- **不伪造数字**：测试数/覆盖率如实核验或由 doc_sync 标记生成，不手写编造。
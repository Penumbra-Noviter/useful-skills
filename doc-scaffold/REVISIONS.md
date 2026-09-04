# Doc Scaffold 修订日志

- 2026-09-05 — dao-skill Mode D 评估（78/100 MVP，E2 干跑）+ 六项修复：
  - P1-1 `doc_standards_check.py` 门禁脚本存在性档位自适应（标准档无 CODE_WIKI.md 时豁免 `doc_sync.py` 存在性——模板门禁表可原样复制，无需按档位删行）
  - P1-2 完整档 CODE_WIKI §3 文件树必须引用分发的 `scripts/*.py`（doc_sync files 双向覆盖会要求全部 .py 被引用）
  - P2-① `doc_sync.py --check` 通过时输出「同步 OK」行（与另两道检查的可见性对齐）
  - P2-② 本文件 + SKILL.md「自身回归」命令
  - P2-③ SKILL.md「调用方与交接」声明（project-kickoff 骨架搭建步骤为编排方）
  - P2-④ `pre-commit.sh.template` python/python3 跨平台探测
  - 回归验证：标准档陷阱回归 + 完整档全链路 + 负向测试，详见 SKILL.md「自身回归」

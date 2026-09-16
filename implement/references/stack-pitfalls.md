# Implement 栈级坑（FastAPI / SQLAlchemy / Pydantic v2 / PySide6）

从个人知识库 `demo/经验/` 蒸馏的实现期反复踩坑清单。涉及对应栈时先读本节，别凭训练记忆重踩。每条给「反模式 → 正解 → 验证点」，来源见知识库同名笔记。

**维护约定（防双源漂移）**：经验本体在知识库 `demo/经验/`，本文件是面向子智能体的缓存副本，知识库为唯一权威。每次 `distill-lesson` 蒸馏新栈级坑后顺带核对本文件——新增条目或修正过时正解；冲突时以知识库为准重写。

## FastAPI

- **序列化走 `response_model`，不手写 dict**：手写 `_x_to_dict()` 与 Pydantic Schema 字段重复，新增字段漏改一处即静默不一致。正解：`response_model=<Schema>` 且 `from_attributes=True`，Schema 是字段唯一事实来源。验证点：repo 内无手写 ORM→dict 映射。（`response_model 统一驱动序列化`）
- **静态挂载顺序**：`StaticFiles(directory=…, html=True)` 挂到 `/` 会遮蔽之后注册的路由，且是静默的（不报错，请求进错分支）。正解：路由注册（含前缀）先于静态挂载，顺序写注释。验证点：`/api/*` 定义在 `mount("/")` 之前。（`FastAPI 静态挂载顺序契约`）
- **白名单归一化不删外来键**：配置文件按白名单 normalize 会静默丢弃未知键 = 数据丢失。正解：归一化时保留外来键，或对未知键显式报错而非丢弃。（`配置文件白名单归一化会静默删除外来键`）

## SQLAlchemy

- **枚举列按 `.value` 存取**：`Enum` 默认 `values_callable` 存成员名，成员名 ≠ 值时与存量 VARCHAR 错位（成员名恰好等于值时会掩盖问题）。正解：`Enum(..., values_callable=lambda e: [m.value for m in e])` 按 `.value` 落库，存量数据零迁移。约定：库里的值永远用枚举 `.value`。验证点：落库值 == 枚举 `.value`。（`DB 枚举列按值存取`）
- **跨消费者解码语义不一致**：同一 URL 字符串，SQLAlchemy sqlite 方言对 `%XX` **零解码**，而 `sqlite3.connect(uri=True)` **会解码**——双端镜像测试只印证「我编码 == 我解码」会形成盲区。正解：跨消费者（ORM vs raw driver）的字符串对齐，必须用「真实消费者能否打开/连接」的连接级用例验证。验证点：含空格/中文/`#`/`%` 路径的连接用例。（`跨语言镜像契约须对真实消费者验证`）

## Pydantic v2

- **区分「显式传参」用 `model_fields_set`**：回退链判断字段是否被显式传入，别用值比较——显式传默认值与没传的值相等，无法区分。正解：`model_fields_set` 判定「是否出现在请求里」。验证点：显式传默认值 vs 不传，两条路径可区分。（`Pydantic model_fields_set 区分显式传参`）

## PySide6 + pyqtgraph

- **整行替换用显式 block 范围，不用 `BlockUnderCursor`**：其实际选中范围是 `[block.pos - 1, block.pos + block.length - 1)`，含前块分隔符、不含本块分隔符；纯 ASCII 单行测试侥幸正常，一旦含中文/emoji（UTF-16 多 code unit）就偏移吞换行。正解：显式 `setPosition` 定范围。验证点：含中文/emoji 的多行文档用例。（`PySide6整行替换用显式block范围`）
- **主题是两套色值消费者**：QSS 接受浮点 alpha 的 `rgba()`，`pg.mkColor` 只认十六进制/SVG 名——暗色 `rgba(255,255,255,.05)` 会让打包版启动即崩；新组件漏配 QSS 选择器则某主题下隐形。正解：图表色值用 hex，QSS 用 rgba，别混用；新组件补全所有主题的 QSS。验证点：双主题各跑一次渲染。（`双主题渲染路径回归`）
- **headless 测试共享替身须弹 `sys.modules` 缓存**：共享 PySide6 替身注入后，先跑的测试把真模块缓存，后跑的测试 `import` 拿到缓存模块，`isinstance` 断言失败。正解：用 `monkeypatch.setitem(sys.modules, …)` 时靠 fixture 自动恢复，或断言统一用共享替身源，不混用文件内局部替身。验证点：共享替身 + 文件内替身不同时存在。（`GUI headless测试共享替身后必须弹出sys.modules缓存`）

## 通用

- **运行态数据与程序目录分离**：数据/配置/日志放用户数据目录（如 `Path.home()`），不与安装目录同址——打包覆盖会丢数据；空环境首启时数据目录必须先 `mkdir`（早退路径也会用到）。正解：启动即幂等确保目录存在。验证点：空目录首启不崩。（`打包覆盖丢数据` / `空环境首启即崩`）
- **仓库搬家后 venv 可编辑安装指向失效**：`pip install -e .` 的 `.pth` 仍指向旧绝对路径，导入报错。正解：搬家后重跑 `pip install -e . --no-deps`；打包脚本失败日志含 spec 行号时先查导入链。（`仓库搬家后 venv 可编辑安装指向失效`）

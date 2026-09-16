# STRIDE × FastAPI 威胁与安全需求映射

六维威胁模型，按 FastAPI + SQLAlchemy 2.x + Pydantic v2 语境给出「威胁 → 缓解（可验证需求）」。跑 Workflow 第 3 步时对照使用；每条缓解都要转成能落到 review 或 pytest 的具体断言。

## Spoofing（伪造身份）

- 威胁：JWT 被盗用、端点缺认证、会话固定。
- 缓解：用依赖注入 `Depends`/`Security` 做认证，不隐式信任裸 token；JWT 短时效 + refresh 轮换 + 吊销检查。
- 验证点：pytest 无 token 请求返回 401；伪造/过期 token 返回 401 而非 500。

## Tampering（篡改）

- 威胁：请求体篡改、SQL 注入、不安全反序列化。
- 缓解：Pydantic v2 严格校验，`ConfigDict(extra="forbid")`；SQLAlchemy 参数化查询，禁用 `text()` 拼接裸字符串；`pickle`/`yaml.load` 不用于不可信输入。
- 验证点：Falsify 轴构造注入 payload（`'; DROP TABLE ...`）返回 4xx；额外字段被拒。

## Repudiation（抵赖）

- 威胁：状态变更无审计、无法溯源。
- 缓解：写操作落审计日志（谁、何时、何操作、结果），结构化日志带 request/correlation ID。
- 验证点：review 检查每个写端点有审计记录；日志不丢 request ID。

## Information Disclosure（信息泄露）

- 威胁：报错泄露栈、越权读、密钥入代码。
- 缓解：FastAPI 全局 exception handler 返回通用错误，详情只入服务端日志；`response_model` 裁剪敏感字段；密钥走环境变量或配置，绝不入代码。
- 验证点：review 检查无 `print(token)` / 栈回显；响应序列化后不含密码哈希。

## Denial of Service（拒绝服务）

- 威胁：无节流、慢查询、正则 ReDoS。
- 缓解：每用户 rate limit；分页 + 查询超时；线性时间正则（禁灾难性回溯）。
- 验证点：并发/压测；大分页参数被限。

## Elevation of Privilege（越权）

- 威胁：IDOR、mass assignment、权限提升。
- 缓解：每个端点做归属校验（用户只能访问自己的资源）；Pydantic 模型用显式 allowlist 字段，禁止把请求体直接绑到 ORM 模型；RBAC 在 `Depends` 层判定。
- 验证点：pytest 换 ID / 换角色返回 403；请求体夹带 `is_admin` 字段被拒。

## 通用映射（OWASP 视角）

- A01 越权 → Elevation of Privilege
- A02 加密失败 → Spoofing / Tampering
- A03 注入 → Tampering
- A05 配置错误 → Information Disclosure
- A08 数据完整性 → Tampering（反序列化）

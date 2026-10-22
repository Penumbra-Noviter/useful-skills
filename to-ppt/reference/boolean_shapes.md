# Boolean Shapes（布尔运算）— scripts/boolean_path.py

`scripts/boolean_path.py` 是一个独立 CLI：读入 JSON 几何数组（rect / ellipse /
polygon，坐标对齐 PPTD bounds、原点左上），用 shapely 做布尔运算，输出可直接写入
PPTD `shapeName: "custom"` 的 SVG path 与 viewBox。用于脚本化构造圆环、缺角卡片、
中空、组合箭头等复杂/镂空形态，代替手写 SVG path。

> 有界验证参考：ppt-master（hugohe3/ppt-master，MIT）的 shape_boolean 操作集——仅作
> 五操作语义对标；本实现为自建（shapely），不包含其代码。

---

## 五操作语义

| `--op` | shapely 映射 | 语义 |
|---|---|---|
| `union` | `unary_union` | 并集：把所有几何拼成一个轮廓 |
| `combine` | `symmetric_difference` | 对称差（XOR）：`union − intersection`，重叠部分镂空 |
| `intersect` | `intersection`（逐个交集） | 交集：只保留共同区域 |
| `subtract` | `difference`（第一个减其余并集） | 差集：第一个几何减去后面所有几何 |
| `fragment` | `ops.polygonize`（先 `unary_union` 打点） | 碎片化：把重叠输入拆成互不重叠的多个区域 |

注意事项：

- `subtract` 需要 **≥2** 个几何（第一个为被减对象）。
- 其余四操作 ≥1 个几何；单几何时 `union` / `combine` / `intersect` / `fragment` 均返回该几何本身。
- 空几何数组 → 报错（exit 2）。
- 结果无剩余面积（如两相同矩形相减）→ 输出 `{"paths": [], "viewBox": [0, 0]}` 并在 stderr 告警。
- `fragment` 的输出每条 path 是一个独立碎片，可分别写入不同 shape，或拼接进同一个
  `path` 字段。

## CLI 用法

```bash
# stdin 输入
python scripts/boolean_path.py --op union < geoms.json

# 文件输入
python scripts/boolean_path.py --op subtract --input geoms.json

# 管道示例：rect + ellipse -> 圆环（combine）
echo '[{"type":"ellipse","frame":[0,0,200,200]},{"type":"ellipse","frame":[50,50,100,100]}]' \
  | python scripts/boolean_path.py --op combine
```

- `--op` 必填，取值为 `union / combine / intersect / subtract / fragment`。
- 输入：stdin 或 `--input FILE`；输出：stdout 一行 JSON。
- 错误（坏 JSON / 非法几何 / 未知 op / subtract 不足两个几何）：stderr 报错 + exit 2。
- **shapely 为 soft 依赖**：未安装时 stderr 提示
  `pip install shapely` 并 exit 3，不抛 traceback。

## 输入 JSON schema

```jsonc
[
  {"type": "rect",    "frame": [x, y, w, h]},          // 轴对齐矩形，w/h > 0
  {"type": "ellipse", "frame": [x, y, w, h]},          // 轴对齐椭圆（外接框），w/h > 0
  {"type": "polygon", "points": [[x, y], [x, y], ...]} // 多边形，≥3 点；自相交会被 make_valid 修复
]
```

- 坐标单位为 px，原点在左上（与 PPTD `bounds` 同语义）。
- 椭圆以 64 段采样多边形近似参与运算（视觉上足够光滑）。
- 非法 frame / 点 / 未知 type / 空数组 → 报错。

## 输出 schema

```jsonc
{
  "paths":   ["M...Z", "M...Z"],   // SVG path 字符串数组
  "viewBox": [w, h]                // 输出包围盒尺寸（非负，1 位小数）
}
```

- 每条 path 是**一个完整 PPTD `path` 值**：首个 `M…Z` 为外环，后续 `M…Z` 为内环（孔）。
- `viewBox` = 输出几何包围盒尺寸（已平移至原点，所有坐标落在 `[0, w] × [0, h]`）。
- 直接写入 PPTD：

```yaml
- elementId: shape-1
  elementType: shape
  bounds: [100, 100, 150, 150]
  shapeName: custom
  viewBox: [150, 150]
  path: "M100.0,50.0L100.0,0.0..."   # 来自本工具的 paths[0]（或拼接）
  fill: {type: solid, color: "$accent"}
```

> 多结果（`combine` / `fragment` / 不相交的 `union`）：`paths` 含多条，每条可直接写入
> 一个 shape；若要放进同一个 custom shape，用字符串拼接（
> `"".join(paths)` 或 `paths.join("")`）。

## 缠绕方向（镂空约定）

每个输出多边形先经 `shapely.geometry.polygon.orient(p, -1)` 重排：**外环 CW、内环 CCW**
（对齐 `reference/pptd.md` 的 custom path 镂空约定：外环 `sweep=1`、内环 `sweep=0`）。
因此「大 shape 挖孔」直接可用：外环 + 内环写在一个 path 字符串里，PowerPoint/WPS
渲染为镂空。验证方式：用 shapely 回读 path，外环 signed area 为负、内环为正。

坐标四舍五入到 **1 位小数**；极小图形（<0.1 单位）可能退化为零面积，工具会丢弃该环
并在 stderr 告警。

## 常见组合样例 path（均为本工具真实输出）

### 圆环（combine：大椭圆 − 小椭圆）

```bash
python scripts/boolean_path.py --op combine <<'EOF'
[{"type":"ellipse","frame":[0,0,200,200]},{"type":"ellipse","frame":[50,50,100,100]}]
EOF
```

```jsonc
{"paths": ["M199.5,90.2L198.1,80.5L195.7,71.0L192.4,61.7L188.2,52.9L183.1,44.4L177.3,36.6L170.7,29.3L163.4,22.7L155.6,16.9L147.1,11.8L138.3,7.6L129.0,4.3L119.5,1.9L109.8,0.5L100.0,0.0L90.2,0.5L80.5,1.9L71.0,4.3L61.7,7.6L52.9,11.8L44.4,16.9L36.6,22.7L29.3,29.3L22.7,36.6L16.9,44.4L11.8,52.9L7.6,61.7L4.3,71.0L1.9,80.5L0.5,90.2L0.0,100.0L0.5,109.8L1.9,119.5L4.3,129.0L7.6,138.3L11.8,147.1L16.9,155.6L22.7,163.4L29.3,170.7L36.6,177.3L44.4,183.1L52.9,188.2L61.7,192.4L71.0,195.7L80.5,198.1L90.2,199.5L100.0,200.0L109.8,199.5L119.5,198.1L129.0,195.7L138.3,192.4L147.1,188.2L155.6,183.1L163.4,177.3L170.7,170.7L177.3,163.4L183.1,155.6L188.2,147.1L192.4,138.3L195.7,129.0L198.1,119.5L199.5,109.8L200.0,100.0ZM149.8,104.9L149.0,109.8L147.8,114.5L146.2,119.1L144.1,123.6L141.6,127.8L138.7,131.7L135.4,135.4L131.7,138.7L127.8,141.6L123.6,144.1L119.1,146.2L114.5,147.8L109.8,149.0L104.9,149.8L100.0,150.0L95.1,149.8L90.2,149.0L85.5,147.8L80.9,146.2L76.4,144.1L72.2,141.6L68.3,138.7L64.6,135.4L61.3,131.7L58.4,127.8L55.9,123.6L53.8,119.1L52.2,114.5L51.0,109.8L50.2,104.9L50.0,100.0L50.2,95.1L51.0,90.2L52.2,85.5L53.8,80.9L55.9,76.4L58.4,72.2L61.3,68.3L64.6,64.6L68.3,61.3L72.2,58.4L76.4,55.9L80.9,53.8L85.5,52.2L90.2,51.0L95.1,50.2L100.0,50.0L104.9,50.2L109.8,51.0L114.5,52.2L119.1,53.8L123.6,55.9L127.8,58.4L131.7,61.3L135.4,64.6L138.7,68.3L141.6,72.2L144.1,76.4L146.2,80.9L147.8,85.5L149.0,90.2L149.8,95.1L150.0,100.0Z"], "viewBox": [200.0, 200.0]}
```

> 说明：椭圆参与布尔运算后边界为 64 段折线近似（面积误差 <1%）；如需更小的 path，
> 可用 `A` 弧手写整圆（参见 `reference/pptd.md` 的 custom path 圆环示例）：
> `M500,0 A500,500 0 1 1 499,0 Z M500,200 A300,300 0 1 0 499,200 Z`（viewBox `[1000,1000]`）。

### 缺角卡片（subtract：卡片 − 角上三角）

```jsonc
{"paths": ["M0.0,100.0L100.0,100.0L100.0,0.0L30.0,0.0L0.0,30.0Z"], "viewBox": [100.0, 100.0]}
```

### 中空（subtract：大矩形 − 内矩形，外环 CW + 内环 CCW 写在一个 path）

```jsonc
{"paths": ["M0.0,0.0L0.0,100.0L100.0,100.0L100.0,0.0ZM70.0,70.0L30.0,70.0L30.0,30.0L70.0,30.0Z"], "viewBox": [100.0, 100.0]}
```

### 组合箭头（union：箭杆矩形 + 箭头三角）

```jsonc
{"paths": ["M0.0,20.0L0.0,60.0L300.0,60.0L300.0,80.0L400.0,40.0L300.0,0.0L300.0,20.0Z"], "viewBox": [400.0, 80.0]}
```

### 多边形裁剪（intersect：两个重叠多边形）

```jsonc
{"paths": ["M50.0,50.0L50.0,0.0L0.0,0.0L0.0,50.0Z"], "viewBox": [50.0, 50.0]}
```

### 重叠矩形碎片化（fragment，附加示例）

```jsonc
{"paths": ["M100.0,50.0L100.0,0.0L0.0,0.0L0.0,100.0L50.0,100.0L50.0,50.0Z", "M100.0,50.0L100.0,100.0L50.0,100.0L50.0,150.0L150.0,150.0L150.0,50.0Z", "M50.0,100.0L100.0,100.0L100.0,50.0L50.0,50.0Z"], "viewBox": [150.0, 150.0]}
```

（三条 path 面积合计 = 并集面积 17500，即 A\B、B\A、A∩B 三块。）

## 依赖

- Python 3.10+（stdlib：`json` / `argparse` / `math` / `sys`）
- **shapely ≥ 2.0**（soft 依赖）：`pip install shapely`；未安装时 CLI 报错 + 安装提示。

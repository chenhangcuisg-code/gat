---
name: godot-editor-control
description: 让 AI 操控一个正在运行的 Godot 编辑器(或游戏运行时)——通过 Hastur Operation Plugin 的 broker REST API 发送 GDScript 来增删改场景节点、改属性、挂脚本、开关场景、改项目设置、运行工程。含 Python 客户端 gop.py(零三方依赖)、10 个常用操作模板、mock broker(无编辑器也能自测)、--dry-run 离线预览。Godot 4.x(4.6.2/4.7)。触发词:"操控Godot编辑器"、"让AI改Godot场景/节点"、"godot editor control"、"Hastur"、"远程执行GDScript"、"godot MCP/自动化"。
argument-hint: [想对编辑器做的操作,如 "在当前场景加个Sprite2D" / "列出场景树" / "运行工程"]
allowed-tools: Bash, Read, Write, Edit
---

# godot-editor-control — 用 AI 操控 Godot 编辑器

通过 **Hastur Operation Plugin**(rayxuln 作,Godot 4.x 远程代码执行插件)驱动**正在运行的 Godot 编辑器**:
发 GDScript 到 broker → broker 经 TCP 转给编辑器插件执行 → 回传 compile/run 结果与 outputs。

请求:$ARGUMENTS

> 架构:**本 skill(Agent)──HTTP:5302──▶ Broker(Node/Express)──TCP:5301──▶ Godot 编辑器插件**
> 插件 GitHub:https://github.com/rayxuln/hastur-operation-plugin
> ⚠️ **安全**:插件在编辑器里执行**任意 GDScript**。broker **只绑 localhost**,token 当密码,别提交/外泄。

## 环境(本机已验证)
- Python(客户端,**仅标准库**):`C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe`
- Node `v24.13.1`(跑 broker)。Godot 工程示例:`C:\Users\User\idle-engines\xiuxian-godot`(4.7)。
- 客户端/模板/测试都在本 skill 下:`scripts/` `gdscript/ops/` `references/`。

## 先决条件(一次性,见 `references/install.md`)
1. 把插件 `addons/hasturoperationgd/` 拷进 Godot 工程 → Project Settings → Plugins 启用 → dock 变绿。
2. 起 broker:`cd broker-server && npm install && npm run dev`(默认 HTTP `:5302` / TCP `:5301`),
   **记下它打印的 64 位 hex token**。
3. 配置客户端连接:工程根/家目录放 `.hastur.json`:
   ```json
   { "broker": "http://localhost:5302", "token": "<broker打印的token>", "project_name": "修仙" }
   ```
   (或用 `--broker/--token` 或环境变量 `HASTUR_BASE_URL/HASTUR_AUTH_TOKEN`。)

## 执行流程(收到一个"操控编辑器"的需求时)
1. **连通自检**:`gop.py health` → 200;`gop.py executors` → 看有没有 `type:editor` 实例、记下 `id`。
2. **选/拼操作**:
   - 命中常用操作 → 用模板:`gop.py op <name> --set k=v ...`(`op --list` 看全部)。
   - 不在模板里 → 写 GDScript:`gop.py exec --file x.gd`(或 `--code "..."`);照 `operations-cookbook.md`。
3. **先 `--dry-run`** 看将发送的 GDScript 对不对,再真发。
4. **读结果**:`compile/run` 是否 OK、`outputs` 键值;失败看 `compile_error/run_error`(退出码 0/1/2)。
5. 改了场景记得 `op save_scene`。

## 输入 / 输出
- **输入**:一句操控意图(自然语言)+(可选)目标实例/工程。
- **输出**:对编辑器的实际改动 + 客户端回显的 `compile/run/outputs`(可读结果)。

## 常用操作(`gdscript/ops/`,`op --list` 可查)
| op | 参数 | 作用 |
|---|---|---|
| `tree` | — | 打印当前编辑场景树(name [Class] (path)) |
| `open_scene` | path | 打开 res:// 场景 |
| `add_node` | type,name,parent | 加节点(自动设 owner=场景根,才存得进 .tscn) |
| `set_prop` | node,property,value | 改属性(value 是**原始 GDScript** 如 `Vector2(10,20)`) |
| `attach_script` | node,script | 挂脚本资源 |
| `instantiate_scene` | scene,parent,name | 实例化 PackedScene |
| `save_scene` | — | 保存当前场景 |
| `play` | — | 运行主场景 |
| `get_setting` / `set_setting` | key[,value] | 读/写并持久化 ProjectSettings |

例:
```bash
PY="C:/Users/User/AppData/Local/Programs/Python/Python312/python.exe"
G="C:/Users/User/.claude/skills/godot-editor-control/scripts/gop.py"
"$PY" "$G" op tree --project-name 修仙
"$PY" "$G" op add_node --set type=Sprite2D --set name=Hero --set parent=. --project-name 修仙
"$PY" "$G" op set_prop --set node=Hero --set property=position --set 'value=Vector2(120,80)' --project-name 修仙
"$PY" "$G" op save_scene --project-name 修仙
```

## 无编辑器也能跑通(自测 / 离线)
- **mock broker**(模拟 broker HTTP 契约,不真执行 GDScript):
  ```bash
  "$PY" scripts/mock_broker.py --port 5399 --token TESTTOKEN &
  "$PY" scripts/gop.py --broker http://127.0.0.1:5399 --token TESTTOKEN executors
  ```
- **`--dry-run`**:`gop.py op add_node --set ... --dry-run` 只渲染将发送的 GDScript,不连真编辑器。

## 文件清单
| 路径 | 用途 |
|---|---|
| `scripts/gop.py` | **客户端**:health/executors/exec/op,目标路由、Bearer、结果解析、退出码、--dry-run |
| `scripts/mock_broker.py` | broker 的**测试替身**(stdlib http),离线验证客户端协议 |
| `gdscript/ops/*.gd` | 10 个操作模板(整类模式、Tab 缩进、`{{token}}` 占位) |
| `gdscript/ops/manifest.json` | 模板的描述与示例参数(`op --list` 用) |
| `agents/hastur.yaml` | 连接默认值 + 操作词表 + 执行约定 |
| `references/install.md` | 装插件 + 起 broker + 配 token + 自检 |
| `references/protocol.md` | broker HTTP 契约(端点/认证/请求响应/目标路由/两模式) |
| `references/operations-cookbook.md` | Godot 4.x 编辑器操作 GDScript 配方 + 坑 |
| `examples/` | 实跑日志(对 mock broker 的成功/错误路径) |

## Definition of Done(一次操控)
- [ ] `health` 200 且 `executors` 有目标 editor 实例。
- [ ] `op`/`exec` 返回 `compile_success && run_success`,outputs 符合预期。
- [ ] 改场景后已 `save_scene`;改设置后 `set_setting` 返回 saved=OK。
- [ ] 失败时已读 `compile_error/run_error` 并据 `operations-cookbook.md` 修正(Tab 缩进、`true/null`、Error==OK、owner)。

> 关键约定:操作模板用**整类模式**(`extends` + `func execute(executeContext)`)规避片段自动包装的 Tab/空格混缩进;
> 节点务必设 `owner=场景根`;很多 API 返回 `Error` 枚举要判 `== OK`。

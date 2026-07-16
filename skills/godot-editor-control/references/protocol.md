# protocol.md — Hastur broker HTTP 契约(客户端依据)

`scripts/gop.py` 与 `scripts/mock_broker.py` 都实现这份契约。来源:rayxuln/hastur-operation-plugin
README + 其自带 `.claude/skills/godot-remote-executor/SKILL.md`。

## 端点
| 方法 | 路径 | 认证 | 用途 |
|---|---|---|---|
| GET  | `/api/health`    | 无    | 存活检查 → `{"status":"ok"}` |
| GET  | `/api/executors` | Bearer | 列出已连实例 |
| POST | `/api/execute`   | Bearer | 在目标实例执行 GDScript |

- Base URL 默认 `http://localhost:5302`(broker HTTP)。认证头:`Authorization: Bearer <token>`。
- token = broker 启动时打印的 **64 位 hex**(或 `--auth-token` 指定)。

## /api/executors 响应
```json
{ "success": true, "data": [
  { "id": "ed-0001", "type": "editor", "project_name": "…", "project_path": "…", "connected": true },
  { "id": "gm-0002", "type": "game",   "project_name": "…", "project_path": "…", "connected": true }
] }
```
- `type`:`"editor"`(可访问 EditorInterface/场景编辑/菜单)或 `"game"`(运行时场景树/物理/输入,**无** EditorInterface)。

## /api/execute 请求
```json
{
  "code": "<GDScript>",
  "executor_id": "ed-0001",        // 三选一(精确)
  "project_name": "修仙",           // 或 模糊匹配工程名
  "project_path": "…/xiuxian-godot",// 或 模糊匹配工程路径
  "type": "editor"                  // 可选,过滤 editor/game
}
```
**目标三选一**:`executor_id` > `project_name` > `project_path`。`gop.py` 的 `build_target()` 按此优先级取,
缺失则报错提示。

## /api/execute 响应
```json
{ "success": true, "data": {
  "request_id": "uuid",
  "compile_success": true,  "compile_error": "",
  "run_success": true,      "run_error": "",
  "outputs": [["key", "value"], ["key2", "value2"]]
} }
```
- `outputs` 是 `[[key, value], …]`,来自代码里 `executeContext.output(key, value)` 调用。
- `gop.py` 退出码:`0`=compile&run 都 OK;`1`=编译或运行失败/缺目标/未知 op;`2`=HTTP/认证失败。

## 执行两模式(broker 侧包装)
- **片段模式(默认,代码不含 `extends`)**:自动包进 `@tool extends RefCounted`,注入 `executeContext`。
- **整类模式(代码含 `extends`)**:你**必须**自己写 `func execute(executeContext):`。
  → 本 skill 的 `gdscript/ops/*.gd` 全部用**整类模式**(规避自动包装的 Tab/空格混缩进问题)。

## executeContext
- `output(key: String, value)`:回传结构化结果(进 `outputs`)。
- `editor_plugin`:`EditorPlugin` 引用(**仅 editor executor**;game 上为 `null`)→ `get_editor_interface()`。

## 关系图
```
gop.py ──HTTP /api/execute──▶ broker(Node/Express) ──TCP 5301──▶ Godot 插件(执行GDScript)
   ▲                                                                      │
   └──────────────── outputs / compile_error / run_error ◀────────────────┘
```

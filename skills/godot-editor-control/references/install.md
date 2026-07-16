# install.md — 安装 Hastur 插件 + 启动 broker + 连上编辑器

本 skill 通过 **Hastur Operation Plugin**(rayxuln 作)驱动**正在运行的 Godot 编辑器**。
三层架构:**Agent(本 skill)→ HTTP → Broker(Node/Express)→ TCP → Godot 编辑器插件**。
GitHub:https://github.com/rayxuln/hastur-operation-plugin · Godot **4.x**(用户环境 4.6.2,本仓库工程为 4.7,同一大版本)。

> ⚠️ 安全:该插件在你的编辑器里**执行任意 GDScript**。Broker **只绑定 localhost**,token 当密码看待,别暴露到公网。

## 0. 前置(本机已验证)
- **Node** `v24.13.1`(`C:\Program Files\nodejs`)—— broker 需要。
- **Python** `C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe` —— 本 skill 客户端只用标准库。
- 一个 Godot 4.x 工程(如 `C:\Users\User\idle-engines\xiuxian-godot`)。

## 1. 装插件进工程
```
# 把仓库的 addons/hasturoperationgd/ 拷进你的工程 addons/
<your-project>/addons/hasturoperationgd/...
```
1. 打开 Godot 工程 → **Project → Project Settings → Plugins** → 启用 **Hastur Operation GD**。
2. **Project Settings → Hastur Operation GD** 配 broker 主机/端口(默认连 `localhost:5301` TCP)。
3. 编辑器 dock 显示**绿色已连接**即成。

## 2. 起 broker
```bash
cd broker-server
npm install
npm run dev                       # 默认 HTTP :5302 / TCP :5301
# 或自定义:
npx tsx src/index.ts --http-port 5302 --tcp-port 5301 --auth-token <你的token>
```
- 不传 `--auth-token` 时,broker **启动时打印一个 64 位十六进制随机 token** 到 stdout——复制它。
- HTTP 默认 `http://localhost:5302`,TCP `5301`。

## 3. 把连接信息给本 skill 客户端
客户端 `scripts/gop.py` 按以下顺序取配置(先到先得):
1. 命令行 `--broker` / `--token`
2. 环境变量 `HASTUR_BASE_URL` / `HASTUR_AUTH_TOKEN`
3. `./.hastur.json` 或 `~/.hastur.json`:
   ```json
   {
     "broker": "http://localhost:5302",
     "token": "粘贴broker打印的64位hex",
     "project_name": "修仙放置"
   }
   ```
把 `.hastur.json` 放在工程根或家目录,之后命令就不用每次带 `--token`。
> `.hastur.json` 含 token,**别提交进 git**(加进 `.gitignore`)。

## 4. 连通性自检
```bash
PY="C:/Users/User/AppData/Local/Programs/Python/Python312/python.exe"
G="C:/Users/User/.claude/skills/godot-editor-control/scripts/gop.py"
"$PY" "$G" health                              # 期望 [HTTP 200] {"status":"ok"}
"$PY" "$G" executors                           # 列出已连的 editor/game 实例(看 id/type/project_name)
"$PY" "$G" op tree --project-name 修仙          # 打印当前编辑场景树
```
拿到 `executors` 里的 `id` 后,后续可用 `--executor-id <id>` 精确指向某个实例。

## 5. 无编辑器也能开发/自测(mock broker)
没开 Godot 时,用内置 mock 跑通客户端协议(不真执行 GDScript,仅模拟响应):
```bash
"$PY" scripts/mock_broker.py --port 5399 --token TESTTOKEN &     # 起 mock
"$PY" scripts/gop.py --broker http://127.0.0.1:5399 --token TESTTOKEN executors
"$PY" scripts/gop.py op add_node --set type=Sprite2D --set name=Hero --set parent=. --dry-run  # 离线看生成的GDScript
```

## 常见问题
- **连不上 broker**:确认 `npm run dev` 在跑、端口对、token 对;`health` 不需要 token,先测它。
- **executors 为空**:Godot 里插件没启用/没连上 broker(看 dock 是否绿)。
- **401 unauthorized**:token 错;重新复制 broker 启动时打印的那串。
- **HTTP 504 超时**:game executor 命中断点(开 **Ignore Error Breaks**),或代码确实慢。
- **编译报错像 Python**:GDScript 用 `func`/`true`/`false`/`null`、**Tab 缩进**,见 `operations-cookbook.md`。

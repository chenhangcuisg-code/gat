# 技能特效生成调研 + 实现报告：以「剑波 (jianbo / sword-energy slash)」为例

**日期**: 2026-07-02
**目标**: 用 AI 端到端生成 2D 游戏**技能特效**动画素材（不是角色 sprite），以剑波（剑气/energy-slash）为具体例子，给出多条可落地流程并实跑。
**算力**: 单台 A100-80GB（`chenhang@210.45.70.34`），HuggingFace 被墙 → 全程走 `hf-mirror.com`，无 sudo/Docker。
**所有模型均为本地已缓存**（FLUX.1-schnell / AnimateDiff motion-adapter / SDXL / SDXL-VAE），P1 额外拉了 DreamShaper-8。

---

## 0. 名词与符号约定（自包含，勿假设读者记得旧定义）

| 符号/术语 | 含义 |
|---|---|
| **剑波 / jianbo** | 动作/修仙游戏里角色挥剑放出的**能量弧刃**（月牙形光波），飞行→放大→消散。本报告的生成目标物。 |
| **VFX** | Visual Effects，游戏特效（火焰/闪电/能量/斩击等），区别于角色立绘。 |
| **luminance key（亮度抠像）** | 本报告全流程的**核心技巧**。特效渲染在**纯黑背景**上，然后令每个像素 `alpha = 感知亮度`（`0.299R+0.587G+0.114B`，再做 gamma/boost 微调）。黑色→透明，亮处→保留。这是游戏特效行业标准做法（见调研 §2）。 |
| **additive blending（加色混合）** | 引擎里特效常用的混合模式：`结果 = 背景 + 特效RGB`。纯黑天然隐身、亮处发光，无需 alpha、无需深度排序。本报告产出的黑底帧可直接用加色，或用亮度抠像后的 RGBA 用普通 alpha 混合。 |
| **sprite sheet（精灵表）** | 把动画所有帧拼成一张网格大图，引擎按格切帧播放。本报告每条流程都产出 `*_sheet.png`。 |
| **.tres** | Godot 4 的 `SpriteFrames` 资源文件，引用逐帧 PNG，带 `speed`(fps)/`loop`。拖进 `AnimatedSprite2D` 即可播放。 |
| **strength (img2img)** | 扩散重绘强度 ∈[0,1]。越高越偏离输入图、越"重画"；越低越保留输入布局。P3 用 0.62。 |
| **guidance_scale (CFG)** | 提示词引导强度，越高越贴 prompt。 |
| **num_frames / N** | 一段动画的帧数。P1=16, P2=18, P3=14。 |

---

## 1. 三条流程（三种不同范式）—— 都已实跑

| | 流程 | 运动来源 | 画面来源 | 定位 | 每段耗时(A100) |
|---|---|---|---|---|---|
| **P1** | AnimateDiff txt2vid | 100% AI（motion 模块自己生成运动） | AI，逐帧 | "描述→模型自己动起来"，最省事、可训 LoRA | ~10s（+首次下载底模） |
| **P2** | FLUX 贴图 + 程序化运动 | 100% 代码（确定性） | AI 生成 1 张贴图 | **生产级**：完全可控、完美循环、可调参 | ~5s |
| **P3** | SDXL 受控 img2img | 程序化 init 轨迹（可控） | AI，逐帧重画 | 混合：既要引擎级可控轨迹，又要 AI 质感 | ~40s（14 帧逐帧扩散） |

### 各流程方法细节（怎么算/用什么数据/什么口径）

**P1 — AnimateDiff txt2vid**（脚本 `p1b_animatediff.py`）
- 底模 `Lykon/dreamshaper-8`（通用 SD1.5，擅长奇幻/动漫）+ 运动模块 `guoyww/animatediff-motion-adapter-v1-5-2`。
- 提示词采用调研确认的社区 VFX 写法：`"...crescent sword energy slash wave..., effect, 2d style, anime, pure solid black background, no character"`；负面词排除角色/风景/灰底。
- `num_frames=16, guidance_scale=8.5, steps=28, DDIM`。输出 16 帧黑底 → 亮度抠像 → 透明帧 + sheet + gif + tres。
- ⚠️ **踩坑（口径重要）**：第一版用 `kohbanye/pixel-art-style` 做底模 → 输出一团青橙色云雾状 blob、无视黑底（像素底模把"black background"理解成风景）。**结论：AnimateDiff 做特效必须用通用底模 + effect 提示词，不能用像素专用底模。** 故换 DreamShaper-8 重跑（本报告最终版）。

**P2 — FLUX 贴图 + 程序化运动**（脚本 `p2_flux_procedural.py`）
- 第一步 `FLUX.1-schnell`（4 步、CFG=0）生成**1 张**月牙剑波贴图（纯黑底，见 `p2_texture.png`）。
- 第二步纯 CPU/PIL 程序化动画（确定性，`seed=7`）：
  - 包络 envelope：前 12% 淡入，中段满值，后 45% 淡出；
  - `scale` 0.55→1.25 随时间放大；`dx` 从 -0.28W 扫到 +0.32W（左→右）；`ang` 正弦轻微摆弧；
  - **拖影 after-image**：3 层滞后副本（lag 0.045/0.09/0.14，亮度 0.5/0.28/0.15）做运动模糊；
  - **前缘火花**：leading edge 处按帧撒 ~9 个高斯抖动亮点。
  - 加色叠加所有层 → clip → 亮度抠像。
- 18 帧。**优点：完全确定性、可任意调飞行方向/速度/颜色、天然可循环、体积极小。**

**P3 — SDXL 受控 img2img**（脚本 `p3_sdxl_ctrl.py`）
- 每帧先程序化画一条**引导 init**：随 `p∈[0,1]` 位置右移、半径 110→230 放大的青白月牙弧（`PIL.ImageDraw.arc` + 高斯模糊），见 `p3_init_XX.png`。
- 再用 `SDXL-base-1.0`（+ `sdxl-vae-fp16-fix`）img2img 重画：`strength=0.62, CFG=6.5, steps=18`，**全帧同一 seed=123** 保证风格稳定，运动由 init 轨迹提供 → 时序连贯 + AI 质感。
- 末段乘 envelope 淡出。14 帧 → 亮度抠像。
- **本质**：用程序化 init 当"穷人版 ControlNet"，兼得引擎级可控运动 + 逐帧 AI 纹理。

### 统一后处理（`vfx_util.py`，三条流程共用）
`luminance_key(gamma=0.85, boost=1.15)` 黑底→RGBA透明 · `save_sheet` 拼精灵表 · `save_gif`(叠深灰底预览发光) · `save_tres`(Godot SpriteFrames, P1/P3=12fps, P2=16fps)。

---

## 2. 调研结论（2024–2026 SOTA，自研单卡口径）

由子智能体 web 调研（DuckDuckGo/官方文档），核心结论：

1. **亮度抠像 + 黑底 + 加色 = 全行业标准**，也是 AI-VFX 社区标准做法（最热特效 LoRA 的推荐提示词就是 `effect, 2d style, anime, black background`）。精修点：用**预乘 alpha (premultiplied)** 防黑边、`alpha=max(R,G,B)` 或加权亮度、软阈值+轻微腐蚀去杂散暗点。
2. **五条可行技术路线，按单卡实用性排序**：
   - ★ **Route 1 = AnimateDiff(SD1.5)+特效LoRA+黑底+亮度抠像** —— 最轻最快、LoRA 生态最丰富、可用自己的剑气样本几分钟训一个 LoRA。**= 本报告 P1。** ≈13GB 显存。
   - ★ **Route 2 = Wan-Alpha (CVPR'26)** —— **原生 RGBA 真透明**（`WeChatCV/Wan-Alpha`，14B），边缘半透明最干净、免抠像；但需 ~80GB/量化、下载大、慢，属"英雄级特效"质量档，本次未跑（留作升级项）。
   - ★ Route 3 = LTX-Video —— 最轻的 DiT 视频模型，适合高吞吐 + I2V 关键帧补间。
   - Route 4 = CogVideoX-5B —— Apache-2.0、运动连贯，较重。
   - Route 5 = ToonCrafter / **Practical-RIFE(`hzwer`)** —— 关键帧插帧补光滑到 60fps（RIFE 最易 pip 安装、A100 上开销可忽略）。
3. **无成熟的一键"文本→透明特效精灵表(剑气)"本地仓库**；所有自研方案都是`视频扩散模型 + 黑底特效LoRA + 亮度抠像 + RIFE + 打包`拼装。最接近的现成项目 SpriteBrew(`GAlbanese09/spritebrew`) 依赖 Retro Diffusion 的付费 API。

**本报告落地对应关系**：P1=Route 1（已实跑）；P2/P3=在缺特效 LoRA 时用「FLUX/SDXL 生成特效纹理 + 程序化/受控运动」补位，反而拿到更可控、更干净的结果；Route 2(Wan-Alpha)/RIFE 补间列为下一步升级。

---

## 3. 结果与判定

| 流程 | 结果 | 判定 |
|---|---|---|
| **P2 FLUX+程序化** | 干净青色月牙剑波，带拖影+火花，扫屏放大消散，透明。 | 🏆 **最佳**：生产级、可控、可循环、体积小。 |
| **P3 SDXL 受控** | 干净发光弧刃，严格跟随可控轨迹，逐帧 AI 重画。 | ✅ **良好**：比 P2 简洁（单弧、无拖影），胜在"引擎可控轨迹 + AI 逐帧质感"。 |
| **P1 AnimateDiff** | 换 DreamShaper-8 后：干净的**青色放射状能量爆发**（rays from center），纯黑底、发光正确。 | ✅ **可用但走偏**：是合格 VFX（适合蓄力/命中/爆发），但 txt2vid 自行收敛成**对称放射爆发**，没给出**方向性月牙剑波**。 |

**关键发现（txt2vid 的控制代价）**：纯 AnimateDiff txt2vid 给你"免费的运动"，但**无法控制特效轮廓/方向**——即使 prompt 明确要"横向月牙斩击扫屏"，模型仍收敛到最省事的对称放射爆发。要拿到指定的方向性剑波，要么 (a) 用 P2/P3 的程序化/受控轨迹，要么 (b) 给 AnimateDiff 喂一张月牙关键帧走 I2V/img2video，或训一个剑气 effect-LoRA。**这正是本对比最有价值的结论：可控性 P2≈P3 > P1，惊艳度/免手工 P1 有其位置。**

---

## 4. 交付物（本目录 `vfx_jianbo/`）

```
vfx_compare.png              三行对比图 (P1/P2/P3 各 6 帧采样, 深灰底)
p2_texture.png               FLUX 生成的剑波原始贴图 (纯黑底)
p1_preview.gif p2_preview.gif p3_preview.gif   三条流程动图 (深灰底预览发光)
p1_sheet.png  p2_sheet.png  p3_sheet.png        三张精灵表 (透明)
godot_package/vfx/p2/  p3/   逐帧透明 PNG + *_jianbo.tres (拖进 Godot AnimatedSprite2D 即用)
```
**Godot 用法**：把 `godot_package/vfx/` 放到项目 `res://vfx/`，新建 `AnimatedSprite2D`，Sprite Frames 加载 `pX_jianbo.tres`，材质设 CanvasItemMaterial→Blend Mode=Add（加色发光）即可。

## 6. A — 无背景（透明）：已实现并验证

**结论：所有帧本就是真透明 RGBA（黑底 luminance-key 得到 alpha），预览 GIF 里的深灰只是为看清发光而临时垫的画布，不是素材背景。**

验证图 `transparency_demo.png`（剑波/火球/冰霜 各取最亮帧）三列：
- **checkerboard (alpha)**：棋盘格从透明区**透出来** → 证明确实无背景。
- **game scene (alpha-blend)**：贴到紫蓝游戏场景上普通 alpha 混合，无黑框。
- **game scene (ADDITIVE glow)**：加色混合，发光更亮、无暗边（能量特效推荐用这个）。

动图证据 `jianbo_on_scene.gif`：剑波以加色叠在场景上飞过，无背景残留。
**升级项（更干净的半透明边缘）**：Wan-Alpha 等原生 RGBA 视频模型可免抠像直出真 alpha，属英雄级质量档。

## 7. B — 其他技能特效库（8 种，已实跑）

同一套「FLUX 黑底贴图 + 参数化运动 archetype」流程，一键扩到多种技能（`vfx_batch.py`），外加 2 种走 AnimateDiff（txt2vid 擅长的混沌火焰）。总览 `batch_compare.png`，逐效果 `effects/<name>_preview.gif` + Godot 包 `godot_package/vfx/batch/<name>/`。

| 效果 | 中文 | 运动 archetype | 颜色 | 生成路线 |
|---|---|---|---|---|
| fireball | 火球 | projectile（飞行+拖影+火花） | 橙黄 | FLUX+程序化 |
| lightning | 闪电 | bolt（strobe 闪烁+抖动） | 紫白 | FLUX+程序化 |
| frost_nova | 冰霜nova | burst（放射膨胀+淡出） | 青白 | FLUX+程序化 |
| heal_aura | 治疗光环 | aura（脉冲缩放+旋转，**完美循环**） | 绿金 | FLUX+程序化 |
| explosion | 爆炸 | burst | 橙红 | FLUX+程序化 |
| arcane_circle | 法阵 | spin（整圈旋转，**完美循环**） | 青金 | FLUX+程序化 |
| adiff_explosion | 爆炸 | txt2vid 自由运动 | 橙红 | AnimateDiff |
| adiff_flame_swirl | 火焰漩涡 | txt2vid 自由运动 | 橙黄 | AnimateDiff |

**运动 archetype 定义（`vfx_batch.py: animate()`）**：
- `projectile`：dx 从 -0.32W 扫到 +0.32W，2 层拖影(lag .06/.12)，前缘火花；
- `burst`：scale 0.25→1.75 (ease-out)，早期闪光后淡出，向外碎屑；
- `bolt`：不位移，亮度 strobe `0.35+0.65|sin(3.5πp)|`+随机，水平抖动；
- `aura`：scale `1+0.13sin(2πp)` 脉冲 + 旋转 360°p + 上升粒子（sin 周期→无缝循环）；
- `spin`：旋转 360°p + 轻微 scale/亮度脉冲（无缝循环）。
**口径**：FLUX 每效果只出 1 张贴图（4 步、CFG=0、对应 seed），运动全程序化确定性；AnimateDiff 版 `num_frames=16, CFG=8.5, steps=28, DreamShaper-8`。

## 8. 画风切换 — 国风水墨简笔 (sumi-e / ink-wash)

**核心：水墨与发光特效的透明逻辑相反，必须换 key。**

| | 能量特效 (§1-7) | 水墨简笔 (本节) |
|---|---|---|
| 生成底色 | 纯黑底 | **纯白宣纸底** |
| 内容 | 亮色发光 | **暗色墨迹** |
| 抠像 | `luminance_key`：alpha = **亮度** | `ink_key`：alpha = **暗度** `(1-lum)`，floor 去纸底、固定墨色 `INK=(28,26,34)` |
| 引擎混合 | **Additive 加色** | **普通 alpha-blend**（墨压在浅色场景上） |
| 运动合成 | 黑底上 numpy 加色叠加 | **透明 RGBA 上 `Image.alpha_composite` over-合成**（墨叠墨变浓不变亮） |
| 预览垫底 | 深灰 | **米色宣纸 `PAPER=(238,232,216)`** |

**5 种水墨特效（`vfx_ink.py` + `vfx_ink_adiff.py`，总览 `ink_compare.png`）**：

| 效果 | 中文 | archetype | 路线 |
|---|---|---|---|
| ink_jianbo | 剑波（月牙笔触+飞溅） | projectile | FLUX+程序化 |
| ink_burst | 墨爆（墨点向外炸开+淡出成灰） | burst | FLUX+程序化 |
| ink_enso | 圆相（禅圆残缺笔环，**无缝旋转循环**） | spin | FLUX+程序化 |
| ink_diffuse | 墨扩散（水中墨迹晕开的有机流动） | txt2vid | AnimateDiff |
| ink_dragon | 墨龙（笔触盘旋成中国龙） | txt2vid | AnimateDiff |

**提示词口径**：`traditional chinese ink wash painting sumi-e, xieyi, bold black ink brush stroke, splash, minimalist, few strokes, on white rice paper, monochrome, no color`。FLUX 对"white rice paper"响应良好（不像 pixel-art token 被忽略）。**发现**：AnimateDiff(DreamShaper) 画有机墨流（扩散/龙）极出彩——水墨的晕染/盘旋正是 txt2vid 的强项。
**透明验证**：`ink_compare.png` 全部合成在米色宣纸上、无黑框，即证 ink_key 透明成立（墨不透、纸透）；真 RGBA 可压任意浅色游戏场景。
Godot 包 `godot_package/vfx/ink/<name>/`（墨迹为暗色→材质用普通 Blend，勿用 Add）。

## 9. 国风水墨风（RICH 发光版，最终采用）

用户反馈：§8 的水墨简笔太稀疏/平。**改回 §1-7 的发光管线**（黑底→`luminance_key`(alpha=亮度)→**additive 加色发光**），**去掉「简笔/极简」约束**，做**富有细节的发光水墨**——即「发光的水墨」：白/银流动墨迹在黑底上发光 + 青玉/金点缀。

**与 §8 简笔水墨的区别（本质是"墨发光 vs 墨压纸"）**：

| | §8 简笔水墨 | §9 发光水墨（本节, 采用） |
|---|---|---|
| 生成 | 白纸底 + 暗墨 | **黑底 + 发光亮墨** |
| 抠像 | `ink_key` alpha=暗度 | **`luminance_key` alpha=亮度** |
| 混合 | 普通 alpha-blend | **Additive 加色** |
| 观感 | 平、稀疏、书法 | **发光、层次丰富、有能量感** |
| prompt | minimalist/few strokes | **richly detailed/intricate**，负面词加 minimalist/sparse/flat 排除 |

**5 种发光水墨特效（`vfx_inkglow.py`+`vfx_inkglow_adiff.py`，总览 `inkglow_compare.png`）**：

| 效果 | 中文 | archetype | 路线 | 观感 |
|---|---|---|---|---|
| ink_jianbo | 剑波 | projectile | FLUX+程序化 | 发光白墨月牙笔触+飞溅,扫屏 |
| ink_burst | 墨爆 | burst | FLUX+程序化 | 白金墨点炸开放射 |
| ink_halo | 光环 | spin | FLUX+程序化 | 青玉发光墨环旋转,无缝循环 |
| ink_dragon | 墨龙🐉 | txt2vid | AnimateDiff | **玉+金发光墨龙翻腾**(最惊艳) |
| ink_swirl | 墨漩 | txt2vid | AnimateDiff | 青色发光墨漩涡 |

**提示词口径**：`glowing luminous flowing ink, white silver ink with jade cyan / gold glow, richly detailed intricate chinese ink wash energy, pure solid black background`；负面排除 `flat, minimalist, sparse, simple, plain white background`。Godot 包 `godot_package/vfx/inkglow/<name>/`（发光→材质 **Blend Mode=Add**，同 §1-7）。**结论**：这版兼得发光质感 + 国风水墨韵，墨龙/墨漩证明 AnimateDiff 画有机发光墨流最出彩。

## 5. 数据来源 / 流水线（可追溯）
- 生成脚本：A100 `/data/chenhang/pixgen_work/vfx/{p1b,p2,p3}_*.py` + `vfx_util.py` + `run_all.sh`；日志 `run.log`/`p1b.log`。
- 本地脚本副本：`scratchpad/{vfx_util,p1_animatediff,p1b_animatediff,p2_flux_procedural,p3_sdxl_ctrl,compare_vfx}.py`。
- 模型：FLUX.1-schnell / guoyww-animatediff-motion-adapter-v1-5-2 / SDXL-base-1.0 / sdxl-vae-fp16-fix / Lykon-dreamshaper-8（均经 hf-mirror.com）。

# Desktop Pet — 一只住在你桌面上的像素史莱姆

> 它不是工具，不是助手，只是一个需要你照顾的小家伙。

**Desktop Pet** 是一个 macOS 桌面养成游戏，用像素复古画风重现了拓麻歌子和数码暴龙机的童年回忆。一只小小的史莱姆住在你的桌面上，会饿、会困、会开心、会难过，在你敲代码的间隙陪着你慢慢长大。

---

## 下载安装

**[下载最新版 (v1.0.0)](https://github.com/nh1571/desktop-pet/releases/latest)**

1. 下载 `Desktop-Pet-macOS.dmg`
2. 双击打开，把 `Desktop Pet` 拖入 `Applications`
3. 首次打开：右键 → 打开（未签名开发者）
4. 史莱姆出现在右下角，这样就完成啦

> 需要 macOS 10.13+（Intel 或 Apple Silicon）

---

## 为什么你需要一只桌面宠物？

它**不会打扰你**。没有弹窗、没有通知红点、没有每日签到。它就安静地待在屏幕角落，偶尔走动两步，偶尔打个瞌睡。你忙的时候它自己玩，你想找它的时候右键点一下就行。

它**有自己的故事**。从一颗刚孵化的史莱姆宝宝，到会追问存在主义问题的叛逆少年，再到会分享人生哲理的成年史莱姆——它会在不同的成长阶段触发不同的剧情对话，一共有 15 段。

它**永远不会死**。需求降到零也只是看起来有点委屈，喂两下就活蹦乱跳了。不会用死亡惩罚你。

---

## 快速开始（开发者）

```bash
# 环境要求：Python 3.10+、pygame 2.5+
pip install pygame
git clone https://github.com/nh1571/desktop-pet.git
cd desktop-pet
python3 main.py
```

启动后，一只绿色的史莱姆宝宝就会出现在屏幕右下角。

**测试模式：** 想快速体验成长和剧情？

```bash
python3 main.py --fast    # 60倍速，1分钟 = 1小时
```

**打包为 .app：**

```bash
./make_dmg.sh    # 生成 dist/Desktop-Pet-macOS.dmg
```

---

## 操作指南

| 操作 | 方式 |
|------|------|
| 移动宠物 | 左键拖拽 |
| 打开菜单 | 右键点击宠物 |
| 喂食 | 菜单选 Feed / 按 `F` |
| 玩耍 | 菜单选 Play / 按 `P` |
| 聊天 | 菜单选 Talk / 按 `T` |
| 睡觉 | 菜单选 Sleep / 按 `S` |
| 查看状态 | 菜单选 Status |
| 窗口置顶 | 菜单选 Toggle Always-on-Top |
| 退出 | 按 `Q` / `Esc` / 菜单 Quit |

---

## 游戏系统

### 成长阶段

| 阶段 | 在线时长 | 特点 |
|------|---------|------|
| 宝宝 (Baby) | 0 ~ 2 小时 | 圆滚滚的史莱姆宝宝，只会咕噜叫 |
| 幼年 (Child) | 2 ~ 8 小时 | 长出小角，开始好奇周围的一切 |
| 少年 (Teen) | 8 ~ 24 小时 | 更清晰的形态，开始思考人生 |
| 成年 (Adult) | 24 小时以上 | 完整的史莱姆形态，充满智慧 |

### 需求系统

史莱姆有三个需求值，按真实时间自然衰减：

- **饥饿度 (Hunger)** — 饿了就喂它
- **快乐度 (Happiness)** — 陪它玩会让它开心
- **精力值 (Energy)** — 困了它会自己睡觉，也可以哄它睡

需求低于阈值会触发不同的行为状态（饿肚子的样子、伤心的表情等）。

### 行为状态机

```
IDLE → WALKING → [随机散步]
IDLE → SLEEPING → [精力不足自动入睡]
IDLE → SAD → [快乐度过低]
FEED → EATING → HAPPY → IDLE
PLAY → PLAYING → HAPPY → IDLE
TALK → HAPPY → IDLE
```

### 存档系统

自动保存到 `~/.desktop_pet/save.json`，每 5 分钟存一次，退出时也会保存。离线时间会按比例计算需求衰减——你休假一周回来，史莱姆会非常饿和难过，但喂几次就好了。

---

## 技术细节

```
desktop_pet/
├── main.py              # 主循环、窗口管理、输入处理
├── config.py            # 全局常量、Q版矢量调色板、参数
├── vector_renderer.py   # Q版矢量史莱姆绘制引擎（抗锯齿几何绘制）
├── vector_animation.py  # 关键帧动画系统（7种动画 + 缓动插值）
├── pet.py               # 核心 Pet 类（整合全部子系统）
├── state_machine.py     # 8 种行为状态 + 转换逻辑
├── needs.py             # 需求衰减 + 阈值判断
├── event_system.py      # 15 个剧情事件 + 触发条件
├── dialog.py            # 气泡式对话 UI（打字机效果）
├── context_menu.py      # pygame 原生右键菜单
├── window_manager.py    # SDL2 窗口控制（置顶、透明度、边框）
├── audio.py             # 8-bit 程序化音效生成
├── save_manager.py      # JSON 持久化 + 离线衰减计算
├── particles.py         # 光滑圆形粒子特效
├── make_dmg.sh          # macOS 安装包一键构建
└── generate_icon.py     # 应用图标生成
```

- **纯 Python**，零外部图片/音频资源文件
- **256x256** Q版矢量渲染，30 FPS
- 精灵通过 `pygame.gfxdraw` 几何绘制 + 抗锯齿
- 动画通过关键帧 + 缓动函数插值
- 音效通过程序化合成（sine/白噪音/扫频）
- SDL2 无边框窗口实现桌面贴附效果

---

## License

MIT — 随便 fork、修改、分发，开心就好。

# 十月更新：回放、音乐与建造兼容

> LetSeries  |  2026/10/23

过去一个月，我们把三块新的拼图放进了 LetSeries：一个把 CoreProtect 历史搬回游戏的回放工具，一个服务端插件加 Fabric Mod 的音乐系统，以及一个专门伺候 Litematica 的兼容层。同时，已有插件也各自往前走了一段。

这篇文章按项目讲清楚它们解决什么问题、怎么实现，以及升级时要注意什么。

## LetMeLook：把 CoreProtect 的历史搬回游戏

查熊、复盘建筑被破坏的过程，通常靠 `/co i` 一条条翻记录：能查到，但不直观。**LetMeLook** 想做的事很直接——在游戏里把一段时间内的方块变化「重放」出来。

它由两部分组成：

- **服务端**：Purpur 1.21.11 + CoreProtect CE 24.x，负责鉴权、限流、调用 CoreProtect 的 `blockLookup`，把时间线分页发给客户端；
- **客户端**：Fabric 1.21.11 Mod，负责接收时间线，用半透明「幽灵方块」渲染出来；
- **协议**：两边共用 `letmelook-common`，通过 `letmelook:lookup` 插件消息通道通信。

### 一次查询，而不是几千次查询

如果按方块逐个查 CoreProtect，大区域会直接把数据库打满。LetMeLook 的做法是围绕选区做一次立方体批量扫描：先用球形包络粗筛，再在 Java 侧按长方体精确裁剪，每条记录都带正确的 `from` / `to` 与放置、破坏方向。

传输上按字节预算分页（`limits.page-bytes`，默认 64 KiB）：小页面保持纯 JSON，超过 32 KiB 自动 gzip，并用魔数头让客户端自动识别，旧版协议的客户端仍能读懂小页面。服务端还有体积上限、冷却与权限 `letmelook.use` 兜底。

### 客户端：幽灵方块与延时摄影

客户端用 `/lm pos1`、`/lm pos2` 框选区域，`/lm lookup <秒> [玩家]` 拉取历史。时间线按时间排序后进入播放头，支持回放、回滚、差异三种查看模式——都只作用于客户端渲染，不会改动服务器世界。

幽灵方块以绿色表示放置、红色表示破坏，每帧最多渲染 4096 个盒子；配合 `/lm time` 时间滑块、`/lm cam add|play` 相机路径，以及 `/lm export <fps> <秒>` 导出帧序列和 ffmpeg 脚本，可以直接做延时摄影。

```text
/lm pos1 / pos2          选择长方体两角
/lm lookup 3600 Steve    回放 Steve 最近一小时
/lm time                 打开时间滑块
/lm mode replay|rollback|diff
/lm cam add (两次以上) → /lm cam play
/lm export 30 20         30fps × 20 秒，导出后用 make-timelapse.sh 合成
```

这是一个研究项目，目前只针对 1.21.11（Purpur 服务端 + Fabric 客户端），第一次 Gradle 构建需要联网下载 loom 与 mappings。仓库：[LetSeries/LetMeLook](https://github.com/LetSeries/LetMeLook)。

## PlayMusic：音乐要服务端和客户端一起做

原版 Minecraft 没有播放任意音频的能力。用资源包塞歌，体积和版权都不现实；只靠服务端发包，歌词和进度又很难做得顺滑。**PlayMusic** 因此拆成两半：服务端插件负责解析、转码与状态，Fabric Mod 负责原生播放与界面。

服务端支持 Minecraft 1.18.2 ~ 1.21.11（Paper / Folia / Purpur，Java 21+），功能包括：

- 搜索并播放网易云歌曲、按 ID 直接播放、实时歌词、私人 FM；
- 播放 B 站视频音轨（DASH AAC，需要 FFmpeg 转码）；
- 播放 / 暂停 / 切歌 / 音量，以及顺序、列表循环、随机、单曲循环；
- 网易云不可用时自动回退 QQ 音乐。

客户端 Mod 覆盖 1.18.2 ~ 26.2 共 25 个版本。装了 Mod 的玩家用 `/pm gui` 打开原生控制面板；没装 Mod 也能玩，插件会提供功能完整的箱子 GUI，只是歌词与进度体验略差。26.x 客户端暂不支持原生 GUI，会自动回退到箱子 GUI，同时兼容 [ZMusic](https://github.com/RealHeart/ZMusic) 客户端协议。

需要注意，音乐数据不来自插件本体，而是三个外部服务：

| 服务 | 用途 | 是否必需 |
| :--- | :--- | :---: |
| NeteaseCloudMusicApi | 网易云搜索与播放地址，默认 `localhost:4111` | 网易云功能必需 |
| FFmpeg | B 站音频转码 | 用 `/pm bili` 时必需 |
| QQMusicApi | 网易云失败后的回退 | 可选 |

```text
/pm play <歌名|ID>    搜索并播放
/pm bili <BV号|链接>  播放 B 站音轨
/pm gui               打开音乐控制面板
/pm volume <0-100>    调整音量
/pm search <关键词>   只搜索不播放
/pm request <歌名>    点歌
```

当前发布 `build-1`，仓库：[LetSeries/PlayMusic](https://github.com/LetSeries/PlayMusic)。

## Servux-paper：让 Litematica 在 Paper 上轻松放置

Litematica 的「轻松放置」（Easy Place）依赖 Servux 协议：客户端先要知道服务端支持它，才会把放置操作按 v3 协议发过来。Paper 本身不提供这层能力，**Servux-paper** 补上的就是握手的最后一公里。

插件做三件事：

1. 注册 `servux:litematics` 通道，回应 metadata 请求，并在玩家进服后主动重发几次，避免 AUTO 模式识别不到；
2. 解码 Easy Place v3 放置包，在 Bukkit 正常放置方块后修正方块状态；
3. 用并发计数器、异步维护线程和线程安全的方块属性缓存，降低大量玩家同时放置时的锁竞争。

它只做放置兼容：不粘贴原理图、不接收上传、不还原容器物品或方块实体 NBT，也不同步 MiniHUD 数据。目标环境是 Paper / Folia `26.1.x` + **Java 25**，需要包含 26.1.2 支持的 ProtocolLib 构建（官方 ProtocolLib 5.4.0 还不支持，构建使用上游开发版）。

```text
/servuxpaper status    查看 metadata 收发与 v3 放置统计
/servuxpaper resend    重新发送握手
```

另外它支持 PlugMan 热卸载与重载时的显式清理，调整配置或热重载时不必反复重启服务器。当前发布 `0.2.4`，仓库：[LetSeries/Servux-paper](https://github.com/LetSeries/Servux-paper)。

## 现有项目也没停下

| 项目 | 版本 | 这一轮的变化 |
| :--- | :--- | :--- |
| [LetMeDo](https://github.com/LetSeries/LetMeDo) | 开发中 | 内置 `/rtp` 随机传送、`/warp` 传送点、`/trade` 面对面交易，模块可在配置里独立开关 |
| [LetMeSee](https://github.com/LetSeries/LetMeSee) | `v1.1.2-37` | 新增 `/lms inv`、`/lms ec` 查看玩家背包与末影箱，Spigot 同步直读，审计日志与自动刷新 |
| [LetMeAsk](https://github.com/LetSeries/LetMeAsk) | `2.0.0` | 物品奖励、答对 Title 与音效、中英文切换、防脚本刷屏踢出、排行榜定时广播 |
| [HumanVerify](https://github.com/LetSeries/HumanVerify) | `v1.3.5-b40` | 验证模式扩到 12 种，验证期间冻结操作，失败可重开或踢出，连续失败自动加难度 |
| [Server-AI](https://github.com/LetSeries/Server-AI) | `1.0.5` | AI 回答支持 Markdown 渲染，`/ask reload` 热重载 |
| [LetMePaytaxes](https://github.com/LetSeries/LetMePaytaxes) | 早期 | 税务系统仍在起步阶段，接口与玩法尚未定型 |

## 升级前值得看一眼

- **LetMeSee / LetMeAsk / HumanVerify** 都新增了配置项，升级后先备份旧配置，让插件补全默认值再逐项调整；
- **Servux-paper** 必须使用 Java 25，且 ProtocolLib 要换成支持 26.1.2 的构建，否则握手不会生效；
- **PlayMusic** 记得先部署 NeteaseCloudMusicApi；没有 FFmpeg 时只有 `/pm bili` 不可用；
- **LetMeLook** 目前只支持 Purpur 1.21.11 + Fabric 1.21.11，且需要 CoreProtect 正在记录数据。

完整的项目列表与构建方式，可以看组织主页的 [README](https://github.com/LetSeries) 或官网的[快速上手](https://letseries.github.io/#quickstart)。如果这些工具帮到了你的服务器，欢迎在仓库里提 Issue 或 PR。

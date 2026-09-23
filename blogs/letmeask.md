# LetMeAsk：把答题做成服务器活动

> LetSeries  |  2026/9/23

## 一个聊天栏里的抢答游戏

[LetMeAsk](https://github.com/LetSeries/LetMeAsk) 定时在聊天栏发布题目，玩家抢答，答对拿金币。规则很简单，但要把“抢答”做成长期稳定的服务器活动，细节一点都不少：题目从哪来、奖励谁来出、答错了怎么办、脚本刷奖怎么防、统计存在哪——这篇文章把这些答案一次讲清。

## 出题：间隔、超时与题库

出题节拍由 `base.yml` 控制：默认每 60 秒出一题，30 秒无人答对就公布答案并出下一题。题库写在 `questions.yml` 里，支持纯文本与带权重的题目：

- `中国首都=北京`：题目 = 答案，多答案用 `|` 分隔，答对任一即可
- `{q: ..., a: ..., weight: 2}`：权重越大越容易被抽中

解析时会自动去重并告警，`/letmeask status` 能看到当前题库数量，`/letmeask question [force]` 可手动出一题，`/letmeask start` 会立刻出一题而不是干等一轮间隔。

## 发奖：谁出钱、发给谁

经济走 Vault，扣款方（`payer`）可配：服务器出资（`Server`）、指定玩家名、UUID，乃至 `littleskin:` 账号。发奖时优先按 UUID 落到离线玩家，避免玩家改名导致错发；题目携带 id 校验，旧题答案领不走新题奖励。没有 Vault 也不摆烂：自动降级为纯公告模式，出题照常。

## 防刷：模糊匹配 + 人机验证

答案支持模糊匹配，相似度阈值默认 0.75，设为 1.0 即严格精确匹配；超长聊天消息直接拒绝。真正的刷奖脚本靠两道阀值拦：

- 回答用时过快（默认 ≤ 1 秒，支持小数）触发 [HumanVerify](https://github.com/LetSeries/HumanVerify) 验证
- 同一玩家连续答对过多（默认 3 次，带 300 秒时间窗口衰减）同样触发验证

验证期间本轮锁定，回调带 epoch 校验，跨 reload 的旧回调直接丢弃；验证本身也有 120 秒超时兜底，过期自动解锁并作废本轮，不会把正常玩家卡死。

## 统计：持久化与排行榜

累计出题数、答对数、每人答对次数与奖金存在 `stats.yml`。落盘是增量的：每 30 秒只写变更玩家，约 5 分钟全量一次，停服不丢数。`/letmeask top [数量]` 看排行榜（默认前 10），`/letmeask stats [玩家名]` 查个人战绩；最新版还把离线名查询做了缓存，top 榜不再反复读磁盘，未知玩家回退显示 UUID 前 8 位。

## 环境与构建

需要 Paper / Spigot 1.20.4+ 与 Java 17，HumanVerify 与 CMI 都是可选依赖：

- `mvn clean package`，或用 Gradle 离线构建（依赖在 `libs/` 下）
- 产物放进 `plugins/`，改 `base.yml` 与 `questions.yml`，`/letmeask reload` 即生效

MIT License，仓库见 [LetSeries/LetMeAsk](https://github.com/LetSeries/LetMeAsk)。

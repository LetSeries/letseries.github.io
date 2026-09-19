# HumanVerify：进服先验证

> LetSeries  |  2026/9/19

## 为什么做人机验证

机器人和批量小号是很多服务器的头疼问题。[HumanVerify](https://github.com/LetSeries/HumanVerify) 是面向高版本服务端的游戏内验证插件：玩家进服自动打开验证界面，在背包里点中唯一方块即通过，支持 Paper、Folia、Purpur。

## 验证模式不止一种

插件内置多种模式，可固定一种，也可以每轮随机：

- 唯一颜色方块、唯一材质方块
- 按编号顺序点击方块
- 点击指定数量目标方块
- 找出唯一不同的方块
- 点击中心或角落方块

背包大小支持 27 / 36 / 45 / 54 格，配合验证超时与错误次数限制，基本能挡住常见的自动脚本。

## Folia 兼容与开放 API

插件使用 Paper/Folia `EntityScheduler`，不依赖传统全局调度器，天然兼容 Folia 区域线程模型。同时通过 Bukkit `ServicesManager` 暴露 `HumanVerifyApi`，其他插件无需依赖实现包即可调用：

- `requestVerification(player)`：幂等发起验证，已验证直接返回成功
- `requestVerification(player, true)`：强制玩家再次验证
- `markVerified(player)`：直接放行，供可信插件调用

[LetMeAsk](https://github.com/LetSeries/LetMeAsk) 的防刷机制就是这么接的：答题过快或连对过多时自动触发验证。

## 运行与构建

需要 Java 21+ 与 Paper 1.21.x 服务端（`plugin.yml` 已声明 `folia-supported: true`）：

```bash
mvn package
```

产物 `target/HumanVerify-1.0.0.jar` 放进 `plugins/` 目录即可，命令 `/humanverify verify [玩家]`、`/humanverify reload`。

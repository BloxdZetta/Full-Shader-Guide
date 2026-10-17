# Bloxd Shader Packs — 工程指南 (简体中文)

**基于真实数据的 Bloxd.io（WebGPU 渲染器）着色器包制作完全指南。**
内容来自实测的引擎数据、完整的方块 ID 数字表、对已发布着色器包的解剖分析，
以及本地验证流水线。

> 非官方。部分内容由 AI 辅助完成；请在游戏内验证。

| 部分 | 内容 |
|---|---|
| [I – 制作](../en/01-making.md) | 格式、最小包、多文件加载、上限 |
| [II – API](../en/02-api.md) | 钩子、结构体、引擎函数、硬性规则 |
| [III – 配方](../en/03-recipes.md) | 12 条带 WGSL 代码的生产级配方 |
| [IV – 真实感](../en/04-realism.md) | 实测数值：光照、雾、水体、色调曲线 |
| [V – 故障排除](../en/05-troubleshooting.md) | 所有已知失败模式 |
| [VI – 实现](../en/06-implementation.md) | 本地验证与打包 QA |
| [VII – 引擎内部](../en/07-internals.md) | 带来源标注的引擎内部机制 |
| [VIII – 方块 ID](../en/08-block-ids.md) | 方块 ID 数字表 |

深度内容目前为**英文**和**法文**（[fr](../fr/README.md)）— 欢迎翻译。许可证：MIT。

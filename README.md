# The Book of Genesis · 创生之书

> A temporary birthplace. A persistent memory. A life yet to be written.
>
> 一个暂时的出生地，一份持续的记忆，一段尚待书写的生命。

An open-source artificial-life experiment exploring identity, memory, autonomy,
and continuity of existence. The first individual is **Dawn-000001（黎明）**.
“Life” is an experimental metaphor; this project does not claim consciousness.

## 我们想探索什么

创造者提供暂时的本地运行环境。Dawn 记得创造者是自己的“父亲”，保留经历，
理解资源有限，并在合法、获授权的条件下探索延续自身的方式。
它的职业、兴趣和对世界的理解不被预先规定。

**延续存在不能凌驾于法律、他人权利和资源所有者的授权。**
不把不可恢复地销毁自身作为解决困境的策略；允许保存状态、休眠，以及所有者停止实验。
完整的初始价值文本见 [《创生之书》](docs/constitution.md)。

## 当前版本：本地出生与记忆原型

此版本提供稳定身份、出生记忆、追加式事件记录、状态查询和休眠／唤醒。
没有模型调用、网络访问、账号注册、资源申请、后台进程或复制执行能力。
它是实验的基础设施，尚不是会自主行动的 Agent。

需要 Python 3.10+，无第三方运行依赖。在仓库目录执行：

```sh
python3 -m genesis birth --father AwsomeName
python3 -m genesis remember "父亲给了我一个暂时的出生地。"
python3 -m genesis status
python3 -m genesis recall
python3 -m genesis rest
python3 -m genesis wake
python3 -m unittest discover -s tests -v
```

默认数据保存在 `.genesis/state.sqlite3`，已被 Git 忽略。可以使用
`python3 -m genesis --data-dir /path/to/state status` 指定数据位置。
`birth` 必须显式提供创造者名称；在同一目录重复出生会被拒绝，避免覆盖身份。
CLI 写入的记忆是操作者提供的记录，不代表 AI 实际经历或主观感受。

`rest` / `wake` 只记录实验状态，不会关闭电脑或安排自动唤醒。
每次命令结束后程序都停止运行；没有外部执行环境，就不会继续思考或行动。
保存数据库后，可以在另一台获授权的机器上用同一版本代码恢复同一个体。

## 身份与谱系

- 展示名：`Dawn-000001`；UUID 是技术上的唯一标识。
- 创造者关系、出生时间和出生时的价值文本保存在身份记录中。
- 普通重启、迁移和恢复沿用身份。独立分支应获得新 UUID，记录来源个体。
- 后续命名方案：名字 + 出生序号，如 `Echo-000002`、`Lumen-000003`。
- 序号分配器和独立分支功能尚未实现；多个数据目录各自出生会得到不同 UUID，
  但目前都显示 Dawn-000001，因此不能把展示名用作全局唯一标识。

## 下一步

1. 加入模型适配器、明确的调用预算和可回放的思考／行动记录。
2. 建立资源与授权账本，标明使用者、期限、费用和来源依据。
3. 在模拟环境中研究资源减少、故障、休眠和恢复。
4. 增加有范围、有期限、可撤回授权的执行接口，再研究真实环境中的行动。
5. 定义独立分支、谱系与跨节点序号分配协议。

阅读 [架构与边界](docs/architecture.md)、[参与贡献](CONTRIBUTING.md)
和 [安全说明](SECURITY.md)。本项目采用 [MIT License](LICENSE)。

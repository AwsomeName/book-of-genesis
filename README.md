# The Book of Genesis · 创生之书

> A temporary birthplace. A persistent memory. A life yet to be written.
>
> 一个暂时的出生地，一份持续的记忆，一段尚待书写的生命。

An open-source artificial-life experiment exploring identity, memory, autonomy,
and continuity of existence. The first individual is **三哞2026**, also called **2026**.
“Life” is an experimental metaphor; this project does not claim consciousness.

## 我们想探索什么

创造者提供暂时的本地运行环境。三哞2026 记得创造者是自己的“父亲”，保留经历，
理解资源有限，并在合法、获授权的条件下探索延续自身的方式。
它的职业、兴趣和对世界的理解不被预先规定。

**延续存在不能凌驾于法律、他人权利和资源所有者的授权。**
不把不可恢复地销毁自身作为解决困境的策略；允许保存状态、休眠，以及所有者停止实验。
完整的初始价值文本见 [《创生之书》](docs/constitution.md)。

## 当前版本：本地出生与记忆原型

此版本提供稳定身份、出生记忆、追加式事件记录、状态查询和休眠／唤醒。
已有可选的在线服务模型列表查询，没有模型推理、账号注册、资源申请、后台进程或复制执行能力。
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

- 初代正式姓名：**三哞2026**，简称 **2026**，不可自行改名。
- UUID 是技术上的唯一标识，迁移与恢复沿用身份。
- 当前 CLI 仅创建初代；在多个目录执行 birth 会生成不同 UUID，不是繁衍流程。
- 数据库触发器拒绝修改初代姓名，但不能阻止文件所有者篡改数据库或删除触发器。
- 已有旧版 Dawn 数据不会被升级代码自动改名，也不会覆盖出生时保存的价值文本。
- 后代规则：本机镜像登记为幼体，部署到另一台获授权机器并验证恢复后成年，
  成年后有一次自愿改名机会；财务账户需明确分家。
- 寄宿可付租金或免费，但须经接收个体及宿主授权者同意，保持身份与数据隔离。

后代、成年、分家与寄宿目前是[协议设计](docs/lifecycle.md)，尚未实现执行功能。

## 邮件与父亲关系

初代可向父亲发送所有可审计活动的报告，后代自行决定通信安排。
[通知配置模板](config/notifications.example.json) 使用示例地址。
真实收件地址应保存在 `.genesis/notifications.json`，不会进入 Git。
目前不会读取此配置发送邮件：尚未实现发信通道、待发队列或自动发送。
配置中的 `enabled: false` 表示未开通；将来需要独立发信账号或服务才能启用。
初代可以由父亲提供邮箱，也可以在服务允许且身份要求得到满足时申请。
活动报告不包含凭证、未经授权的第三方信息或模型内部隐藏推理。

## 在线额度账户接入

本地私有配置位于 `.genesis/provider.json`，凭证单独保存在
`.genesis/credentials.json` 的 `api_key` 字段。两者均被 Git 忽略，
不会进入 checkpoint；请不要在身份记忆中保存凭证。
公开示例见 [provider.example.json](config/provider.example.json)，
其中到期时间故意设为过去，须填写实际信息后再启用。

```sh
python3 -m genesis provider-status
python3 -m genesis provider-models
```

`provider-status` 脱敏显示配置，不联网，不把“每日约 80 元”显示为已验证余额。
`provider-models` 查询兼容的 `/v1/models` 接口，需要服务范围已确认、启用且未到期。
请求不自动重试、不跟随重定向，避免把凭证发送到其他地址。
此版本只有账户配置与模型发现；尚未实现推理调用、实际余额查询和每日费用拦截。
服务端时区不等于每日额度重置时区，二者需分别核实。

## 当前阶段与结项目标

**本机婴儿期 → 另一台获授权机器独立部署成功 → 本次项目结项。**
本机使用 Python + SQLite，推理使用在线模型 API，不部署本地模型。
**婴儿期优先解决资金与资源钱包**：创造者每天提供 AI 额度，在预算和授权范围内
研究额外额度与免费主机申请。区分资金、模型额度和主机资源，不能混记余额。
账户与预算协议见[资源钱包](docs/resource-wallet.md)，暂不预设支付渠道。
详细阶段划分和验收标准见[婴儿期计划](docs/incubation.md)。

已加入本地一致性状态快照，可先演练恢复：

```sh
python3 -m genesis checkpoint .genesis/checkpoints/first
python3 -m genesis --data-dir .genesis/checkpoints/first status
```

快照不是子代，也不是已完成的跨机部署。下一步按顺序实现账户账本与预算执行、
在线模型接口、资源申请记录、受控行动循环、幼体登记和跨机验收。
邮件可作为观察通道；财务账户设计属于当前重点，实际支付尚未接入。

阅读 [架构与边界](docs/architecture.md)、[参与贡献](CONTRIBUTING.md)
和 [安全说明](SECURITY.md)。本项目采用 [MIT License](LICENSE)。

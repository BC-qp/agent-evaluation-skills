# Agent Evaluation Skills

两套中文 Skill，覆盖从工作材料提炼任务到基于真实证据评测智能体的流程。核心内容按需读取，不需要一次加载所有规则。

**完整链路：出题 → 输入冻结与RUBRIC → 运行归档 → 产物验收 → 过程评审 → 评分取证 → 报告 → 交付。** 阶段输入、输出和交接条件见[完整评测体系](skills/agent-eval-workflow/references/workflow.md)。

| 模块 | 用途 | 入口 |
|---|---|---|
| 1. 任务提示词生成 | 基本规则、信息分层、脱敏、粒度、工具调用量与难度映射 | [task-distiller](skills/task-distiller/SKILL.md) |
| 2. 产物维度评分 | 准确性、完整性、指令遵循、可用性与验收深度 | [产物质量](skills/agent-eval-workflow/references/product-quality.md) |
| 3. 过程维度评分 | 任务理解、工具使用、恢复、核验、交接与证据归因 | [执行过程](skills/agent-eval-workflow/references/process-quality.md) |
| 4. 语言与交付说明 | 具体事实、评分依据、自然表达、反馈与取证 | [语言规范](skills/agent-eval-workflow/references/writing-style.md) |

另有[输出模板](skills/agent-eval-workflow/assets/templates/evaluation-report.md)、[截图取证](skills/agent-eval-workflow/references/evidence-capture.md)、[取证红线](skills/agent-eval-workflow/references/evidence-redlines.md)、[运行归档](skills/agent-eval-workflow/references/run-and-archive.md)与[报告写作](skills/agent-eval-workflow/references/report-writing.md)。

后面三个模块由 [agent-eval-workflow](skills/agent-eval-workflow/SKILL.md) 统一路由。两套 Skill 可以分别使用，也可以依次协作。

## 结构

```text
skills/
  task-distiller/
    SKILL.md
    references/       基本规则、粒度、脱敏、调用量映射和输出合同
    assets/           提示词与任务包模板
    scripts/          提纯产物检查
    agents/           可选界面元数据
  agent-eval-workflow/
    SKILL.md
    references/       产物、过程、校准、语言、取证和归档
    assets/templates/ 评分稿、RUBRIC和任务包模板
    scripts/          任务包创建与结构检查
    agents/           可选界面元数据
docs/
  design-notes.md     目录设计参考
```

## 使用

将需要的完整 Skill 文件夹放入宿主支持的技能目录，依宿主当前说明完成注册或刷新。不要只复制 `SKILL.md`，否则按需引用与模板会缺失。不支持 Skill 注册的环境也可以读取入口及所需参考文件。

任务生成示例：

> 使用 task-distiller，把附带的工作记录和数据整理成任务提示词。脱敏后保留业务难点，明确交付物与验收；设计和脱敏记录留在内部。

评分示例：

> 使用 agent-eval-workflow，按附带任务书、评分规则、首轮产物和完整轨迹分别评价产物与过程，只评价首轮。缺少证据的部分明确说明。

工具调用量不等于难度、工作量或质量。映射方法给出有条件的估计，不提供固定换算系数，也不要求执行者凑次数。参见[调用量映射](skills/task-distiller/references/tool-call-mapping.md)。

## 可选脚本

从仓库根目录运行，Python 3.10+，无需第三方依赖：

```text
python skills/task-distiller/scripts/validate_distilled_task.py <提纯任务包目录> --json
python skills/agent-eval-workflow/scripts/create_task_package.py <新任务包目录>
python skills/agent-eval-workflow/scripts/validate_task_package.py <已运行任务包目录> --json
```

创建脚本生成的是内部归档骨架，不能整个目录直接下发给执行者。运行前只从中取提示词与必要脱敏输入。骨架运行前没有真实轨迹，不能通过已运行任务包检查。校验脚本不证明隐私已彻底清除、轨迹真实或交付质量合格，仍需人工语义检查。

## 分享边界

案例全部标注为虚构教学示例，不含真实运行成绩。任务提示词与必要脱敏附件可交给执行者，内部设计、评分和真实值映射不得混入执行输入。分享新的案例前检查背景组合、编号、哈希、精确数值、链接与文件元数据。

本包提供通用方法，不替代任何一次评测的实际任务书或完整评分标准。没有适用分制时先整理证据，不自动造分。

## 维护

规则只维护一处：入口负责路由，参考文件负责详细方法，模板负责输出结构。修改维度规则时同步检查模板、链接与脚本。目录设计参考见[设计说明](docs/design-notes.md)。

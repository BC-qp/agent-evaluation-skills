---
name: agent-eval-workflow
description: 基于任务要求、真实产物和执行轨迹开展智能体评测，分别检查产物质量与执行过程，整理证据并撰写评分稿。适用于评测设计、运行归档、评分取证和交付检查，不用于运行器安装或凭空评模型。
---

# 智能体评测工作流

先确定本次要做任务设计、运行归档、产物评分、过程评分还是评分稿整理，按已授权范围推进。

完整流程、阶段输入输出和交接条件见[评测体系总览](references/workflow.md)。

## 共同约束

- 本次任务书、实际输入、完整评分标准和实际表单决定分制、字段、标签及范围。通用方法不能替代源标准。
- 产物与过程各自依证据判断，不互相映射分数；没有要求时允许有依据的同分，不增加总分、效率分、权重或封顶。
- 原始执行、教学模拟、评审者复核分别标明。记录缺失限制评价范围，不自动扣分或补造分数。
- 只评某轮时恢复对应产物版本；无法还原的部分不作评价。原始包保持不动。
- 本包不包含私人项目来源目录、历史成绩或真实运行案例。当前材料由用户提供或授权读取。

## 一、任务提示词与运行准备

设计任务读[任务设计接口](references/prompt-design.md)。需要从材料提纯任务时可配合独立 `task-distiller`，本工作流本身不要求另一套 Skill 才能加载。
运行与归档读[执行手册](references/run-and-archive.md)；已有轨迹需要追加任务读[追加需求](references/follow-up-tasks.md)；编写 RUBRIC 读[编写规则](references/rubric-design.md)和[模板](assets/templates/task-rubric.txt)。

## 二、产物维度

完整读取[评分接入](references/scoring-contract.md)、[证据身份](references/evidence-identity.md)、[产物质量](references/product-quality.md)和[独立校准](references/score-calibration.md)。按要求打开、运行或复算实际产物，不用文件数、承诺或PASS文本替代验收。

## 三、过程维度

完整读取共同的评分接入与证据身份，再读[执行过程](references/process-quality.md)、[独立校准](references/score-calibration.md)和[行为归因](references/attribution.md)。核对主会话、续接和子会话，覆盖理解、实施、工具使用、恢复、核验和交接。

## 四、语言与交付说明

写评分稿时完整读取[语言规范](references/writing-style.md)、[取证规则](references/evidence-capture.md)、[交付检查](references/delivery-checklist.md)和[评分模板](assets/templates/scoring-report.md)。每条评价说明事实、位置和影响，整批检查套句、重复反馈和证据一致性。

## 五、报告汇总

需要从评分稿形成完整报告时，读取[报告写作](references/report-writing.md)和[报告模板](assets/templates/evaluation-report.md)。保持原评分事实与口径，按任务和维度汇总，说明证据范围与限制。

## 其他按需材料

- 截图真实性与结论范围：[取证红线](references/evidence-redlines.md)。
- RUBRIC不完整：[补充边界](references/rubric-gaps.md)。
- 冻结输入、归档与验收：[输入清单](assets/templates/input-manifest.md)、[运行记录](assets/templates/run-record.md)、[验收矩阵](assets/templates/acceptance-matrix.md)、[证据索引](assets/templates/evidence-index.md)。
- 找完整标准、处理来源冲突：[来源回溯](references/source-resolution.md)。
- 运行环境、编码和便携使用：[兼容说明](references/compatibility.md)。
- 共享材料或提交：[隐私与提交边界](references/privacy-and-submission.md)。
- 理解两栏独立和自然表述：[虚构教学案例](references/synthetic-examples.md)。

创建任务包：`python scripts/create_task_package.py <新目录>`。
检查已运行任务包：`python scripts/validate_task_package.py <任务包目录> --json`。
以上命令从本 Skill 目录执行。脚本不运行模型，不证明轨迹真实或产物合格；模板骨架缺真实轨迹，预期不能通过已运行任务包检查。

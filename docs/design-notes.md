# 目录设计参考

以下为2026-11-02读取 GitHub 仓库 API 和源文件时的快照，不是全站排名。Stars只辅助选择参照，不证明规则质量。

| 仓库 | Stars快照 | 检查的结构 | 本包采用的部分 |
|---|---:|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | 186,507 | [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) | 短入口；references、scripts、assets各司其职；按需加载 |
| [obra/superpowers](https://github.com/obra/superpowers) | 310,829 | [writing-skills](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) | 长参考与可复用工具分开；规则服务可观察行为，不写成个人复盘 |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | 33,379 | [react-best-practices](https://github.com/vercel-labs/agent-skills/blob/main/skills/react-best-practices/SKILL.md) | 分类索引明确指向细则，避免一个长文档承载所有维度 |

这里只参考组织方式，未复制这些仓库的实现、业务规则或品牌元数据。没有机械套用固定文件数、复杂目录或平台专用字段。

## 本包的划分

- 任务生成独立为 task-distiller。基本规则、工具调用映射和模板分开维护。
- 评测独立为 agent-eval-workflow。产物、过程、语言分开读取；证据身份与评分校准是共享规则。
- 运行器操作留给当前环境说明，本包保留通用的隔离、归档与检查要求。
- 历史来源记录不属于可复用规则。教学案例使用独立构造的情境，明确区分虚构数字与实测结果。

## 检查边界

发布准备包含UTF-8、相对引用、入口元数据、历史标识和脚本行为检查。它不等于在所有宿主上的安装测试，也不构成对评分效果或隐私不可反推的绝对保证。

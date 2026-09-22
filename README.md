# Qualisys Visual3D Joint Angle Skill

一个用于 Codex 的可复用 skill，用来处理 Qualisys QTM/C3D 与 Visual3D 之间的下肢关节角度解算、验证和导出。

它特别适合 CAST 下肢 marker set、静态校准试验、刚性板 tracking markers、右踝/左踝角度，以及从 Visual3D 导出 JSON/CSV 的工作流。

这个仓库不包含任何个人采集数据、QTM/C3D 文件、Visual3D 报告、PAF 文件或实验室私有模型。所有输入路径、marker 命名、模型文件和 pipeline 都必须由当前项目提供并现场验证。

## 解决的问题

从已经正确标记的 QTM/C3D 数据开始，skill 指导 Codex 完成：

1. 保护原始 QTM、C3D、QPR、PAF 和静态试验。
2. 检查 CAST marker identity、左右侧和刚性板拓扑。
3. 将 QTM 数据安全导出为 Visual3D 可用的 C3D。
4. 使用静态试验建立 Visual3D hybrid model。
5. 将动态刚性 marker cluster 映射到大腿、小腿和足部 segment。
6. 根据当前项目实际使用的 `.mdh` 和 recalculation pipeline 计算关节角度。
7. 区分最终 CAST 角度、CGM 角度、raw 角度和 processed 角度。
8. 在导出 CSV 前检查信号是否为空、是否包含 X/Y/Z、帧数是否正确。
9. 保留 source frame、采样率、时间列和 trial 顺序。
10. 对没有测力台的数据禁止输出未经支持的力矩、功率、GRF 或 COP。

## 重要原则

### 不创造 marker

QTM marker 对应和 gap filling 是两个不同问题：

- 只能根据已经采集并确认身份的 marker 对应骨性点或 tracking label。
- 不能为了达到 36 个静态点或 28 个动态点而创造坐标。
- 正确的 `Measured` 数据优先于 relational、interpolated 或其他 synthetic 数据。
- 如果 marker 在错误位置，先修正 identity；不能把 identity 错误当作普通 gap。
- 需要补点时，先确认用户明确授权、参考 marker 有效，并在输出中标记 filled provenance。

如需进行 CAST marker relabel 或 relational gap repair，应先使用对应的 `qualisys-cast-gap-repair` skill。

### 不把非空信号当成正确结果

Visual3D 中信号必须按三部分识别：

```text
TYPE::FOLDER::NAME
```

例如：

```text
LINK_MODEL_BASED::ORIGINAL::Right Ankle Angles
LINK_MODEL_BASED::PROCESSED::Right Ankle Angles
LINK_MODEL_BASED::ORIGINAL::Right Ankle Angles_CGM
```

这三个对象可能具有不同的模型定义。`Right Ankle Angles_CGM` 有数值，并不证明它可以替代 CAST 的 `Right Ankle Angles`。如果最终信号是 0 帧，必须追查 model build、segment pose、pipeline branch 和 signal folder。

### 静态足部归一化不是 gait-cycle 百分比归一化

`right_foot_normalized=TRUE` 通常表示使用静态试验建立的足部参考方向或 floor-related calibration。它不是把 gait cycle 重采样到 0-100%，也不是 body-size normalization。

常见 CAST pipeline 的右踝定义可能是：

```text
TRUE  -> Right Foot Normalized relative to RSK
FALSE -> RMF relative to RSK
```

但这只是常见模式，不能代替检查当前 `.mdh`、`.v3s/.v3m` 和 Visual3D Data Tree。项目自定义模型可能使用不同 segment、参考 segment、Cardan sequence 或 sign convention。

## 目录结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── workflow.md
│   ├── cast-model.md
│   ├── export-validation.md
│   └── troubleshooting.md
└── scripts/
    └── audit_visual3d_joint_angles.py
```

### `SKILL.md`

Skill 的入口说明、适用范围、硬性约束、执行顺序和最终验收标准。

### `references/workflow.md`

从文件清单、QTM 检查、C3D 导出、静态 model、动态 trial、recalc、信号检查到最终 handoff 的完整流程。

### `references/cast-model.md`

说明静态 calibration、动态 rigid cluster、segment relative rotation、CAST 足部归一化和轴方向验证方法。

### `references/export-validation.md`

说明 Visual3D 精确信号选择、JSON 诊断导出、CSV 字段、source frame、time 列和 derivative signal 的注意事项。

### `references/troubleshooting.md`

说明空信号、`_CGM` 混淆、恒定角度偏移、内外翻符号相反、pipeline Replace/Append、没有测力台和 marker identity 错误的排查方法。

### `scripts/audit_visual3d_joint_angles.py`

只读审计 Visual3D JSON。它不会修改原始数据，默认检查精确的 `Right Ankle Angles` 信号。

## 安装到 Codex

### 方法一：从 GitHub 安装

如果环境提供 skill installer，可以使用仓库地址安装：

```text
$skill-installer https://github.com/anonymousguestme-ctrl/QualisysVisual3dJointAngleSkill.git
```

### 方法二：手动安装

将仓库目录复制到 Codex skills 目录，并保留以下结构：

```text
<CODEX_HOME>/skills/qualisys-visual3d-joint-angles/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/
```

如果没有设置 `CODEX_HOME`，通常使用用户的 `.codex/skills` 目录。安装后重新启动 Codex，使 skill 目录被重新发现。

## 使用示例

```text
使用 $qualisys-visual3d-joint-angles，处理这个文件夹中的 CAST 动态试验。
先确认静态试验和动态 trial 顺序，再检查 marker identity 和 tracking cluster。
使用当前项目实际的 Visual3D model/pipeline 解算右踝关节角，最后导出每个 trial 的 CSV。
不要覆盖任何原始 QTM、C3D 或 CMZ；如果最终 Right Ankle Angles 为空，不要自动改用 _CGM。
```

没有测力台时：

```text
使用 $qualisys-visual3d-joint-angles 只计算 marker-based kinematics。
输出右踝角度、角速度和角加速度，但不要输出或声称有效的 GRF、COP、关节力矩和功率。
```

## 推荐的 Visual3D 操作顺序

1. 建立受保护的输入 manifest，记录路径、大小、修改时间和 SHA-256。
2. 确认用户指定的 static trial 和动态 trial 顺序。
3. 在 QTM 中检查标签、颜色、bone lines、TH/SK 刚性板和左右侧。
4. 处理 identity 问题后再处理明确授权的 gap filling。
5. 将 static 和 dynamic trial 导出为 full-label C3D。
6. 用 static C3D 创建或加载 hybrid model。
7. 应用当前项目的 CAST `.mdh`，检查 build warnings 和 segment axes。
8. 将同一个 calibrated model 关联到动态 C3D。
9. 查看实际 `model_used`、足部归一化开关、event mode 和 recalc branch。
10. 运行 recalc，发现 segment 或 signal 错误时停止追查上游原因。
11. 在 Data Tree 中检查 exact `TYPE::FOLDER::NAME`，确认 X/Y/Z 均有逐帧数值。
12. 先导出 JSON 并审计，再转换为 CSV。
13. 保存新的 CMZ 和 manifest，不覆盖原报告。

## JSON 审计

对单个文件：

```powershell
py -3 scripts\audit_visual3d_joint_angles.py `
  --input .\export\01_trial.json `
  --signal "Right Ankle Angles" `
  --expected-frames 800 `
  --sample-rate 100
```

对目录：

```powershell
py -3 scripts\audit_visual3d_joint_angles.py `
  --input .\export\ `
  --signal "Right Ankle Angles" `
  --sample-rate 100
```

审计失败的情况包括：

- exact signal 不存在或出现多个匹配对象；
- signal 为 0 帧；
- 缺少 X、Y 或 Z；
- component 长度与声明帧数不一致；
- 存在空值、NaN、Infinity 或非数字值；
- 固定帧数与预期不一致。

该脚本是结构审计，不替代 Visual3D 动画检查、曲线检查、marker identity 检查和已知动作的正负方向验证。

## CSV 推荐字段

长表 CSV 建议至少包含：

```text
trial_order
trial
source_file
signal_type
signal_folder
signal
component
clinical_axis_label
positive_direction_evidence
unit
sampling_frequency_hz
sample_index
source_frame
time_seconds
value
```

当轴的临床含义或正方向没有通过模型和已知动作验证时，使用 `unverified`，不要猜测。

如果源数据没有时间列，可在确认 point rate 和 first source frame 后计算：

```text
time_seconds = (source_frame - first_source_frame) / point_rate_hz
```

不要仅因为 velocity/acceleration 的数组少了首尾帧，就假定它们一定是某个 angle signal 的中心差分。必须检查生成命令、过滤和时间对齐。

## 什么情况下必须停止

出现以下任一情况，应报告 `not validated`，而不是交付一个看似完整的 CSV：

- static trial 未确认或属于另一个 session/subject；
- marker identity、左右侧或刚性板拓扑有歧义；
- requested segment 没有有效 pose；
- 只有替代信号有数值，且无法证明定义等价；
- 轴方向或正负号无法用模型或已知动作确认；
- marker-only session 被要求输出 kinetics；
- 无法证明原始文件没有被覆盖；
- pipeline 的 Replace/Append 状态或 active file 不清楚。

## 相关官方文档

- [Qualisys: Using QTM data with Visual3D](https://docs.qualisys.com/getting-started/content/getting_started/getting_started_with_biomechanics/using_qtm_data_with_visual3d.htm)
- [Qualisys: Export to C3D](https://docs.qualisys.com/qtm/content/processing_measurement/export_to_c3d_format.htm)
- [Qualisys: C3D export settings](https://docs.qualisys.com/qtm/content/project_options/c3d_export.htm)
- [Visual3D: Compute Model Based Data](https://www.wiki.has-motion.com/doku.php?id=visual3d%3Adocumentation%3Apipeline%3Amodel_based_data_commands%3Acompute_model_based_data)

## 许可证

仓库许可证见 [LICENSE](LICENSE)。

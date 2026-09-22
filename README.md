<div align="center">

# Qualisys Visual3D Joint Angle Skill

### 从 Qualisys QTM/C3D 到 Visual3D：建立 CAST 下肢模型、计算关节角、验证信号并导出 CSV

面向 CAST 静态校准、刚体板动态追踪和踝关节角度分析的可复用 Codex Skill。

中文｜[GitHub](https://github.com/anonymousguestme-ctrl/QualisysVisual3dJointAngleSkill)

</div>

---

## ✨ 为什么做它

Visual3D 中出现一条平滑曲线，并不代表关节角一定正确。

同一个报告里可能同时存在：

- CAST 关节角；
- CGM 关节角；
- raw rigid-cluster angle；
- static-foot-normalized angle；
- `ORIGINAL` 与 `PROCESSED` 文件夹中的同名信号；
- 有名称但为 0 帧的无效信号。

如果只按名称或“有没有数值”选择信号，很容易把 `_CGM` 当成 CAST、把 raw angle 当成静态归一化角，或者把错误 segment 的相对旋转导出为最终结果。

这个项目把一套可追溯的处理流程固化下来：

- 保护原始 QTM、C3D、QPR、PAF、静态试次和 Visual3D 报告；
- 先确认 marker identity 和刚体板拓扑，再进入模型解算；
- 用静态试次建立解剖坐标系，用动态刚体 marker 追踪 segment pose；
- 明确记录 distal segment、reference segment 和角度分解方式；
- 区分 CAST、CGM、raw 和 static-normalized 信号；
- 先导出 JSON 做结构审计，再生成有 frame/time 的 CSV；
- marker-only 数据只报告运动学，不虚构关节力矩、功率、GRF 或 COP。

## 🚦 结果状态

| 状态 | 条件 | 可以怎样报告 |
| --- | --- | --- |
| ✅ Validated | 静态模型、segment pose、精确信号、XYZ、帧数、时间轴和轴方向均已验证 | 可作为最终关节角结果 |
| ⚠️ Raw CAST | `RMF relative to RSK` 等 raw segment angle 有效，但静态归一化分支未验证 | 必须明确标为 Raw CAST |
| ⚠️ Structurally valid | XYZ、帧数和数值通过审计，但临床轴/正方向尚未验证 | 可导出，但轴含义写 `unverified` |
| ❌ Not validated | requested signal 为 0 帧、segment 无 pose、模型分支不明或只有替代信号有数据 | 不得冒充最终结果 |

> [!IMPORTANT]
> `_CGM` 有数据，不代表它可以替代 CAST 的 `Right Ankle Angles`。替代信号必须证明模型定义等价，否则只能单独命名和报告。

## 🧭 它是怎么工作的

```text
人工确认的静态 CAST 试次
        │
        ├── 解剖 marker / joint center
        ├── segment 局部坐标系
        └── tracking cluster 与解剖段的校准关系
                        │
                        ▼
              动态 C3D / rigid clusters
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
      骨盆姿态        大腿/小腿姿态       足部姿态
        │               │               │
        └───────────────┼───────────────┘
                        ▼
        distal segment 相对 reference segment
                        │
                        ▼
         按 Visual3D 当前旋转约定分解 XYZ
                        │
                        ▼
       exact signal 检查 → JSON 审计 → CSV
```

概念上，若两个 segment 的旋转矩阵都表示在实验室坐标系中：

```text
R_relative(t) = transpose(R_reference(t)) * R_distal(t)
joint_components(t) = decompose(R_relative(t), active Visual3D convention)
```

关节角不是由两个 marker 的连线直接计算。动态 marker cluster 用来估计 segment 的每帧姿态；静态校准把 tracking cluster 的姿态映射到解剖坐标系。

## 🦶 CAST 踝关节定义

常见 CAST 右踝分支如下，但必须检查当前项目的 `.mdh`、`.v3s/.v3m` 和 Visual3D Data Tree，不能只凭这个表推断：

| 分支 | Distal segment | Reference segment | 说明 |
| --- | --- | --- | --- |
| CAST static-normalized | `Right Foot Normalized` | `RSK` | 使用静态足姿势/地面参考建立的足段 |
| CAST raw | `RMF` | `RSK` | 未使用 static-foot-normalized 段 |
| CGM | `RFT` | `RSK` | CGM 分支，不自动等价于 CAST |

左侧通常对应：

```text
Left Foot Normalized relative to LSK
LMF relative to LSK
LFT relative to LSK
```

### 静态足归一化是什么

`right_foot_normalized=TRUE` 通常表示使用静态试次和 floor-related calibration 建立足部参考方向。它不是：

- 把步态周期重采样到 0-100%；
- 用身高或体重归一化；
- 把每条曲线减去自己的第一帧；
- 自动把站立帧强制变成三个方向都为 0°。

只有在 normalized foot segment 确实建立成功并在动态 trial 中具有有效 pose 时，才能把结果称为 static-foot-normalized ankle angle。

## 📦 需要准备什么

| 项目 | 要求 | 用途 |
| --- | --- | --- |
| Qualisys QTM | 已正确标记的静态和动态试次 | marker trajectory 和 label 来源 |
| C3D | 保留完整 label、帧范围、单位和 point rate | Visual3D 输入 |
| 静态 CAST trial | 与动态数据属于同一受试者和 session | 建立校准模型 |
| CAST `.mdh` | 当前项目实际使用的模型模板 | segment 和 tracking target 定义 |
| Recalc pipeline | 当前报告对应的 `.v3s/.v3m` | 选择模型分支和生成信号 |
| Visual3D | 能打开并重算当前报告 | 模型建立、解算和导出 |
| Python 3 | 用于 JSON 结构审计 | 运行仓库审计脚本 |

如果 marker identity、左右侧、TH/SK 刚体板或 gap 尚未确认，应先使用 `qualisys-cast-gap-repair`，不要直接进入关节角解算。

## ⚡ 快速开始

### 1. 下载项目

```powershell
git clone https://github.com/anonymousguestme-ctrl/QualisysVisual3dJointAngleSkill.git
cd QualisysVisual3dJointAngleSkill
```

### 2. 安装为 Codex Skill

使用 skill installer：

```text
$skill-installer https://github.com/anonymousguestme-ctrl/QualisysVisual3dJointAngleSkill.git
```

也可以手动复制到：

```text
%USERPROFILE%\.codex\skills\qualisys-visual3d-joint-angles
```

安装后重新启动 Codex，使 skill 被重新发现。

### 3. 调用 Skill

```text
$qualisys-visual3d-joint-angles

处理这个目录中的 CAST 静态和动态试次。
先确认静态文件、动态 trial 顺序和 marker identity，
再用当前项目的 Visual3D model/pipeline 计算右踝关节角，
最后按 trial 顺序导出带 Frame 和 Time 的 CSV。
不要覆盖原始 QTM、C3D 或 CMZ；不要用 _CGM 替代为空的 CAST 信号。
```

### 4. 审计 Visual3D JSON

单个文件：

```powershell
py -3 scripts\audit_visual3d_joint_angles.py `
  --input .\export\01_trial.json `
  --signal "Right Ankle Angles" `
  --expected-frames 800 `
  --sample-rate 100 `
  --folder ORIGINAL
```

整个目录：

```powershell
py -3 scripts\audit_visual3d_joint_angles.py `
  --input .\export `
  --signal "Right Ankle Angles" `
  --sample-rate 100 `
  --folder ORIGINAL
```

审计器会检查：

- exact signal 是否唯一存在；
- 是否为 0 帧；
- X/Y/Z 是否完整；
- component 长度是否一致；
- 是否存在 null、NaN、Infinity 或非数字；
- 帧数是否与预期一致；
- sample span 是否与 point rate 一致。

该脚本只做结构审计，不能替代 Visual3D 动画、segment axes、marker identity、波形和已知动作方向检查。

## 🔄 推荐工作流程

### 1. 冻结 provenance

记录并保护：

- 原始 `.qtm`、采集 `.c3d`、`.qpr`、PAF 和 settings；
- 用户确认的静态 trial；
- 用户确认的动态 trial 顺序；
- CAST `.mdh` 和 recalc pipeline；
- CMZ 报告；
- 文件大小、修改时间和 SHA-256；
- QTM/Visual3D 是否有未保存状态。

所有输出写入新目录，保存新的 CMZ。不要覆盖唯一报告或原始采集文件。

### 2. 检查 QTM marker

确认：

- 左右 marker 身份；
- TH/SK 四点刚体板拓扑；
- 足部 marker；
- `Measured` 与 filled provenance；
- QTM bone/line；
- 分析范围内的 gap 和身份跳变。

Measured 优先，但 Measured 标签也可能贴错物理点。身份不确定时先处理 marker，不能靠平滑关节角掩盖问题。

### 3. 导出 C3D

核对：

- full marker labels；
- static/dynamic 文件对应关系；
- first/last frame；
- point rate 和 analog rate；
- 长度单位与实验室坐标轴；
- events 和 force-platform metadata；
- 是否意外裁剪或转换坐标系。

### 4. 建立静态模型

在 Visual3D 中用静态 C3D 创建或加载 hybrid model，并应用当前项目的 CAST `.mdh`。检查：

- pelvis、thigh、shank、foot segment 是否存在；
- joint center 和 segment length 是否合理；
- TH/SK tracking target 是否绑定正确侧；
- 足部 marker 是否绑定到预期 foot segment；
- segment axes 是否朝向合理；
- build warnings 是否全部解释。

### 5. 关联动态 trial

只加载用户确认的动态文件，并对所有动态 trial 使用同一个已校准模型。播放每个 trial，检查第一帧、大动作区间、gap 两端和最后一帧的 segment pose。

### 6. 确认模型分支

记录实际执行值，例如：

```text
model_used = CAST
right_foot_normalized = TRUE or FALSE
left_foot_normalized = TRUE or FALSE
event_mode = actual acquisition mode
```

如果没有测力台，应使用运动学路径，不能因为复制的 `session.xml` 写着 `Multiple forceplates` 就声称存在有效动力学结果。

### 7. 重算与信号检查

加载完整独立 pipeline 时通常选择 **Replace**；只有确认新命令应接在现有流程之后时才选择 **Append**。执行前检查 pipeline 列表和 active file。

在 Data Tree 中按完整身份检查：

```text
TYPE::FOLDER::NAME
```

例如：

```text
LINK_MODEL_BASED::ORIGINAL::Right Ankle Angles
LINK_MODEL_BASED::PROCESSED::Right Ankle Angles
LINK_MODEL_BASED::ORIGINAL::Right Ankle Angles_CGM
```

这些是不同对象。诊断导出应包含 empty signal，避免 0 帧信号在输出中静默消失。

### 8. JSON 审计与 CSV 导出

先导出 Visual3D JSON，运行仓库审计脚本，再转换成 CSV。每个 trial 的 CSV 至少保留：

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

如果 QTM TSV 或其他来源提供逐帧 `Frame/Time`，优先使用原始时间列。如果只能根据 point rate 计算，应明确记录：

```text
time_seconds = (source_frame - first_source_frame) / point_rate_hz
```

不要默认每个 C3D 从 frame 1 开始。

## ✅ 最终验收

只有以下条件全部满足，才能把结果称为最终关节角：

- 静态和动态源文件已明确列出并受保护；
- marker identity、左右侧和刚体板拓扑通过检查；
- 静态模型成功建立，请求的 segment 全程有有效 pose；
- 记录了 distal segment、reference segment 和 normalization 分支；
- exact requested signal 具有完整 X/Y/Z；
- 每个 trial 帧数和 source frame/time 对齐；
- 轴含义和正方向有模型或已知动作证据；
- filters、gap fill、裁剪和 boundary loss 已披露；
- JSON 审计和 Visual3D 曲线/动画检查均通过；
- marker-only session 没有报告 kinetics；
- 原始文件重算哈希后保持不变。

## 🧾 输出 Manifest

建议每次处理保存一个 manifest，至少包含：

```text
source_qtm_c3d_paths_and_hashes
static_trial
ordered_dynamic_trials
model_template_path_and_hash
recalc_pipeline_path_and_hash
model_used
foot_normalization_choice
distal_segment
reference_segment
signal_type_folder_name
rotation_convention
axis_and_sign_evidence
point_rate
source_frame_and_time_rule
filters_and_gap_fill_provenance
output_json_csv_cmz_paths
validation_result
warnings_and_limitations
```

## 🎯 X/Y/Z 和临床方向

很多 CAST 工作流把三个分量解释为：

- X：矢状面屈伸；
- Y：额状面内翻/外翻；
- Z：横断面内旋/外旋。

但这只是常见假设，不是所有项目的通用真理。必须通过以下至少一种方式验证：

1. 查看 Visual3D segment axes 和 joint-angle definition；
2. 使用已知方向的单独动作 trial；
3. 比较已控制的静态姿势和中立位；
4. 检查 pipeline 中的 Cardan sequence、negate 和 resolution coordinate system。

没有证据时，在 CSV 中写 `unverified`，不要凭 X/Y/Z 名称赋予临床正方向。

## ⚖️ 运动学与动力学

| 输出 | 仅 marker + 静态校准 | 还需要有效测力台/动力学输入 |
| --- | ---: | ---: |
| 关节角 | ✅ | 否 |
| 角速度/角加速度 | ✅ | 否 |
| GRF / COP | ❌ | ✅ |
| 关节力矩 | ❌ | ✅ |
| 关节功率 | ❌ | ✅ |

没有测力台的内翻/外翻动作仍然可以计算关节角，但不能给出可信的踝关节力矩、功率、GRF 或 COP。

## 🛠️ 故障排查

### `Right Ankle Angles` 为 0 帧

依次检查：

1. exact signal 位于 `ORIGINAL` 还是 `PROCESSED`；
2. 当前 active file 是否正确；
3. `Right Foot Normalized` 或 `RMF` 是否有有效 pose；
4. `RSK` 是否由正确的 `R_SK1-R_SK4` 追踪；
5. `model_used` 和 `right_foot_normalized` 实际执行值；
6. model build/recalc 的第一条上游错误；
7. 单个 trial 在干净 pipeline 状态下是否能重算。

不要立即切换到 `_CGM`。

### `_CGM` 有数据，但 CAST 为空

这说明 CGM 分支可能有效，但不能证明与请求的 CAST 定义等价。修复 CAST segment/model 分支；若用户明确需要比较，可把 `_CGM` 作为单独命名的对照信号导出。

### 静态归一化足段为 0 帧

检查静态足 marker、floor landmarks、模型段名称和动态 tracking target。如果仍然无 pose，报告 `not validated`。只有用户明确接受不同定义时，才可以另行计算并命名 `Right Ankle Angles Raw CAST`，不能悄悄替代最终信号。

### 角度有很大的固定偏置

检查 raw/static-normalized 分支、静态 trial、静态姿势、左右身份、足/小腿 segment axes、实验室坐标系和单位。不要先做减零处理；盲目减去第一帧可能掩盖模型错误。

### 内翻/外翻符号相反

先播放已知方向动作并显示 segment axes。确认是坐标约定、左右侧符号、marker identity 还是 segment orientation 问题。任何翻转都应生成新的 derived signal，并记录公式和依据。

### 角度、角速度和角加速度帧数不同

检查每个信号的生成命令和滤波方式。中心差分可能损失边界样本，但帧数少不能单独证明时间偏移。不能在定义和对齐不明时把它们合并为同一分析表。

### Visual3D 询问 Replace 或 Append

- 完整独立 pipeline：选择 **Replace**；
- 明确设计为当前流程后续步骤：选择 **Append**；
- 不清楚现有 pipeline 是否有未保存工作：取消并先检查。

## 🔐 数据与隐私

- 仓库不包含受试者 QTM、C3D、CMZ、PAF、CSV 或实验室私有模型；
- 原始采集和唯一报告不应被提交到 GitHub；
- 输出使用新的目录、文件名和 CMZ；
- manifest 可以记录哈希和相对名称，但公开前应移除受试者姓名和本地绝对路径；
- 本项目不自动上传实验数据，也不证明第三方模型模板的许可范围。

## 📁 项目结构

```text
SKILL.md                               Codex Skill 入口和强制规则
agents/openai.yaml                     Skill 显示名称和默认提示词
references/workflow.md                 QTM → C3D → Visual3D 完整流程
references/cast-model.md               CAST segment、踝角和足归一化定义
references/export-validation.md        JSON/CSV、frame/time 和数值验证
references/troubleshooting.md          空信号、CGM、偏置和 pipeline 排查
scripts/audit_visual3d_joint_angles.py  Visual3D JSON 只读审计器
LICENSE                                MIT License
```

## 🧪 开发检查

```powershell
py -3 -m py_compile .\scripts\audit_visual3d_joint_angles.py
py -3 .\scripts\audit_visual3d_joint_angles.py --help
```

Skill 结构可使用 Codex `skill-creator` 的 `quick_validate.py` 检查。

## ⚠️ 当前限制

- 默认说明面向 CAST Lower Body，其他 marker set 必须重新核对模型定义；
- 不包含实验室私有 `.mdh`、`.v3m` 或 Visual3D license；
- 审计脚本只验证 JSON 结构，不证明生物力学定义正确；
- 不能仅靠曲线形状判断左右侧、segment 或 marker identity；
- 不同实验室可能使用不同坐标轴、Cardan sequence 和符号；
- 自动化不能替代 Visual3D Data Tree、3D 动画和已知动作的人工复核；
- 无有效 force/analog 数据时，只能报告运动学。

## 相关文档

- [Qualisys：Using QTM data with Visual3D](https://docs.qualisys.com/getting-started/content/getting_started/getting_started_with_biomechanics/using_qtm_data_with_visual3d.htm)
- [Qualisys：Export to C3D](https://docs.qualisys.com/qtm/content/processing_measurement/export_to_c3d_format.htm)
- [Qualisys：C3D export settings](https://docs.qualisys.com/qtm/content/project_options/c3d_export.htm)
- [Visual3D：Compute Model Based Data](https://www.wiki.has-motion.com/doku.php?id=visual3d%3Adocumentation%3Apipeline%3Amodel_based_data_commands%3Acompute_model_based_data)

## License

本项目使用 [MIT License](LICENSE)。

# 基于 Agent 的胎儿医学影像工具链
AutoRecon 用于胎儿脑 MRI 的脑提取、三维重建、图像配准、组织分割、脑区分区、表面生成，以及基于证据的质量检查和研究报告生成。

推荐通过 Agentic Dashboard 使用：用户直接输入自然语言需求，系统先整理需求并生成执行计划，用户确认后再运行工具。每一步都会显示进度、简短日志、可视化结果和技术质量指标。

> 最终报告用于科研分析和专家复核，不是临床诊断报告。技术检查通过不代表医学正常。

## 1. 快速启动 Dashboard

### 1.1 配置非敏感参数

项目根目录的 `.env` 只保存非敏感配置。可以从示例开始：

```bash
cd /mnt/sda/huangwei/projects/AutoRecon
cp .env.example .env
```

当前推荐配置格式：

```dotenv
AUTORECON_LLM_ENABLED=true
AUTORECON_LLM_PROVIDER=auto
AUTORECON_LLM_BASE_URL=https://airouter.aibotplatform.com/v1
AUTORECON_LLM_MODEL=anthropic/claude-sonnet-4-6

AUTORECON_LLM_USE_FOR_REQUEST_PARSING=true
AUTORECON_LLM_USE_FOR_PLANNING=true
AUTORECON_LLM_USE_FOR_RESULT_ANALYSIS=true
AUTORECON_LLM_USE_FOR_REPORTING=true
AUTORECON_LLM_FALLBACK_TO_RULES=true

AUTORECON_ANTS_DIR=/home/huangwei/.conda/envs/ants/bin
AUTORECON_ROI_WARP_ENV=/home/zhaojunyang/.conda/envs/zjy
```

`auto` 会先尝试 OpenAI-compatible 接口；遇到协议级 `404/405` 后自动尝试 Anthropic native 接口，并记住成功的协议。

### 1.2 配置 API Key

API Key 不要写入项目 `.env`、代码或命令历史。推荐保存在本地 Secret 文件：

```bash
# /mnt/sda/huangwei/.env
AUTORECON_LLM_API_KEY='your-key'
```

安全启动脚本会在当前 Dashboard 进程启动前执行 `source/export`，但不会复制或打印 Key：

```bash
cd /mnt/sda/huangwei/projects/AutoRecon

AUTORECON_SECRET_FILE=/mnt/sda/huangwei/.env \
  scripts/run_agentic_dashboard.sh \
  --host 127.0.0.1 \
  --port 8901
```

打开：

```text
http://127.0.0.1:8901
```

也可以手动导出后启动：

```bash
export AUTORECON_LLM_API_KEY='your-key'

python -m agentic.dashboard_server \
  --host 127.0.0.1 \
  --port 8901
```

如果端口已被占用，先确认占用进程：

```bash
lsof -iTCP:8901 -sTCP:LISTEN
```

停止确认不再需要的旧 Dashboard，或者改用其他端口，例如 `8902`。不要直接结束来源不明的进程。

通过 SSH/VS Code Remote 使用时，需要把远程端口 `8901` 转发到本机，然后在本机浏览器打开上述地址。

## 2. Dashboard 的标准使用流程

### 第一步：输入自然语言需求

用户可以自由描述目标，不需要按照固定关键词模板编写。建议明确说明：

- 从原始数据运行，还是导入已有结果。
- 受试者目录或已有 run 目录。
- 孕周和图谱。
- 希望实际运行、页面展示、报告引用哪些步骤。
- 是否允许复用已有中间结果。
- 报告语言和详细程度。

### 第二步：选择 Execution mode

| 选项                         | 什么时候使用                            | 是否运行影像处理工具 |
| ---------------------------- | --------------------------------------- | -------------------- |
| `Run full pipeline`        | 从原始 BTFE NIfTI 开始新运行或断点继续  | 是                   |
| `Import existing run demo` | 导入已完成的 run，查看可视化、QC 和报告 | 否                   |
| `Plan only`                | 只让系统理解需求并生成计划              | 否                   |

### 第三步：填写路径参数

从原始数据运行时：

```text
Execution mode: Run full pipeline
Subject directory: 包含 BTFE_*.nii.gz 的受试者目录
Work root: 新 run 的输出目录
Gestational age: 胎龄周数
Atlas: 对应孕周图谱
ROI mode: warp / segresnet / skip
Surface: auto / on / off
```

导入已有结果时：

```text
Execution mode: Import existing run demo
Existing run directory: 已有 run 根目录
Gestational age: 对应孕周
```

### 第四步：点击 Generate plan

`Generate plan` 只会：

1. 理解用户需求并生成结构化需求单。
2. 根据系统已有工具生成按依赖排序的计划。
3. 检查工具、前置步骤、路径、参数和运行环境。
4. 在 Task Plan 中展示计划。

此时不会启动 GPU 或 Pipeline。生成过程中页面会显示处理中提示。

请重点检查：

- `execution_mode` 是否符合“新运行”或“导入已有结果”。
- `subject_dir`、`work_root`、`existing_run_dir` 是否正确。
- `execution_steps` 是否与用户要求一致。
- `display_steps` 是否只控制页面展示。
- `report_steps` 是否符合报告范围；空数组表示使用全部已有证据。
- `missing`、`warnings`、`unfulfilled_requests` 是否为空或合理。

### 第五步：点击 Run / Demo

确认计划无误后点击 `Run / Demo`：

- 新运行会异步启动 Pipeline，并立即返回 run ID。
- 导入模式会读取已有产物，不重新进行影像计算。
- 页面每两秒更新状态，不会反复重建交互图像窗口。
- 每一步会展示简短实时日志、产物链接、QC 指标和可视化。

## 3. 可直接使用的需求示例

### 示例 A：从原始数据运行前三步

表单：

```text
Execution mode: Run full pipeline
Subject directory: /mnt/sda/public/00_Datasets/in_house/MRI/20260430-NJGL-fetal_brain/IngeniaAmbition_patch2/nii/AnHuiJing
Work root: /mnt/sda/huangwei/projects/AutoRecon/AnHuiJing_raw_run01
Gestational age: 31
Atlas: /mnt/sda/public/00_Projects/2512_AutoRecon/data/FBA_Chinese_Atlas/img/31w.nii.gz
ROI mode: skip
Surface: off
```

用户需求：

```text
请对31周胎儿 AnHuiJing 从原始 BTFE NIfTI 输入开始，
重新运行 extraction、reconstruction、registration，
不复用任何已有中间结果。展示这三个步骤的日志、产物、质量指标和可视化，
分别生成分步说明，并生成一份包含全部执行步骤的完整中文最终报告。
```

正确计划应满足：

```text
execution_mode = run_pipeline
resume = false
execution_steps = [extraction, reconstruction, registration]
display_steps = [extraction, reconstruction, registration]
report_steps = [extraction, reconstruction, registration]
```

### 示例 B：导入完整结果

```text
导入 existing_run_dir=/mnt/sda/huangwei/projects/AutoRecon/AnHuiJing_run02，
展示完整六步可视化、每一步质量指标和日志，
基于全部证据生成完整中文专业研究报告。
```

表单选择：

```text
Execution mode: Import existing run demo
Existing run directory: /mnt/sda/huangwei/projects/AutoRecon/AnHuiJing_run02
```

### 示例 C：页面只展示一步，但报告使用全部证据

```text
导入 existing_run_dir=/mnt/sda/huangwei/projects/AutoRecon/BaiHuPing_run01，
只展示 reconstruction，但用全部可用证据生成完整中文报告，
并明确列出需要复核的质量问题。
```

正确解析应为：

```text
display_steps = [reconstruction]
report_steps = []  # 空数组表示报告使用全部可用证据
```

页面只显示 Reconstruction，但 Evidence Bank 和最终报告仍会保留并检查其他步骤，避免因为页面隐藏而漏报问题。

## 4. 三种范围的区别

| 字段                | 含义                       | 影响                           |
| ------------------- | -------------------------- | ------------------------------ |
| `execution_steps` | 实际计算哪些 Pipeline 步骤 | 计算资源、执行时间和依赖步骤   |
| `display_steps`   | Dashboard 显示哪些步骤     | 只影响页面                     |
| `report_steps`    | 报告引用哪些步骤的证据     | 只影响报告；空数组表示全部证据 |

例如“只展示 reconstruction，但生成完整报告”并不矛盾：页面可以保持简洁，报告仍检查所有已有证据。

## 5. 六步 Pipeline 和质量检查

```text
脑提取 → 三维重建 → 图像配准 → 组织分割 ┐
                              └→ 脑区分区 ┴→ 表面生成
```

Step 4、5、6 必须基于 Step 3 的配准结果：

```text
outputs/registered_input/<subject>.nii.gz
```

Dashboard 中每一步至少显示两个技术质量指标：

| 步骤           | 主要检查                                  |
| -------------- | ----------------------------------------- |
| Extraction     | 掩膜成功率、前景范围、切片覆盖            |
| Reconstruction | 图像有限值、非零比例、强度范围、体素数    |
| Registration   | Mattes、GC、配准图像是否存在              |
| Tissue         | 标签数、前景范围、与配准 MRI 空间是否一致 |
| ROI            | 标签数、前景范围、与配准 MRI 空间是否一致 |
| Surface        | 必要表面文件和统计文件是否齐全            |

状态含义：

- `PASS`：自动技术检查通过，仍建议人工查看图像。
- `REVIEW`：结果已生成，但需要人工复核。
- `FAIL`：关键技术检查未通过，不应直接信任相关下游结果。

这些状态评价的是技术产物，不评价胎儿是否医学正常或异常。

## 6. 命令行直接运行 Pipeline

不使用 LLM/Dashboard 编排时，可以直接运行：

```bash
cd /mnt/sda/huangwei/projects/AutoRecon

bash pipeline/run_single_case_pipeline.sh \
  --subject-dir /path/to/subject \
  --work-root /path/to/run01 \
  --atlas /path/to/31w.nii.gz \
  --ga 31 \
  --roi-mode warp \
  --surface auto \
  --dashboard on
```

只运行前三步：

```bash
bash pipeline/run_single_case_pipeline.sh \
  --subject-dir /path/to/subject \
  --work-root /path/to/run01 \
  --atlas /path/to/31w.nii.gz \
  --ga 31 \
  --roi-mode skip \
  --surface off \
  --steps extraction,reconstruction,registration \
  --dashboard on
```

从已验证产物断点继续：

```bash
bash pipeline/run_single_case_pipeline.sh \
  --subject-dir /path/to/subject \
  --work-root /path/to/run01 \
  --atlas /path/to/31w.nii.gz \
  --ga 31 \
  --roi-mode warp \
  --surface auto \
  --steps roi,surface \
  --resume \
  --dashboard on
```

`--resume` 会校验已有文件，从第一个缺失或失败步骤继续；它不会仅凭文件名假设产物有效。

完整参数说明：

```bash
bash pipeline/run_single_case_pipeline.sh --help
```

## 7. 输出文件

每个 Agentic run 默认保存在：

```text
agentic_runs/<run_id>/
```

主要文件：

```text
agentic_state.json       # 完整运行状态
intent_spec.json         # 结构化用户需求
task_plan.json           # 经验证的执行计划
evidence_bank.json       # 用户需求、计划、逐步 QC、来源、结论和限制
medical_evidence.json    # 报告使用的医学研究证据
report.md                # 最终可读报告
```

Pipeline 工作目录还包含：

```text
<work_root>/dashboard/run_state.json
<work_root>/dashboard/qc_summary.json
<work_root>/dashboard/logs/
<work_root>/dashboard/previews/
<work_root>/outputs/
```

## 8. 运行验证

运行自动化测试：

```bash
python -m unittest discover -s tests -v
```

验证 Demo、Evidence Bank、截图和组会材料：

```bash
python scripts/verify_goal_deliverables.py
```

预期结尾：

```text
ALL GOAL DELIVERABLE CHECKS PASSED
```

## 9. 安全与使用边界

- API Key 只从当前进程环境读取，不保存到状态、报告、日志或 Pipeline 子进程。
- LLM 只能组合已注册工具，不能生成任意 shell 或新代码执行。
- 缺少路径、孕周、图谱或运行环境时，系统应停止并展示缺失项。
- 自动 QC 是工程和技术完整性检查，不是胎儿发育常模。
- 在没有经验证的孕周常模、解剖标签映射、异常检测器和专家签署时，报告不会判断医学正常或异常。

<div align="center">

# Large language model assistance for report-based carotid plaque AHA classification: a multi-reader study

### 大语言模型辅助基于报告的颈动脉斑块 AHA 分型：一项多阅片者研究

[![已接受 · Insights into Imaging](https://img.shields.io/badge/Accepted-Insights_into_Imaging-276678?style=flat-square&labelColor=334155)](https://link.springer.com/journal/13244)
![影响因子 · 5.7](https://img.shields.io/badge/Impact_Factor-5.7-52796F?style=flat-square&labelColor=334155)
![JCR · Q1](https://img.shields.io/badge/JCR-Q1-6D597A?style=flat-square&labelColor=334155)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)](https://www.docker.com/)

**[English](README.md)** ·
**[论文](#引用)**

</div>

---

## 摘要

颈动脉粥样硬化斑块破裂是缺血性卒中的主要原因。基于高分辨率磁共振成像（HRMRI）的改良美国心脏协会（AHA）分型系统可实现超越狭窄程度的风险分层。然而，从自由文本报告中推断标准化AHA分型认知负荷高且高度依赖经验。

我们提出**标准引导提示（CGP, Criteria-Guided Prompting）**，将改良AHA分型标准显式嵌入LLM提示词中，引导模型将信号描述映射到斑块成分，再根据分型标准确定最终分型。本多中心读片人研究纳入了来自三家医疗机构的**433例患者（866条颈动脉）**。

<div align="center">

![研究流程](fig/fig2.svg)

**图2.** 总体研究流程与实验设计。**(a)** 参考标准建立。**(b)** AI独立性能评估：对比规则基线与10个LLM在朴素提示和标准引导提示下的表现。**(c)** 人机协作读片人研究：采用随机交叉设计，设置6周洗脱期。

</div>

---

## 核心结果

以下数值为研究结果摘要。本仓库提供 Web 应用、提示词和部署模板，未包含完整研究数据集或统计评估流程。

<table>
<tr>
<td width="50%" valign="top">

### 六分类准确率

| 模型 | 准确率 |
|:------|:--------:|
| DeepSeek-R1 (CGP) | **87.41%** |
| Qwen3-235B-Instruct (CGP) | 85.57% |
| GLM-4.5 (CGP) | 85.45% |
| Qwen3-8B (CGP) | 81.52% |

**Qwen3-8B** 在标准引导提示下从38.91%提升至**81.52%**（+42.6 pp）

</td>
<td width="50%" valign="top">

### 二分类性能（AUC）

| 任务 | 最佳模型 | AUC |
|:-----|:-----------|:---:|
| 进展性病变检测（III–VIII vs Normal/I–II） | GLM-4.5 | **0.992** |
| VI型复杂斑块检测（VI vs non-VI） | DeepSeek-R1 | **0.950** |

</td>
</tr>
</table>

### 多阅片者研究（n=4名放射科医师）

| 条件 | 准确率 | 加权κ |
|:----------|:--------:|:----------:|
| 无AI辅助 | 69.38% | 0.231 |
| DeepSeek-R1辅助 | **90.00%** | **0.775** |

- 初级医师：**+26 pp** 提升
- 高级医师：**+15 pp** 提升

DeepSeek-R1 辅助增加了研究中的判读时间（图3c），体现了准确率与耗时之间的权衡。

<div align="center">

![读片人研究表现](fig/figure_3.png)

**图3.** AI辅助下的读片人研究表现。**(a)** 血管水平和 **(b)** 患者水平六分类准确率。**(c)** 每例平均判读时间。**(d)** 诊断辅助效用评分（DAUS）分布。AI辅助提高了诊断准确率，初级医师获益最大。

</div>

---

## 方法学

### 标准引导提示（CGP）

CGP将改良AHA分型标准显式嵌入LLM提示词中，要求模型提供涵盖以下两步的结构化解释：

**步骤1：信号到成分映射**
- T1WI/T2WI信号模式 → 组织成分（脂质核心、纤维组织、钙化）
- 形态学特征 → 表面特征（溃疡、血栓）
- 强化模式 → 组织血管化和炎症

**步骤2：基于标准进行分型**
- 将报告中的成分及结构特征与提供的标准进行比较，确定AHA分型
- 生成结构化解释供审阅

该方法直接提供临床分型标准，无需微调或检索外部知识库。应用验证的是响应结构，不独立验证模型解释或分型的临床正确性。

---

## 改良AHA分型

| 类型 | 描述 | MRI特征 |
|:----:|:------------|:--------------------|
| **I-II** | 接近正常的管壁增厚 | 管壁厚度轻微增加 |
| **III** | 弥漫性内膜增厚/小偏心性斑块 | 无脂质核心的早期斑块 |
| **IV-V** | 含脂质/坏死核心的斑块 | T2WI低信号核心，无出血 |
| **VI** | 伴出血/血栓的复杂斑块 | 表面破裂，斑块内出血（T1WI高信号） |
| **VII** | 钙化斑块 | T1/T2极低信号（信号消失） |
| **VIII** | 无脂质核心的纤维斑块 | T2WI等信号，均匀强化 |

此表为简化概述。应用对报告文本进行分型，不直接分析 MRI 图像。

---

## 安装部署

### 环境要求

- Python 3.10+
- NVIDIA GPU（本地部署LLM时需要，可选）

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/Becomingw/CGP-Plaque.git
cd CGP-Plaque

# 创建独立环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置API（复制并编辑）
cp api_config_example.json api_config.json
# 编辑 api_config.json，填写端点、模型名称和 API 密钥

# 启动服务器
python app.py
# 服务器运行在 http://127.0.0.1:7860
```

### Docker部署

```bash
# 构建并运行
docker build -t aha-classifier .
docker run --rm -p 127.0.0.1:7860:7860 \
  -e API_KEY -e API_BASE_URL -e API_MODEL \
  aha-classifier
```

运行容器前，在 shell 中设置 `API_KEY`、`API_BASE_URL` 和 `API_MODEL`。镜像不包含本地 API 配置或用户数据。

---

## 环境变量配置

| 变量 | 说明 | 默认值 |
|:---------|:------------|:--------|
| `API_KEY` | LLM API密钥 | - |
| `API_BASE_URL` | API端点URL | - |
| `API_MODEL` | 模型名称 | - |
| `API_MAX_TOKENS` | 最大令牌数 | 4096 |
| `API_TEMPERATURE` | 采样温度 | 0.1 |
| `API_NO_THINK` | 是否附加提供商特定的 `/no_think` 指令 | false |
| `HOST` | Web 服务监听地址（Docker 中设为 `0.0.0.0`） | 127.0.0.1 |
| `PORT` | Web 服务端口 | 7860 |
| `ENABLE_EVALUATION_STORAGE` | 是否将提交的报告、模型输出和评分保存至 `user_data/` | false |

完整的 API 环境变量配置优先于 `api_config.json`。

### 数据处理

报告文本会发送至配置的 LLM API 端点，请使用去标识化输入。评估存储默认关闭；启用后会将提交的报告文本和模型输出写入本地 JSON 文件。应用没有用户身份认证，适用于本地研究。浏览器资源从 Google Fonts 和 unpkg 加载。

---

## 本地LLM部署（vLLM）

`deploy/` 目录包含使用 vLLM 本地部署模型的 Docker Compose 模板。请显式设置 `MODEL_DIR`、`VLLM_API_KEY` 和 `IMAGE`，选择兼容模型架构及 CUDA/GPU 环境的 vLLM 镜像；这些模板不代表已验证的全部研究运行环境。

```
deploy/
├── qwen3_8b/           # Qwen3-8B（推荐用于效率优化）
├── deepseek-r1/        # DeepSeek-R1（最高准确率）
├── deepseek-v3/
├── glm-4.5/
├── qwen3_235b_instruct/
├── qwen3_235b_thinking/
└── ...
```

**本地部署Qwen3-8B：**

```bash
cd deploy/qwen3_8b

# 配置环境变量
export MODEL_DIR=/path/to/qwen3_8b_weights
export VLLM_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export IMAGE='vllm/vllm-openai:<compatible-version>'
export CUDA_VISIBLE_DEVICES=0

# 启动服务
docker compose up -d

# 服务地址 http://localhost:9002
```

然后配置 `api_config.json`，使用上面生成的同一密钥。如果 Web 应用运行在容器内，`localhost` 指向该容器本身，应改为容器可访问的端点（例如 Docker Desktop 的 `host.docker.internal`）：

```json
{
  "api_configs": [{
    "name": "qwen3-8b-local",
    "base_url": "http://localhost:9002/v1",
    "api_key": "REPLACE_WITH_YOUR_VLLM_API_KEY",
    "model": "qwen3_8b",
    "enabled": true
  }],
  "use_name": "qwen3-8b-local"
}
```

---

## 引用

**Large language model assistance for report-based carotid plaque AHA classification: a multi-reader study.** _Insights into Imaging_. **已接受。**

正式出版信息公布后，将补充完整引用和 DOI。

---

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

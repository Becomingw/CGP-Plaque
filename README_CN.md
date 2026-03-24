<div align="center">

# 大语言模型辅助基于报告的颈动脉斑块AHA分型

### 多中心读片人研究

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)](https://www.docker.com/)

**[English](README.md)** ·
**[论文](#引用)**

[![Demo](https://img.shields.io/badge/🚀_在线演示-KGP--Plaque-brightgreen?style=for-the-badge)](https://spongebobkvin-kgp-plaque.hf.space/)
[![Hugging Face Space](https://img.shields.io/badge/🤗_Hugging_Face-Space-yellow?style=for-the-badge)](https://huggingface.co/spaces/SpongeBobkvin/KGP-Plaque)
[![Password](https://img.shields.io/badge/🔑_访问密码-REMOVED_ACCESS_CODE-blue?style=for-the-badge)]()

</div>

---

## 摘要

颈动脉粥样硬化斑块破裂是缺血性卒中的主要原因。基于高分辨率磁共振成像（HRMRI）的改良美国心脏协会（AHA）分型系统可实现超越狭窄程度的风险分层。然而，从自由文本报告中推断标准化AHA分型认知负荷高且高度依赖经验。

我们提出**标准引导提示（CGP, Criteria-Guided Prompting）**，将改良AHA分型标准显式嵌入LLM提示词中，将任务分解为两个可审计的步骤——将信号描述映射到斑块成分，然后应用层级标准确定最终分型。本多中心读片人研究纳入了来自三家医疗机构的**433例患者（866条颈动脉）**。

<div align="center">

![研究流程](fig/fig2.svg)

**图2.** 总体研究流程与实验设计。**(a)** 参考标准建立。**(b)** AI独立性能评估：对比规则基线与10个LLM在朴素提示和标准引导提示下的表现。**(c)** 人机协作读片人研究：采用随机交叉设计，设置6周洗脱期。

</div>

---

## 核心结果

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

### 临床验证（多阅片者研究，n=4名放射科医师）

| 条件 | 准确率 | 加权κ |
|:----------|:--------:|:----------:|
| 无AI辅助 | 69.38% | 0.231 |
| DeepSeek-R1辅助 | **90.00%** | **0.775** |

- 初级医师：**+26 pp** 提升
- 高级医师：**+15 pp** 提升

<div align="center">

![读片人研究表现](fig/figure_3.png)

**图3.** AI辅助下的读片人研究表现。**(a)** 血管水平和 **(b)** 患者水平六分类准确率。**(c)** 每例平均判读时间。**(d)** 诊断辅助效用评分（DAUS）分布。AI辅助提高了诊断准确率，初级医师获益最大。

</div>

---

## 方法学

### 标准引导提示（CGP）

CGP将改良AHA分型标准显式嵌入LLM提示词中，引导模型通过两步可审计推理过程：

**步骤1：信号到成分映射**
- T1WI/T2WI信号模式 → 组织成分（脂质核心、纤维组织、钙化）
- 形态学特征 → 表面特征（溃疡、血栓）
- 强化模式 → 组织血管化和炎症

**步骤2：层级标准应用**
- 按优先级顺序应用预定义分类规则，确定最终AHA分型
- 生成结构化推理链供临床审阅

该方法使模型输出与既定临床规则对齐，无需微调或外部知识库。

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

> **临床意义**：VI型（伴斑块内出血的复杂斑块）使缺血风险增加5-6倍。

---

## 安装部署

### 环境要求

- Python 3.8+
- NVIDIA GPU（本地部署LLM时需要，可选）

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/your-repo/LLMAHA_Web.git
cd LLMAHA_Web

# 安装依赖
pip install -r requirements.txt

# 配置API（复制并编辑）
cp api_config.example.json api_config.json

# 启动服务器
python app.py
# 服务器运行在 http://127.0.0.1:7860
```

### Docker部署

```bash
# 构建并运行
docker build -t aha-classifier .
docker run -p 7860:7860 \
  -e API_KEY=your-api-key \
  -e API_BASE_URL=https://api.example.com/v1 \
  -e API_MODEL=model-name \
  aha-classifier
```

---

## 环境变量配置

| 变量 | 说明 | 默认值 |
|:---------|:------------|:--------|
| `API_KEY` | LLM API密钥 | - |
| `API_BASE_URL` | API端点URL | - |
| `API_MODEL` | 模型名称 | - |
| `API_MAX_TOKENS` | 最大令牌数 | 4096 |
| `API_TEMPERATURE` | 采样温度 | 0.1 |

---

## 本地LLM部署（vLLM）

`deploy/` 目录包含使用vLLM在本地部署模型的Docker Compose配置：

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
export VLLM_API_KEY=your-secret-key
export CUDA_VISIBLE_DEVICES=0

# 启动服务
docker-compose up -d

# 服务地址 http://localhost:9002
```

然后配置 `api_config.json`：

```json
{
  "api_configs": [{
    "name": "qwen3-8b-local",
    "base_url": "http://localhost:9002/v1",
    "api_key": "your-secret-key",
    "model": "qwen3_8b",
    "enabled": true
  }],
  "use_name": "qwen3-8b-local"
}
```

---

## 在线演示

在Hugging Face Spaces上试用交互式演示：

[![Demo](https://img.shields.io/badge/🚀_在线演示-KGP--Plaque-brightgreen?style=for-the-badge)](https://spongebobkvin-kgp-plaque.hf.space/)
[![Hugging Face Space](https://img.shields.io/badge/🤗_Hugging_Face-Space-yellow?style=for-the-badge)](https://huggingface.co/spaces/SpongeBobkvin/KGP-Plaque)
[![Password](https://img.shields.io/badge/🔑_访问密码-REMOVED_ACCESS_CODE-blue?style=for-the-badge)]()

---

## 引用

```bibtex
@article{cgp-aha-2026,
  title={Large Language Model Assistance for Report-Based Carotid Plaque
         AHA Classification: Multicenter Reader Study},
  author={...},
  journal={Insights into Imaging},
  year={2026}
}
```

---

## 许可证

本项目采用 MIT 许可证。

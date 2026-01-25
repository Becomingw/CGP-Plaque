<div align="center">

# Knowledge-Guided Large Language Models for Automated Modified AHA Classification of Carotid Plaque

### A Multicenter Validation Study

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)](https://www.docker.com/)

**[中文文档](README_CN.md)** ·
**[Live Demo](https://huggingface.co/spaces/your-space)** ·
**[Paper](#citation)**

</div>

---

## Abstract

Carotid atherosclerotic plaque rupture is a leading cause of ischemic stroke. The modified American Heart Association (AHA) classification based on high-resolution magnetic resonance imaging (HRMRI) enables risk stratification beyond stenosis degree. However, manual classification from free-text reports is time-consuming and yields suboptimal inter-rater consistency.

We introduce **Knowledge-Guided Prompting (KGP)**, which embeds structured classification criteria into LLM prompts to enable accurate automated classification with traceable reasoning chains. This multicenter validation study includes **433 patients (866 carotid vessels)** from three medical centers.

<div align="center">

![Study Workflow](fig/fig_1_pipeline.svg)

**Figure 1.** Study design and Knowledge-Guided Prompting framework

</div>

---

## Key Results

<table>
<tr>
<td width="50%" valign="top">

### Six-Class Classification

| Model | Accuracy |
|:------|:--------:|
| DeepSeek-R1 (KGP) | **87.41%** |
| Qwen3-235B-Instruct (KGP) | 85.57% |
| GLM-4.5 (KGP) | 85.45% |
| Qwen3-8B (KGP) | 81.52% |

**Qwen3-8B** improved from 38.91% to **81.52%** (+42.6 pp) with knowledge guidance.

</td>
<td width="50%" valign="top">

### Binary Classification (AUC)

| Task | Best Model | AUC |
|:-----|:-----------|:---:|
| Significant Plaques (III-VIII) | GLM-4.5 | **0.992** |
| Type VI Complex Plaques | DeepSeek-R1 | **0.950** |

</td>
</tr>
</table>

### Clinical Validation (Reader Study, n=4 radiologists)

| Condition | Accuracy | Weighted κ |
|:----------|:--------:|:----------:|
| Without AI | 69.38% | 0.231 |
| With DeepSeek-R1 | **90.00%** | **0.775** |

- Junior physicians: **+26 pp** improvement
- Senior physicians: **+15 pp** improvement

<div align="center">

![Performance Comparison](fig/fig2_bar_chart.png)

**Figure 2.** Six-class modified AHA classification performance comparison across models

</div>

---

## Methodology

### Knowledge-Guided Prompting (KGP)

KGP embeds structured classification criteria directly into prompts, guiding LLMs through a two-step reasoning process:

**Step 1: Signal-to-Component Mapping**
- T1WI/T2WI signal patterns → Tissue composition (lipid core, fibrous tissue, calcification)
- Morphological features → Surface characteristics (ulceration, thrombosis)
- Enhancement patterns → Tissue vascularity and inflammation

**Step 2: Component-to-Type Assignment**
- Synthesize identified components based on dominant pathological features
- Apply differential criteria to determine final AHA classification

This approach provides a lightweight alternative to RAG without external infrastructure.

---

## Modified AHA Classification

| Type | Description | MRI Characteristics |
|:----:|:------------|:--------------------|
| **I-II** | Near-normal wall thickening | Minimal wall thickness increase |
| **III** | Diffuse intimal thickening / small eccentric plaque | Early plaque without lipid core |
| **IV-V** | Plaque with lipid/necrotic core | T2WI low signal core, no hemorrhage |
| **VI** | Complex plaque with hemorrhage/thrombosis | Surface rupture, IPH (T1WI high signal) |
| **VII** | Calcified plaque | T1/T2 extremely low signal (signal void) |
| **VIII** | Fibrous plaque without lipid core | T2WI isointense, homogeneous enhancement |

> **Clinical Significance**: Type VI (complex plaques with IPH) increases ischemic risk by 5-6 fold.

---

## Installation

### Prerequisites

- Python 3.8+
- NVIDIA GPU (for local LLM deployment, optional)

### Local Development

```bash
# Clone repository
git clone https://github.com/your-repo/LLMAHA_Web.git
cd LLMAHA_Web

# Install dependencies
pip install -r requirements.txt

# Configure API (copy and edit)
cp api_config.example.json api_config.json

# Run server
python app.py
# Server runs at http://127.0.0.1:7860
```

### Docker Deployment

```bash
# Build and run
docker build -t aha-classifier .
docker run -p 7860:7860 \
  -e API_KEY=your-api-key \
  -e API_BASE_URL=https://api.example.com/v1 \
  -e API_MODEL=model-name \
  aha-classifier
```

---

## Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `API_KEY` | LLM API key | - |
| `API_BASE_URL` | API endpoint URL | - |
| `API_MODEL` | Model name | - |
| `API_MAX_TOKENS` | Maximum tokens | 4096 |
| `API_TEMPERATURE` | Sampling temperature | 0.1 |

---

## Local LLM Deployment (vLLM)

The `deploy/` directory contains Docker Compose configurations for deploying models locally with vLLM:

```
deploy/
├── qwen3_8b/           # Qwen3-8B (recommended for efficiency)
├── deepseek-r1/        # DeepSeek-R1 (highest accuracy)
├── deepseek-v3/
├── glm-4.5/
├── qwen3_235b_instruct/
├── qwen3_235b_thinking/
└── ...
```

**Deploy Qwen3-8B locally:**

```bash
cd deploy/qwen3_8b

# Configure environment
export MODEL_DIR=/path/to/qwen3_8b_weights
export VLLM_API_KEY=your-secret-key
export CUDA_VISIBLE_DEVICES=0

# Start service
docker-compose up -d

# Service available at http://localhost:9002
```

Then configure your `api_config.json`:

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

## Live Demo

Try the interactive demo on Hugging Face Spaces: [Demo Link](https://huggingface.co/spaces/your-space)

---

## Citation

```bibtex
@article{kgp-aha-2025,
  title={Knowledge-Guided Large Language Models for Automated Modified AHA
         Classification of Carotid Plaque from Free-Text MRI Reports:
         A Multicenter Validation Study},
  author={...},
  journal={...},
  year={2025}
}
```

---

## License

This project is licensed under the MIT License.

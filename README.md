<div align="center">

# Large language model assistance for report-based carotid plaque AHA classification: a multi-reader study

[![Accepted · Insights into Imaging](https://img.shields.io/badge/Accepted-Insights_into_Imaging-276678?style=flat-square&labelColor=334155)](https://link.springer.com/journal/13244)
![Impact Factor · 5.7](https://img.shields.io/badge/Impact_Factor-5.7-52796F?style=flat-square&labelColor=334155)
![JCR · Q1](https://img.shields.io/badge/JCR-Q1-6D597A?style=flat-square&labelColor=334155)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)](https://www.docker.com/)

**[中文文档](README_CN.md)** ·
**[Paper](#citation)**

</div>

---

## Abstract

Carotid atherosclerotic plaque rupture is a leading cause of ischemic stroke. The modified American Heart Association (AHA) classification based on high-resolution magnetic resonance imaging (HRMRI) enables risk stratification beyond stenosis degree. However, inferring standardized AHA classification from free-text reports is cognitively demanding and highly experience-dependent.

We propose **Criteria-Guided Prompting (CGP)**, which explicitly embeds the modified AHA classification criteria into LLM prompts, guiding the model to map signal descriptions to plaque components and apply the classification criteria to assign the final type. This multicenter reader study includes **433 patients (866 carotid vessels)** from three institutions.

<div align="center">

![Study Workflow](fig/fig2.svg)

**Figure 2.** Overall study workflow and experimental design. **(a)** Reference standard establishment. **(b)** Standalone AI performance evaluation comparing a rule-based baseline against 10 LLMs under naive and criteria-guided prompting. **(c)** Human–AI collaboration reader study with a randomized crossover design and 6-week washout period.

</div>

---

## Key Results

The following values summarize the study results. This repository provides the web application, prompts, and deployment templates; it does not include the full study dataset or the statistical evaluation pipeline.

<table>
<tr>
<td width="50%" valign="top">

### Six-Class Classification

| Model | Accuracy |
|:------|:--------:|
| DeepSeek-R1 (CGP) | **87.41%** |
| Qwen3-235B-Instruct (CGP) | 85.57% |
| GLM-4.5 (CGP) | 85.45% |
| Qwen3-8B (CGP) | 81.52% |

**Qwen3-8B** improved from 38.91% to **81.52%** (+42.6 pp) with criteria-guided prompting.

</td>
<td width="50%" valign="top">

### Binary Classification (AUC)

| Task | Best Model | AUC |
|:-----|:-----------|:---:|
| Advanced Lesion Detection (III–VIII vs Normal/I–II) | GLM-4.5 | **0.992** |
| Type VI Complex Plaque Detection (VI vs non-VI) | DeepSeek-R1 | **0.950** |

</td>
</tr>
</table>

### Reader Study (n=4 radiologists)

| Condition | Accuracy | Weighted κ |
|:----------|:--------:|:----------:|
| Without AI | 69.38% | 0.231 |
| With DeepSeek-R1 | **90.00%** | **0.775** |

- Junior physicians: **+26 pp** improvement
- Senior physicians: **+15 pp** improvement

DeepSeek-R1 assistance increased interpretation time in the reader study (Figure 3c), indicating an accuracy–time trade-off.

<div align="center">

![Reader Study Performance](fig/figure_3.png)

**Figure 3.** Reader study performance with AI assistance. **(a)** Vessel-level and **(b)** patient-level six-class accuracy for junior and senior radiologists under three conditions: no AI, Qwen3-8B assistance, and DeepSeek-R1 assistance. **(c)** Mean interpretation time per case. **(d)** Distribution of Diagnostic Assistance Utility Score (DAUS). AI assistance improved accuracy with larger gains in junior radiologists.

</div>

---

## Methodology

### Criteria-Guided Prompting (CGP)

CGP explicitly embeds the modified AHA classification criteria into LLM prompts, requesting a structured explanation covering two steps:

**Step 1: Signal-to-Component Mapping**
- T1WI/T2WI signal patterns → Tissue composition (lipid core, fibrous tissue, calcification)
- Morphological features → Surface characteristics (ulceration, thrombosis)
- Enhancement patterns → Tissue vascularity and inflammation

**Step 2: Criteria-Based Classification**
- Compare the described components and structural features against the supplied criteria to assign an AHA type
- Generate a structured explanation for review

This approach supplies clinical criteria without requiring fine-tuning or retrieval from an external knowledge base. The application validates the response structure; it does not independently verify the clinical correctness of the model's explanation or classification.

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

This table is a simplified overview. The application classifies report text; it does not analyze MRI images directly.

---

## Installation

### Prerequisites

- Python 3.10+
- NVIDIA GPU (for local LLM deployment, optional)

### Local Development

```bash
# Clone repository
git clone https://github.com/Becomingw/CGP-Plaque.git
cd CGP-Plaque

# Create an isolated environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API (copy and edit)
cp api_config_example.json api_config.json
# Edit api_config.json with your endpoint, model, and API key

# Run server
python app.py
# Server runs at http://127.0.0.1:7860
```

### Docker Deployment

```bash
# Build and run
docker build -t aha-classifier .
docker run --rm -p 127.0.0.1:7860:7860 \
  -e API_KEY -e API_BASE_URL -e API_MODEL \
  aha-classifier
```

Set `API_KEY`, `API_BASE_URL`, and `API_MODEL` in your shell before running the container. The container does not include your local API configuration or user data.

---

## Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `API_KEY` | LLM API key | - |
| `API_BASE_URL` | API endpoint URL | - |
| `API_MODEL` | Model name | - |
| `API_MAX_TOKENS` | Maximum tokens | 4096 |
| `API_TEMPERATURE` | Sampling temperature | 0.1 |
| `API_NO_THINK` | Append the provider-specific `/no_think` directive | false |
| `HOST` | Web server bind address (Docker sets `0.0.0.0`) | 127.0.0.1 |
| `PORT` | Web server port | 7860 |
| `ENABLE_EVALUATION_STORAGE` | Enable saving submitted reports, model outputs, and ratings in `user_data/` | false |

Complete environment-based API settings take precedence over `api_config.json`.

### Data handling

Report text is sent to the configured LLM API endpoint. Use de-identified inputs. Evaluation storage is disabled by default; enabling it writes submitted report text and model outputs to local JSON files. The application has no user authentication and is intended for local research use. Browser assets are loaded from Google Fonts and unpkg.

---

## Local LLM Deployment (vLLM)

The `deploy/` directory contains Docker Compose templates for deploying models locally with vLLM. Set `MODEL_DIR`, `VLLM_API_KEY`, and `IMAGE` explicitly. Choose a vLLM image compatible with the model architecture and your CUDA/GPU setup; these templates are not verified reproductions of all study environments.

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
export VLLM_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export IMAGE='vllm/vllm-openai:<compatible-version>'
export CUDA_VISIBLE_DEVICES=0

# Start service
docker compose up -d

# Service available at http://localhost:9002
```

Then configure your `api_config.json`, using the same key generated above. For a containerized web application, `localhost` refers to that container; use an endpoint reachable from it (for example, `host.docker.internal` on Docker Desktop):

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

## Citation

**Large language model assistance for report-based carotid plaque AHA classification: a multi-reader study.** _Insights into Imaging_. **Accepted.**

The complete citation and DOI will be added when publication details are available.

---

## License

This project is licensed under the [MIT License](LICENSE).

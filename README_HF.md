---
title: MRI AHA Plaque Classification
emoji: 🩺
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

<div align="center">

# LLM-Assisted Carotid Plaque AHA Classification

Live demo for the research paper: *Large Language Model Assistance for Report-Based Carotid Plaque AHA Classification: Multicenter Reader Study*

**[GitHub Repository](https://github.com/WangMemPhy/KGP-Plaque)** · **[Paper](#citation)**

</div>

---

## About This Demo

This interactive demo allows you to test our Criteria-Guided Prompting (CGP) approach for report-based carotid plaque AHA classification from MRI reports.

### Key Features

- **Bilingual Interface**: Switch between Chinese/English
- **Prompt Comparison**: Toggle between Naive Prompting (NP) and Criteria-Guided Prompting (CGP)
- **Example Cases**: Pre-loaded clinical cases from validation study
- **Traceable Reasoning**: View AI's step-by-step reasoning process

### Performance Highlights

| Model | Accuracy | Notes |
|:------|:--------:|:------|
| DeepSeek-R1 (CGP) | **87.41%** | Highest accuracy |
| Qwen3-8B (CGP) | **81.52%** | +42.6 pp improvement with CGP |
| Clinical Validation | **90.00%** | Physician accuracy with AI assistance |

---

## How to Use

1. **Select Language**: Choose Chinese (中文) or English
2. **Choose Prompt Version**: 
   - **NP**: Naive Prompting (baseline)
   - **CGP**: Criteria-Guided Prompting (recommended)
3. **Input MRI Findings**: 
   - Click on example cases, or
   - Enter custom MRI report text
4. **Analyze**: Click "启动AI分析" / "Start AI Analysis"
5. **Review Results**: 
   - View AHA classification for left/right carotid arteries
   - Read AI's reasoning process
   - Optionally rate AI usefulness

---

## Modified AHA Classification

| Type | Description |
|:----:|:------------|
| **I-II** | Near-normal wall thickening |
| **III** | Diffuse intimal thickening / small eccentric plaque |
| **IV-V** | Plaque with lipid/necrotic core |
| **VI** | Complex plaque with hemorrhage/thrombosis (high risk) |
| **VII** | Calcified plaque |
| **VIII** | Fibrous plaque without lipid core |

---

## Citation

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

## License

MIT License

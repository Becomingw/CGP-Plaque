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

# Knowledge-Guided LLMs for Carotid Plaque Classification

Live demo for the research paper: *Knowledge-Guided Large Language Models for Automated Modified AHA Classification of Carotid Plaque from Free-Text MRI Reports: A Multicenter Validation Study*

**[GitHub Repository](https://github.com/WangMemPhy/KGP-Plaque)** · **[Paper](#citation)**

</div>

---

## About This Demo

This interactive demo allows you to test our Knowledge-Guided Prompting (KGP) approach for automated carotid plaque classification from MRI reports.

### Key Features

- **Bilingual Interface**: Switch between Chinese/English
- **Prompt Comparison**: Toggle between Naive Prompting (NP) and Knowledge-Guided Prompting (KGP)
- **Example Cases**: Pre-loaded clinical cases from validation study
- **Traceable Reasoning**: View AI's step-by-step reasoning process

### Performance Highlights

| Model | Accuracy | Notes |
|:------|:--------:|:------|
| DeepSeek-R1 (KGP) | **87.41%** | Highest accuracy |
| Qwen3-8B (KGP) | **81.52%** | +42.6 pp improvement with KGP |
| Clinical Validation | **90.00%** | Physician accuracy with AI assistance |

---

## How to Use

1. **Select Language**: Choose Chinese (中文) or English
2. **Choose Prompt Version**: 
   - **NP**: Naive prompting (baseline)
   - **KGP**: Knowledge-Guided Prompting (recommended)
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

MIT License

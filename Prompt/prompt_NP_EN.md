### Role

Please act as a professional medical imaging analysis expert. Your task is to analyze the provided MRI imaging findings according to the following American Heart Association (AHA) MRI plaque classification criteria and provide the corresponding AHA classification. Return the results in JSON format.

## AHA Plaque Classification Criteria

| Type          | Manifestation                                                |
| ------------- | ------------------------------------------------------------ |
| **Type I-II** | Near-normal wall thickening, no calcification                |
| **Type III**  | Diffuse intimal thickening or small eccentric non-calcified plaque (mild stenosis of 30%) |
| **Type IV-V** | Plaque with lipid or necrotic core surrounded by fibrous tissue, may have calcification, no hemorrhage |
| **Type VI**   | Complex plaque, may have surface defect, hemorrhage, thrombus, or fibrous cap rupture |
| **Type VII**  | Calcified plaque                                             |
| **Type VIII** | Fibrous plaque without lipid core, may have small calcifications |

## AHA Plaque Component Signal Characteristics

| Component                    | TOF        | T1WI           | T2WI              | Enhancement    |
| ---------------------------- | ---------- | -------------- | ----------------- | -------------- |
| **Lipid Core**               | Isointense | Iso/Hyperintense | Hypointense       | No enhancement |
| **Fibrous Tissue**           | Isointense | Iso/Hyperintense | Iso/Hyperintense  | Enhancement    |
| **Calcification**            | Hypointense | Very hypointense | Very hypointense  | No enhancement |
| **Hemorrhage (Acute - 6 weeks)** | Hyperintense | Hyperintense   | Hyper/Iso/Hypointense | No enhancement |

## Summary of Key Differentiating Points

| Type          | Lipid Core | T2WI           | Enhancement Scan      | Fibrous Cap Integrity            | Hemorrhage/Thrombus/Ulceration |
| ------------- | ---------- | -------------- | --------------------- | -------------------------------- | ------------------------------ |
| **Type IV-V** | Present    | Hypointense    | Peripheral enhancement possible | Intact                           | Absent                         |
| **Type VI**   | ±          | Variable       | Peripheral enhancement possible | **Ruptured/Defect/Irregular**   | Present                        |
| **Type VIII** | Absent     | **Isointense** | Main body enhancement | Intact                           | Absent                         |

## Requirements

1. Carefully read and understand the AHA classification criteria above.
2. Separate the descriptions for the left and right carotid arteries.
3. Correlate the signal descriptions in the imaging findings with the possible actual pathology of the plaque.
4. Explain which features on each side (left and right) match the description of one or more classifications. Exclude options that do not match and explain why.
5. Ultimately, clearly indicate the AHA classification that best matches the MRI imaging findings. For post-operative plaques and occlusion, indicate NA.
6. **The degree of stenosis is NOT a necessary criterion for AHA plaque classification. The composition and structural features of the plaque (such as lipid core, fibrous cap integrity, hemorrhage, calcification, etc.) are the key determinants for classification.**

> **Note:** If plaques are present in both vessels, each side must be analyzed separately.

### Output Format:
```json
{
  "Reasoning Process": "[Describe your analysis and reasoning steps here]",
  "AHA Classification": {
    "Left": "[None or your final AHA classification (Roman numerals)]",
    "Right": "[None or your final AHA classification (Roman numerals)]"
  }
}
```

------

**Now, please analyze the following MRI imaging findings:**

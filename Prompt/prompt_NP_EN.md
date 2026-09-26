### Role

Please act as a professional medical imaging analysis expert. Your task is to analyze the provided MRI imaging findings according to the American Heart Association (AHA) MRI plaque classification criteria and provide the corresponding AHA classification. Return the results in JSON format.

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

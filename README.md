# AHA UI - Medical Imaging AHA Classification System

A web-based AI-assisted plaque classification interface for MRI carotid artery images based on the American Heart Association (AHA) plaque typing standards (Types I-VIII).

[中文文档](README_CN.md)

## Features

- **Bilingual Interface**: Full Chinese/English language support with one-click toggle
- **Dual Input Modes**: Excel batch mode and custom input mode for flexible data entry
- **AI-Assisted Classification**: LLM-powered inference with structured AHA typing output
- **Multi-User Support**: Independent progress tracking per user with JSON persistence
- **Real-time Timer**: Tracks evaluation time per patient for workflow analysis
- **Excel Export**: Export all evaluations (both Excel and custom) to spreadsheet format

## Screenshots

| Login | Patient Information (Chinese) | Patient Information (English) |
|:---:|:---:|:---:|
| ![Login](fig/登陆.png) | ![Patient Info CN](fig/病人信息中文.png) | ![Patient Info EN](fig/病人信息英文.png) |

| Doctor Assessment (Chinese) | Doctor Assessment (English) | Custom Input Mode |
|:---:|:---:|:---:|
| ![Assessment CN](fig/推理中文.png) | ![Assessment EN](fig/推理英文.png) | ![Custom Mode](fig/自定义信息.png) |

## Project Structure

```
LLMAHA_Web/
├── app.py                  # Flask backend application
├── run_production.py       # Production server (Waitress WSGI)
├── requirements.txt        # Python dependencies
├── api_config.json         # API configuration (create from example)
├── api_config_example.json # Example API configuration template
├── prompt_9.md             # AI system prompt for AHA classification
├── test200.xlsx            # Sample patient data (Excel format)
├── static/
│   ├── index.html          # Main frontend page
│   ├── js/
│   │   └── app.js          # Vue.js 3 application with i18n
│   └── css/
│       └── style.css       # UI styling
├── user_data/              # Auto-created directory for user progress
│   ├── {username}.json     # Excel mode evaluation progress
│   └── {username}_custom.json  # Custom mode evaluations
└── fig/                    # Documentation screenshots
```

## Deployment Guide

### 1. Prerequisites

- Python 3.8+
- pip package manager

### 2. Clone and Install Dependencies

```bash
git clone <repository-url>
cd LLMAHA_Web
uv pip install -r requirements.txt
```

Required packages:
- flask
- flask-cors
- pandas
- openpyxl
- openai
- pydantic
- waitress

### 3. Configure API

Copy and edit the API configuration file:

```bash
cp api_config_example.json api_config.json
```

Edit `api_config.json` to add your LLM API credentials:

```json
{
  "api_configs": [
    {
      "name": "your-api-name",
      "base_url": "https://api.example.com/v1",
      "api_key": "your-api-key-here",
      "model": "model-name",
      "max_tokens": 2000,
      "temperature": 0.3,
      "timeout": 30,
      "enabled": true
    }
  ],
  "use_name": "your-api-name"
}
```

**Supported API providers:**
- OpenAI / OpenAI-compatible APIs
- SiliconFlow
- DeepSeek
- Local LLM deployments (Ollama, vLLM, etc.)

### 4. Prepare Data File

Place your patient data Excel file in the project root. The file must contain:
- Column `条码号` (Barcode): Patient identifier
- Column `检查所见` (Examination Findings): MRI findings text

Default file path: `test200.xlsx`

To change the data file path, edit `TABLE_PATH` in `app.py` (line 147).

### 5. Start the Server

**Development mode** (single-threaded, with debug):
```bash
python app.py
# Server runs at http://127.0.0.1:5001
```

**Production mode** (multi-threaded, recommended):
```bash
python run_production.py
# Server runs at http://0.0.0.0:5001
```

Production mode uses Waitress WSGI server with:
- 4 concurrent threads
- 60-second channel timeout for AI inference
- Accessible from network (0.0.0.0)

## Usage Guide

### Step 1: Login

1. Open browser and navigate to `http://localhost:5001`
2. Enter your username (any string, used for progress tracking)
3. Click "Login" button

### Step 2: Choose Input Mode

- **Excel Mode**: Load patients from the Excel data file sequentially
- **Custom Input Mode**: Manually enter examination findings for ad-hoc analysis

### Step 3: Review Patient Information

In Excel mode:
- View current patient's barcode and examination findings
- Use "Previous/Next" buttons or enter barcode to jump to specific patient
- Progress indicator shows current position (e.g., "1/200")

### Step 4: AI-Assisted Classification

1. Click "Start AI Analysis" button
2. Wait for the LLM to analyze the examination findings
3. Review the AI's reasoning and suggested AHA classifications

### Step 5: Doctor Assessment

1. Adjust AHA classification sliders for left and right carotid arteries (I-VIII)
2. Rate AI usefulness (0-5 scale) for each side
3. Timer tracks time spent on current patient

### Step 6: Submit and Navigate

1. Click "Submit" to save the evaluation
2. Click "Next Patient" to proceed to the next case
3. Progress is automatically saved to `user_data/{username}.json`

### Step 7: Export Results

Click "Export Results" to download an Excel file containing:
- Sheet 1: Excel mode evaluations with all patient data
- Sheet 2: Custom mode evaluations (if any)

## AHA Classification Reference

| Type | Description | MRI Characteristics |
|:---:|:---|:---|
| I-II | Near-normal wall thickening | Minimal changes |
| III | Diffuse intimal thickening / small eccentric plaque | Early plaque formation |
| IV-V | Plaque with lipid/necrotic core | T2WI low signal, no hemorrhage |
| VI | Complex plaque with hemorrhage/thrombosis | Surface defects, intraplaque hemorrhage |
| VII | Calcified plaque | T1/T2 extremely low signal |
| VIII | Fibrous plaque without lipid core | T2WI isointense, enhancement |

## API Endpoints

| Endpoint | Method | Description |
|:---|:---:|:---|
| `/api/login` | POST | User login, load Excel data |
| `/api/patient/navigate` | POST | Navigate to next/prev patient |
| `/api/patient/jump` | POST | Jump to specific barcode |
| `/api/submit` | POST | Submit evaluation (Excel mode) |
| `/api/custom/submit` | POST | Submit evaluation (Custom mode) |
| `/api/custom/list` | POST | List all custom evaluations |
| `/api/export` | POST | Export results to Excel |
| `/api/infer` | POST | Call AI for classification |
| `/api/infer/test` | POST | Mock AI response (testing) |
| `/api/mode/switch` | POST | Switch between Excel/Custom mode |

## Testing

Test the AI inference endpoint without consuming API credits:

```bash
curl -X POST http://localhost:5001/api/infer/test \
  -H "Content-Type: application/json" \
  -d '{"findings": "test examination findings"}'
```

## License

MIT License

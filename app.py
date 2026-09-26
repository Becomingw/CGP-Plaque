from flask import Flask, jsonify, request
from openai import OpenAI
import os
import json
import time
import logging
import re
import uuid
from pydantic import BaseModel, Field, ValidationError, ConfigDict


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Pydantic Models for AI Response Validation ---

class AHAClassificationZH(BaseModel):
    """AHA分型结果模型 (中文)"""
    左侧: str = Field(..., min_length=1, description="左侧颈动脉AHA分型")
    右侧: str = Field(..., min_length=1, description="右侧颈动脉AHA分型")

class AHAClassificationEN(BaseModel):
    """AHA Classification Model (English)"""
    Left: str = Field(..., min_length=1, description="Left carotid AHA classification")
    Right: str = Field(..., min_length=1, description="Right carotid AHA classification")

class AIInferenceResponseZH(BaseModel):
    """AI推理响应的完整模型 (中文)"""
    model_config = ConfigDict(extra="ignore")
    推理过程: str = Field(..., min_length=1, description="AI分析推理的详细过程")
    AHA分型: AHAClassificationZH = Field(..., description="左右侧AHA分型结果")

class AIInferenceResponseEN(BaseModel):
    """AI Inference Response Model (English)"""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    Reasoning_Process: str = Field(..., min_length=1, alias="Reasoning Process", description="AI reasoning process")
    AHA_Classification: AHAClassificationEN = Field(..., alias="AHA Classification", description="AHA classification results")

def validate_and_parse_ai_response(raw_response: str, language: str = "zh") -> dict:
    """
    验证并解析AI响应，确保结构正确 (支持中英文)
    """
    result = {
        "success": False,
        "data": None,
        "raw": raw_response,
        "error": None
    }

    if not isinstance(raw_response, str) or not raw_response.strip():
        result["error"] = "Empty model response"
        return result

    # 尝试直接解析JSON
    parsed_json = None
    try:
        parsed_json = json.loads(raw_response)
    except json.JSONDecodeError:
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw_response)
        if json_match:
            try:
                parsed_json = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                result["error"] = "Invalid JSON in model response"
                logger.warning(result["error"])
        else:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_response)
            if json_match:
                try:
                    parsed_json = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    result["error"] = "Invalid JSON in model response"
                    logger.warning(result["error"])
            else:
                result["error"] = "未找到有效的JSON格式"
                logger.warning(result["error"])

    if not isinstance(parsed_json, dict):
        result["error"] = "Model response must be a JSON object"
        return result

    try:
        if language == "en":
            validated_data = AIInferenceResponseEN(**parsed_json)
            result["data"] = {
                "Reasoning Process": validated_data.Reasoning_Process,
                "AHA Classification": {
                    "Left": validated_data.AHA_Classification.Left,
                    "Right": validated_data.AHA_Classification.Right
                }
            }
        else:
            validated_data = AIInferenceResponseZH(**parsed_json)
            result["data"] = validated_data.model_dump()

        result["success"] = True
        logger.info("AI响应验证成功")
    except ValidationError:
        # ValidationError includes input values; do not log report/model content.
        result["error"] = "Model response is missing required fields or has invalid field types"
        logger.warning("Model response schema validation failed")

    return result


# --- Flask App Setup ---

app = Flask(__name__, static_folder='static')
app.config["MAX_CONTENT_LENGTH"] = 128 * 1024
app.config["ENABLE_EVALUATION_STORAGE"] = os.environ.get("ENABLE_EVALUATION_STORAGE", "false").lower() == "true"

# --- Configuration ---

USER_DATA_PATH = os.path.join(os.path.dirname(__file__), "user_data")
AHA_LABELS = {"I-II", "III", "IV-V", "VI", "VII", "VIII", "None", "NA"}

# Load prompts for both languages and both versions
PROMPT_DIR = os.path.join(os.path.dirname(__file__), "Prompt")
PROMPTS = {}
LANG_SUFFIX = {"zh": "CN", "en": "EN"}
for version in ["NP", "CGP"]:
    PROMPTS[version] = {}
    for lang in ["zh", "en"]:
        suffix = LANG_SUFFIX[lang]
        prompt_file = f"prompt_{version}_{suffix}.md"
        prompt_path = os.path.join(PROMPT_DIR, prompt_file)
        with open(prompt_path, "r", encoding="utf-8") as f:
            PROMPTS[version][lang] = f.read()

# Load examples
EXAMPLES_PATH = os.path.join(os.path.dirname(__file__), "static", "data", "examples.json")
with open(EXAMPLES_PATH, "r", encoding="utf-8") as f:
    EXAMPLES_DATA = json.load(f)

# --- API Configuration ---

# Try to load a complete configuration from environment variables first
API_KEY = os.environ.get("API_KEY", "")
BASE_URL = os.environ.get("API_BASE_URL", "")
MODEL = os.environ.get("API_MODEL", "")
MAX_TOKENS = int(os.environ.get("API_MAX_TOKENS", "4096"))
TEMPERATURE = float(os.environ.get("API_TEMPERATURE", "0.1"))
NO_THINK = os.environ.get("API_NO_THINK", "false").lower() == "true"

# If environment variables not set, fall back to api_config.json (local development)
if not API_KEY or not BASE_URL or not MODEL:
    API_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "api_config.json")
    if os.path.exists(API_CONFIG_PATH):
        with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
            api_config_data = json.load(f)

        selected_api = None
        selected_api_name = api_config_data.get("use_name", "")
        if selected_api_name:
            for api in api_config_data.get("api_configs", []):
                if api.get("name", "") == selected_api_name and api.get("enabled", False):
                    selected_api = api
                    break
        else:
            for api in api_config_data.get("api_configs", []):
                if api.get("enabled", False) and api.get("api_key", "").strip():
                    selected_api = api
                    break

        if selected_api:
            API_KEY = selected_api["api_key"]
            BASE_URL = selected_api["base_url"]
            MODEL = selected_api["model"]
            MAX_TOKENS = selected_api.get("max_tokens", 4096)
            TEMPERATURE = selected_api.get("temperature", 0.1)
            logger.info(f"Using API configuration: {selected_api['name']} with model {MODEL}")

# Initialize OpenAI client
CLIENT = None
if API_KEY and BASE_URL and MODEL and not API_KEY.startswith("REPLACE_WITH_"):
    CLIENT = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=120.0, max_retries=0)
    logger.info(f"OpenAI client initialized with model: {MODEL}")
else:
    logger.warning("API credentials not configured. AI inference will not work.")


# --- Input Validator ---

def validate_mri_input(findings: str, language: str = "zh") -> tuple:
    """Validate if input is related to MRI AHA plaque classification assessment"""
    if not findings or not findings.strip():
        return False, "输入为空" if language == "zh" else "Input is empty"

    findings_lower = findings.lower()

    mri_keywords_zh = [
        "颈动脉", "斑块", "mri", "t1wi", "t2wi", "tof", "高信号", "低信号", "等信号",
        "强化", "脂质", "纤维", "钙化", "出血", "溃疡", "狭窄", "管壁", "血栓",
        "aha", "分型", "影像", "检查所见", "动脉粥样硬化"
    ]

    mri_keywords_en = [
        "carotid", "plaque", "mri", "t1wi", "t2wi", "tof", "hyperintense", "hypointense",
        "isointense", "enhancement", "lipid", "fibrous", "calcification", "hemorrhage",
        "ulcer", "stenosis", "wall", "thrombus", "aha", "classification", "imaging",
        "findings", "atherosclerotic", "artery"
    ]

    keywords = mri_keywords_zh if language == "zh" else mri_keywords_en
    has_keyword = any(keyword in findings_lower for keyword in keywords)

    if not has_keyword:
        error_msg = "无效预测，请检查输入为正确的HRMRI影像描述" if language == "zh" else \
                    "Invalid prediction, please check input is correct HRMRI imaging description"
        return False, error_msg

    return True, ""


# --- Custom Evaluation Storage ---

def save_custom_evaluation(username, custom_id, evaluation_data):
    """Write one submission per file, avoiding shared-file overwrite races."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", username):
        raise ValueError("Invalid evaluation identifier")
    os.makedirs(USER_DATA_PATH, mode=0o700, exist_ok=True)
    custom_file = os.path.join(USER_DATA_PATH, f"{username}_{custom_id}.json")
    fd = os.open(custom_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(evaluation_data, f, ensure_ascii=False, indent=2)


# --- API Endpoints ---

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify({"evaluation_storage_enabled": app.config["ENABLE_EVALUATION_STORAGE"]})


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get all examples with the specified language"""
    lang = request.args.get('lang', 'zh')
    if lang not in LANG_SUFFIX:
        return jsonify({"error": "Unsupported language"}), 400

    examples = []
    for ex in EXAMPLES_DATA["examples"]:
        examples.append({
            "id": ex["id"],
            "title": ex[lang]["title"],
            "findings": ex[lang]["findings"]
        })

    return jsonify({"examples": examples})


@app.route('/api/examples/<example_id>', methods=['GET'])
def get_example(example_id):
    """Get a specific example by ID"""
    lang = request.args.get('lang', 'zh')
    if lang not in LANG_SUFFIX:
        return jsonify({"error": "Unsupported language"}), 400

    for ex in EXAMPLES_DATA["examples"]:
        if ex["id"] == example_id:
            return jsonify({
                "id": ex["id"],
                "title": ex[lang]["title"],
                "findings": ex[lang]["findings"]
            })

    return jsonify({"error": "Example not found"}), 404


@app.route('/api/infer', methods=['POST'])
def call_AI_infer():
    """AI inference endpoint"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400
    exam_findings = data.get("findings", "")
    language = data.get("language", "zh")
    prompt_version = data.get("prompt_version", "NP")
    if language not in ("zh", "en") or prompt_version not in ("NP", "CGP"):
        return jsonify({"error": "Unsupported language or prompt version"}), 400
    if not isinstance(exam_findings, str) or len(exam_findings) > 20000:
        return jsonify({"error": "Findings must be a string of at most 20000 characters"}), 400

    # Input validation
    is_valid, error_msg = validate_mri_input(exam_findings, language)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    if CLIENT is None:
        return jsonify({"error": "API not configured"}), 503

    # Use language and version-specific prompt
    system_prompt = PROMPTS[prompt_version][language]
    directive = " /no_think" if NO_THINK else ""

    try:
        response = CLIENT.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": f"{system_prompt}\n\n {exam_findings}{directive}"}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        ai_response = response.choices[0].message.content

        # 验证并解析AI响应
        validation_result = validate_and_parse_ai_response(ai_response, language)

        if validation_result["success"]:
            return jsonify({
                "result": ai_response,
                "validated": True,
                "data": validation_result["data"],
                "warning": validation_result.get("error")
            })
        else:
            logger.warning(f"AI响应验证失败，但返回原始内容: {validation_result['error']}")
            return jsonify({
                "result": ai_response,
                "validated": False,
                "error": validation_result["error"]
            })

    except Exception as e:
        logger.error("AI inference failed (%s)", type(e).__name__)
        return jsonify({"error": "AI inference failed; check the API configuration and service availability"}), 502


@app.route('/api/custom/submit', methods=['POST'])
def submit_custom_evaluation():
    """Submit a custom evaluation"""
    if not app.config["ENABLE_EVALUATION_STORAGE"]:
        return jsonify({"error": "Evaluation storage is disabled"}), 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400
    username = data.get('username')
    findings = data.get('findings', '')
    labels = data.get('labels', {})
    ai_result = data.get('ai_result', '')

    if not isinstance(username, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", username):
        return jsonify({"error": "Invalid evaluation identifier"}), 400

    if not isinstance(findings, str) or not findings.strip() or len(findings) > 20000:
        return jsonify({"error": "Findings must contain 1–20000 characters"}), 400
    if not isinstance(ai_result, str) or len(ai_result) > 60000:
        return jsonify({"error": "Invalid AI result"}), 400
    if not isinstance(labels, dict):
        return jsonify({"error": "Invalid labels"}), 400
    for side in ("left", "right"):
        assessment = labels.get(f"{side}_assessment")
        usefulness = labels.get(f"{side}_usefulness")
        if not isinstance(assessment, str) or assessment not in AHA_LABELS:
            return jsonify({"error": "Invalid AHA classification"}), 400
        if type(usefulness) is not int or not 1 <= usefulness <= 5:
            return jsonify({"error": "Usefulness must be an integer from 1 to 5"}), 400

    custom_id = f"CUSTOM_{uuid.uuid4().hex}"

    # Prepare evaluation data
    evaluation_data = {
        "custom_id": custom_id,
        "findings": findings.strip(),
        "left_assessment": labels["left_assessment"],
        "right_assessment": labels["right_assessment"],
        "left_usefulness": str(labels.get("left_usefulness", 0)),
        "right_usefulness": str(labels.get("right_usefulness", 0)),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ai_result": ai_result
    }

    try:
        save_custom_evaluation(username, custom_id, evaluation_data)
        logger.info("Evaluation saved")
        return jsonify({
            "custom_id": custom_id,
            "message": "自定义评估已保存"
        })
    except Exception as e:
        logger.error("Evaluation storage failed (%s)", type(e).__name__)
        return jsonify({"error": "Unable to save evaluation"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=port, debug=False, threaded=True)

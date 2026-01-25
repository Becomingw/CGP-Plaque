from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
import os
import json
import time
import logging
from pydantic import BaseModel, Field, ValidationError, ConfigDict


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Pydantic Models for AI Response Validation ---

class AHAClassificationZH(BaseModel):
    """AHA分型结果模型 (中文)"""
    左侧: str = Field(..., description="左侧颈动脉AHA分型")
    右侧: str = Field(..., description="右侧颈动脉AHA分型")

class AHAClassificationEN(BaseModel):
    """AHA Classification Model (English)"""
    Left: str = Field(..., description="Left carotid AHA classification")
    Right: str = Field(..., description="Right carotid AHA classification")

class AIInferenceResponseZH(BaseModel):
    """AI推理响应的完整模型 (中文)"""
    model_config = ConfigDict(extra="allow")
    推理过程: str = Field(..., description="AI分析推理的详细过程")
    AHA分型: AHAClassificationZH = Field(..., description="左右侧AHA分型结果")

class AIInferenceResponseEN(BaseModel):
    """AI Inference Response Model (English)"""
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    Reasoning_Process: str = Field(None, alias="Reasoning Process", description="AI reasoning process")
    AHA_Classification: AHAClassificationEN = Field(None, alias="AHA Classification", description="AHA classification results")

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

    # 尝试直接解析JSON
    parsed_json = None
    try:
        parsed_json = json.loads(raw_response)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw_response)
        if json_match:
            try:
                parsed_json = json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                result["error"] = f"从代码块提取JSON失败: {str(e)}"
                logger.warning(result["error"])
        else:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_response)
            if json_match:
                try:
                    parsed_json = json.loads(json_match.group(0))
                except json.JSONDecodeError as e:
                    result["error"] = f"提取JSON对象失败: {str(e)}"
                    logger.warning(result["error"])
            else:
                result["error"] = "未找到有效的JSON格式"
                logger.warning(result["error"])

    if parsed_json is None:
        return result

    try:
        if language == "en":
            validated_data = AIInferenceResponseEN(**parsed_json)
            result["data"] = {
                "Reasoning Process": validated_data.Reasoning_Process,
                "AHA Classification": {
                    "Left": validated_data.AHA_Classification.Left if validated_data.AHA_Classification else "Unknown",
                    "Right": validated_data.AHA_Classification.Right if validated_data.AHA_Classification else "Unknown"
                }
            }
        else:
            validated_data = AIInferenceResponseZH(**parsed_json)
            result["data"] = validated_data.model_dump()

        result["success"] = True
        logger.info("AI响应验证成功")
    except ValidationError as e:
        result["error"] = f"数据验证失败: {str(e)}"
        logger.warning(f"Pydantic验证错误，尝试部分恢复: {e}")

        if isinstance(parsed_json, dict):
            is_english = "Reasoning Process" in parsed_json or "AHA Classification" in parsed_json

            if is_english:
                fallback_data = {
                    "Reasoning Process": parsed_json.get("Reasoning Process", "No reasoning provided"),
                    "AHA Classification": {
                        "Left": "Unknown",
                        "Right": "Unknown"
                    }
                }
                if "AHA Classification" in parsed_json:
                    aha = parsed_json["AHA Classification"]
                    if isinstance(aha, dict):
                        fallback_data["AHA Classification"]["Left"] = str(aha.get("Left", "Unknown"))
                        fallback_data["AHA Classification"]["Right"] = str(aha.get("Right", "Unknown"))
            else:
                fallback_data = {
                    "推理过程": parsed_json.get("推理过程", "未提供推理过程"),
                    "AHA分型": {
                        "左侧": "未知",
                        "右侧": "未知"
                    }
                }
                if "AHA分型" in parsed_json:
                    aha = parsed_json["AHA分型"]
                    if isinstance(aha, dict):
                        fallback_data["AHA分型"]["左侧"] = str(aha.get("左侧", "未知"))
                        fallback_data["AHA分型"]["右侧"] = str(aha.get("右侧", "未知"))

            if is_english or "推理过程" in parsed_json or "AHA分型" in parsed_json:
                result["data"] = fallback_data
                result["success"] = True
                result["error"] = "使用了部分恢复的数据"
                logger.warning("使用部分恢复的数据结构")

    return result


# --- Flask App Setup ---

app = Flask(__name__, static_folder='static')
CORS(app)

# --- Configuration ---

USER_DATA_PATH = r"user_data"
os.makedirs(USER_DATA_PATH, exist_ok=True)

# Load prompts for both languages and both versions
PROMPT_DIR = os.path.join(os.path.dirname(__file__), "Prompt")
PROMPTS = {}
LANG_SUFFIX = {"zh": "CN", "en": "EN"}
for version in ["NP", "KGP"]:
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

# --- API Configuration (Environment Variables for HF Spaces) ---

# Try to load from environment variables first (for HF Spaces)
API_KEY = os.environ.get("API_KEY", "")
BASE_URL = os.environ.get("API_BASE_URL", "")
MODEL = os.environ.get("API_MODEL", "")
MAX_TOKENS = int(os.environ.get("API_MAX_TOKENS", "4096"))
TEMPERATURE = float(os.environ.get("API_TEMPERATURE", "0.1"))

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
                if api.get("name", "") == selected_api_name:
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
if API_KEY and BASE_URL:
    CLIENT = OpenAI(api_key=API_KEY, base_url=BASE_URL)
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

def load_custom_evaluations(username):
    """Load custom evaluations from {username}_custom.json"""
    custom_file = os.path.join(USER_DATA_PATH, f"{username}_custom.json")
    if os.path.exists(custom_file):
        try:
            with open(custom_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取自定义评估失败 {custom_file}: {e}")
            return {}
    return {}

def save_custom_evaluation(username, custom_id, evaluation_data):
    """Save a custom evaluation to {username}_custom.json"""
    custom_file = os.path.join(USER_DATA_PATH, f"{username}_custom.json")
    evaluations = load_custom_evaluations(username)
    evaluations[custom_id] = evaluation_data

    try:
        with open(custom_file, 'w', encoding='utf-8') as f:
            json.dump(evaluations, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存自定义评估: {custom_file} - {custom_id}")
    except Exception as e:
        logger.error(f"保存自定义评估失败 {custom_file}: {e}")
        raise


# --- API Endpoints ---

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get all examples with the specified language"""
    lang = request.args.get('lang', 'zh')

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
    if CLIENT is None:
        return jsonify({"error": "API not configured"}), 500

    data = request.json
    exam_findings = data.get("findings", "")
    language = data.get("language", "zh")
    prompt_version = data.get("prompt_version", "NP")

    # Input validation
    is_valid, error_msg = validate_mri_input(exam_findings, language)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    # Use language and version-specific prompt
    system_prompt = PROMPTS.get(prompt_version, {}).get(language, PROMPTS["NP"][language])

    try:
        response = CLIENT.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": f"{system_prompt}\n\n {exam_findings} /no_think"}
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
        logger.error(f"AI推理失败: {e}")
        return jsonify({"error": f"AI推理失败: {str(e)}"}), 500


@app.route('/api/custom/submit', methods=['POST'])
def submit_custom_evaluation():
    """Submit a custom evaluation"""
    data = request.json
    username = data.get('username')
    findings = data.get('findings', '').strip()
    labels = data.get('labels', {})
    ai_result = data.get('ai_result', '')

    if not username:
        return jsonify({"error": "用户名不能为空"}), 400

    if not findings:
        return jsonify({"error": "检查所见不能为空"}), 400

    # Generate custom ID with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    custom_id = f"CUSTOM_{timestamp}"

    # Prepare evaluation data
    evaluation_data = {
        "custom_id": custom_id,
        "findings": findings,
        "left_assessment": labels.get("left_assessment", "I"),
        "right_assessment": labels.get("right_assessment", "I"),
        "left_usefulness": str(labels.get("left_usefulness", 0)),
        "right_usefulness": str(labels.get("right_usefulness", 0)),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ai_result": ai_result
    }

    try:
        save_custom_evaluation(username, custom_id, evaluation_data)
        logger.info(f"用户 {username} 提交自定义评估: {custom_id}")
        return jsonify({
            "custom_id": custom_id,
            "message": "自定义评估已保存"
        })
    except Exception as e:
        logger.error(f"保存自定义评估失败: {e}")
        return jsonify({"error": f"保存失败: {str(e)}"}), 500


if __name__ == '__main__':
    os.makedirs(USER_DATA_PATH, exist_ok=True)
    # For local development, use port 5001
    # For HF Spaces, use port 7860
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

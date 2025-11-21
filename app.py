from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from openai import OpenAI
import pandas as pd
import os
import json
import time
import tempfile
import logging
from typing import Optional
from pydantic import BaseModel, Field, ValidationError


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Pydantic Models for AI Response Validation ---

class AHAClassification(BaseModel):
    """AHA分型结果模型"""
    左侧: str = Field(..., description="左侧颈动脉AHA分型，如'IV-V'、'无'、'NA'等")
    右侧: str = Field(..., description="右侧颈动脉AHA分型，如'IV-V'、'无'、'NA'等")

class AIInferenceResponse(BaseModel):
    """AI推理响应的完整模型"""
    推理过程: str = Field(..., description="AI分析推理的详细过程")
    AHA分型: AHAClassification = Field(..., description="左右侧AHA分型结果")

    class Config:
        # 允许额外字段，以防AI返回其他信息
        extra = "allow"

def validate_and_parse_ai_response(raw_response: str) -> dict:
    """
    验证并解析AI响应，确保结构正确

    Args:
        raw_response: AI返回的原始字符串

    Returns:
        包含验证后数据的字典，格式为：
        {
            "success": bool,
            "data": dict or None,
            "raw": str,
            "error": str or None
        }
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
        # 如果直接解析失败，尝试从markdown代码块中提取
        import re
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw_response)
        if json_match:
            try:
                parsed_json = json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                result["error"] = f"从代码块提取JSON失败: {str(e)}"
                logger.warning(result["error"])
        else:
            # 尝试查找任何JSON对象
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

    # 使用Pydantic验证JSON结构
    try:
        validated_data = AIInferenceResponse(**parsed_json)
        result["success"] = True
        result["data"] = validated_data.model_dump()
        logger.info("AI响应验证成功")
    except ValidationError as e:
        result["error"] = f"数据验证失败: {str(e)}"
        logger.error(f"Pydantic验证错误: {e}")

        # 尝试部分恢复：如果有基本字段，仍然返回
        if isinstance(parsed_json, dict):
            if "推理过程" in parsed_json or "AHA分型" in parsed_json:
                # 创建一个兜底的结构
                fallback_data = {
                    "推理过程": parsed_json.get("推理过程", "未提供推理过程"),
                    "AHA分型": {
                        "左侧": "未知",
                        "右侧": "未知"
                    }
                }

                # 尝试提取AHA分型
                if "AHA分型" in parsed_json:
                    aha = parsed_json["AHA分型"]
                    if isinstance(aha, dict):
                        fallback_data["AHA分型"]["左侧"] = str(aha.get("左侧", "未知"))
                        fallback_data["AHA分型"]["右侧"] = str(aha.get("右侧", "未知"))

                result["data"] = fallback_data
                result["success"] = True
                result["error"] = "使用了部分恢复的数据"
                logger.warning("使用部分恢复的数据结构")

    return result


class RomanConverter:
    ROMAN_NUMBERS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
    ROMAN_TO_INT = {roman: i + 1 for i, roman in enumerate(ROMAN_NUMBERS)}
    INT_TO_ROMAN = {i + 1: roman for i, roman in enumerate(ROMAN_NUMBERS)}

    @classmethod
    def int_to_roman(cls, value: int) -> str:
        return cls.INT_TO_ROMAN.get(value, "I")

    @classmethod
    def roman_to_int(cls, roman: str) -> int:
        return cls.ROMAN_TO_INT.get(roman, 1)

# --- Flask 应用设置 ---

app = Flask(__name__, static_folder='static')
CORS(app)  # 允许跨域请求


# --- 全局变量和配置 ---
# 注意：在生产环境中，应该使用更健壮的方式管理会话和数据，而不是全局变量
# 这里为了简化，我们为每个用户动态创建一个 "session"

user_sessions = {}
TABLE_PATH = r"/mnt/f/Project/AHA_LLM-main/aha_llm/aha_UI/test200.xlsx"
USER_DATA_PATH = r"user_data"
os.makedirs(USER_DATA_PATH, exist_ok=True)
system_prompt_file = os.path.join(os.path.dirname(__file__), "prompt_9.md")
with open(system_prompt_file, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


# Load API configuration from api_config.json
API_CONFIG_PATH = r"/mnt/f/Project/AHA_LLM-main/aha_llm/aha_UI/api_config.json"
with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
    api_config_data = json.load(f)

# Find enabled API configuration
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


# Initialize OpenAI client with configuration from api_config.json
API_KEY = selected_api["api_key"]
BASE_URL = selected_api["base_url"]
CLIENT = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)
MODEL = selected_api["model"]
MAX_TOKENS = selected_api.get("max_tokens", 2048)
TEMPERATURE = selected_api.get("temperature", 0.1)
TIMEOUT = selected_api.get("timeout", 60)

logger.info(f"Using API configuration: {selected_api['name']} with model {MODEL}")

# --- 核心逻辑 ---

def get_user_session(username):
    if username not in user_sessions:
        user_sessions[username] = {
            "table_df": None,
            "patient_labels": {},
            "current_patient_index": 0,
            "start_time": None
        }
    return user_sessions[username]

def load_user_progress(username):
    user_file = os.path.join(USER_DATA_PATH, f"{username}.json")
    if os.path.exists(user_file):
        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("current_patient_index", 0), data.get("patient_labels", {})
        except Exception as e:
            logger.error(f"读取用户进度失败 {user_file}: {e}")
    return 0, {}

def save_user_progress(username):
    session = get_user_session(username)
    if not username:
        return
    user_file = os.path.join(USER_DATA_PATH, f"{username}.json")
    data = {
        "current_patient_index": session["current_patient_index"],
        "patient_labels": session["patient_labels"],
        "last_save_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存用户进度: {user_file}")
    except Exception as e:
        logger.error(f"保存用户进度失败 {user_file}: {e}")

def get_current_patient_data(username):
    session = get_user_session(username)
    df = session["table_df"]
    if df is None or df.empty:
        return None

    index = session["current_patient_index"]
    if not 0 <= index < len(df):
        return None

    row = df.iloc[index]
    barcode = str(row.get("条码号", "")).strip()
    findings = str(row.get("检查所见", "")).strip()
    
    labels = session["patient_labels"].get(barcode, {})
    
    return {
        "barcode": barcode,
        "findings": findings,
        "index": index,
        "total": len(df),
        "labels": {
            "left_assessment": RomanConverter.roman_to_int(labels.get("left_assessment", "I")),
            "right_assessment": RomanConverter.roman_to_int(labels.get("right_assessment", "I")),
            "left_usefulness": int(labels.get("left_usefulness", 0)),
            "right_usefulness": int(labels.get("right_usefulness", 0)),
            "time_spent": labels.get("time_spent", 0)
        }
    }

# --- API Endpoints ---

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({"error": "用户名不能为空"}), 400

    session = get_user_session(username)
    
    try:
        if not os.path.exists(TABLE_PATH):
            return jsonify({"error": f"数据文件不存在: {TABLE_PATH}"}), 500
        
        df = pd.read_excel(TABLE_PATH)
        required_cols = ["条码号", "检查所见"]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return jsonify({"error": f"表格缺少必要列: {', '.join(missing)}"}), 500

        df["条码号"] = df["条码号"].astype(str).str.strip()
        session["table_df"] = df
        
        index, labels = load_user_progress(username)
        session["current_patient_index"] = index
        session["patient_labels"] = labels
        
        patient_data = get_current_patient_data(username)
        if patient_data is None:
             return jsonify({"error": "无法加载患者数据"}), 500

        session["start_time"] = time.time()
        return jsonify(patient_data)

    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({"error": f"服务器内部错误: {e}"}), 500

@app.route('/api/patient/navigate', methods=['POST'])
def navigate_patient():
    data = request.json
    username = data.get('username')
    direction = data.get('direction', 'next') # 'next' or 'prev'
    
    session = get_user_session(username)
    if session["table_df"] is None:
        return jsonify({"error": "请先登录"}), 401

    if direction == 'next':
        session["current_patient_index"] += 1
    else: # prev
        session["current_patient_index"] -= 1
    
    # 边界检查
    if not 0 <= session["current_patient_index"] < len(session["table_df"]):
        session["current_patient_index"] = max(0, min(session["current_patient_index"], len(session["table_df"]) - 1))
        return jsonify({"error": "已经是第一条或最后一条数据"}), 404

    save_user_progress(username)
    patient_data = get_current_patient_data(username)
    session["start_time"] = time.time() # 重置计时器
    return jsonify(patient_data)

@app.route('/api/patient/jump', methods=['POST'])
def jump_to_patient():
    data = request.json
    username = data.get('username')
    barcode = data.get('barcode', '').strip()

    session = get_user_session(username)
    df = session["table_df"]
    if df is None:
        return jsonify({"error": "请先登录"}), 401
    
    if not barcode:
        return jsonify({"error": "条码号不能为空"}), 400

    matches = df.index[df['条码号'] == barcode].tolist()
    if not matches:
        return jsonify({"error": f"未找到条码号: {barcode}"}), 404
        
    session["current_patient_index"] = matches[0]
    save_user_progress(username)
    patient_data = get_current_patient_data(username)
    session["start_time"] = time.time() # 重置计时器
    return jsonify(patient_data)


@app.route('/api/submit', methods=['POST'])
def submit_evaluation():
    data = request.json
    username = data.get('username')
    session = get_user_session(username)

    if session["table_df"] is None:
        return jsonify({"error": "请先登录"}), 401

    barcode = str(session["table_df"].iloc[session["current_patient_index"]]["条码号"]).strip()
    
    time_spent = 0
    if session["start_time"]:
        time_spent = time.time() - session["start_time"]

    if barcode not in session["patient_labels"]:
        session["patient_labels"][barcode] = {}

    labels = data.get('labels', {})
    session["patient_labels"][barcode]["left_assessment"] = RomanConverter.int_to_roman(labels.get("left_assessment", 1))
    session["patient_labels"][barcode]["right_assessment"] = RomanConverter.int_to_roman(labels.get("right_assessment", 1))
    session["patient_labels"][barcode]["left_usefulness"] = str(labels.get("left_usefulness", 0))
    session["patient_labels"][barcode]["right_usefulness"] = str(labels.get("right_usefulness", 0))
    session["patient_labels"][barcode]["time_spent"] = time_spent

    save_user_progress(username)
    
    return jsonify({
        "message": "提交成功",
        "time_spent": time_spent
    })

@app.route('/api/export', methods=['POST'])
def export_results():
    data = request.json
    username = data.get('username')
    session = get_user_session(username)
    df = session["table_df"]
    
    if df is None:
        return jsonify({"error": "没有数据可导出"}), 400

    df_export = df.copy()
    df_export["左侧评估"] = ""
    df_export["右侧评估"] = ""
    df_export["左侧有用性"] = ""
    df_export["右侧有用性"] = ""
    df_export["时间"] = ""

    for idx, row in df_export.iterrows():
        barcode = str(row["条码号"]).strip()
        if barcode in session["patient_labels"]:
            labels = session["patient_labels"][barcode]
            df_export.at[idx, "左侧评估"] = labels.get("left_assessment", "I")
            df_export.at[idx, "右侧评估"] = labels.get("right_assessment", "I")
            df_export.at[idx, "左侧有用性"] = labels.get("left_usefulness", "0")
            df_export.at[idx, "右侧有用性"] = labels.get("right_usefulness", "0")
            df_export.at[idx, "时间"] = labels.get("time_spent", 0)

    df_export = df_export.loc[:, ~df_export.columns.str.contains('Unnamed')]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        output_path = tmp.name
        df_export.to_excel(output_path, index=False, engine='openpyxl')

    return send_file(output_path, as_attachment=True, download_name=f"{username}_export_{int(time.time())}.xlsx")


@app.route('/api/infer', methods=['POST'])
def call_AI_infer():
    data = request.json
    exam_findings = data.get("findings", "")
    if not exam_findings:
        return jsonify({"error": "检查所见不能为空"}), 400

    try:
        response = CLIENT.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": f"{SYSTEM_PROMPT}\n\n {exam_findings} /no_think"}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        ai_response = response.choices[0].message.content
        # logger.info(f"AI响应: {ai_response}")
        # logger.info(f"AI响应内容前100字符: {ai_response[:100]}...")

        # 验证并解析AI响应
        validation_result = validate_and_parse_ai_response(ai_response)

        if validation_result["success"]:
            # 返回验证后的结构化数据
            return jsonify({
                "result": ai_response,  # 保留原始响应供前端fallback使用
                "validated": True,
                "data": validation_result["data"],
                "warning": validation_result.get("error")  # 如果有部分恢复的警告
            })
        else:
            # 验证失败，但仍返回原始响应
            logger.warning(f"AI响应验证失败，但返回原始内容: {validation_result['error']}")
            return jsonify({
                "result": ai_response,
                "validated": False,
                "error": validation_result["error"]
            })

    except Exception as e:
        logger.error(f"AI推理失败: {e}")
        return jsonify({"error": f"AI推理失败: {str(e)}"}), 500


@app.route('/api/infer/test', methods=['POST'])
def infer_test():
    """测试端点，返回模拟的AI推理结果，用于前端测试"""
    data = request.json or {}
    findings = data.get('findings', '')

    # 创建符合Pydantic模型的模拟数据
    mock_data = {
        "推理过程": f"这是基于检查所见 '{findings[:50]}...' 的模拟AI分析。\n\n1. 左侧颈动脉分析：检测到斑块成分包括脂质核心和纤维组织，T2WI呈低信号，符合Type IV-V特征。\n2. 右侧颈动脉分析：观察到明显钙化，T1WI和T2WI均呈极低信号，符合Type VII特征。",
        "AHA分型": {
            "左侧": "IV-V",
            "右侧": "VII"
        }
    }

    # 模拟JSON字符串响应
    mock_response = json.dumps(mock_data, ensure_ascii=False, indent=2)

    # 使用相同的验证流程
    validation_result = validate_and_parse_ai_response(mock_response)

    return jsonify({
        "result": mock_response,
        "validated": validation_result["success"],
        "data": validation_result["data"],
        "warning": validation_result.get("error")
    })


if __name__ == '__main__':
    os.makedirs(USER_DATA_PATH, exist_ok=True)
    # 启用多线程支持，允许多个用户并发调用AI
    # threaded=True: 每个请求在独立线程中处理，避免相互阻塞
    app.run(debug=True, port=5001, threaded=True)

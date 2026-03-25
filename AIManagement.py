import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json
import io


def load_prompt_from_md():
    """从md或txt文件加载系统提示词"""
    base_dir = os.path.dirname(__file__)
    possible_files = ["Huibi_AI_Analysis_Prompt.md", "AI提示词文档.txt"]

    for filename in possible_files:
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split('\n')
                core_lines = []
                skip_section = False
                for line in lines:
                    if line.startswith('## 一、项目背景') or line.startswith('## 二、技术方案'):
                        skip_section = False
                    if line.startswith('## 八、输出格式') or line.startswith('## 九、参考'):
                        skip_section = True
                    if not skip_section and line.strip() and not line.startswith('# ') and not line.startswith('## '):
                        core_lines.append(line)
                return '\n'.join(core_lines)
    return None


st.set_page_config(
    page_title="慧笔有方",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)


def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_session():
    if st.session_state.current_session:
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)


def load_sessions():
    session_list = []
    if os.path.exists("sessions"):
        for filename in os.listdir("sessions"):
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True)
    return session_list


def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败!")


def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("删除会话失败!")


def recognize_speech(audio_bytes):
    """
    语音转文字 - 请在这里接入实际的语音识别API
    返回识别到的文字，如果失败返回None
    """
    # TODO: 接入语音识别API，例如：
    # import openai
    # client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    # response = client.audio.transcriptions.create(
    #     model="whisper-1",
    #     file=audio_bytes
    # )
    # return response.text
    
    # 临时：模拟识别结果，实际使用时删除这行
    return "这是语音转文字的结果（请集成语音识别API）"


# ========== 初始化状态 ==========
if "messages" not in st.session_state:
    st.session_state.messages = []
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小甜甜"
if "nature" not in st.session_state:
    st.session_state.nature = "活泼开朗的东北姑娘"
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()
if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False
if "processing_voice" not in st.session_state:
    st.session_state.processing_voice = False

client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")


def get_system_prompt():
    md_content = load_prompt_from_md()
    nick_name = st.session_state.get('nick_name', '小甜甜')
    nature = st.session_state.get('nature', '活泼开朗的东北姑娘')

    if md_content:
        return f"""你叫 {nick_name}，你是慧笔有方品牌下的智能辅助练字机器人的配套的辅助AI系统。

以下是你需要掌握的项目详细技术资料：

{md_content}

回复要求：
3. 匹配用户的语言
4. 有需要的话可以用emoji表情
5. 用符合伴侣性格的方式对话：{nature}
6. 回复的内容要充分体现伴侣的性格特征
7. 回答技术问题时必须结合上述详细技术资料
8. 回答技术问题时，使用更加专业语言，融入专业的名词

你必须严格遵守上述规则来回复用户。"""
    else:
        return f"""你叫 {nick_name}，你是慧笔有方品牌下的智能辅助练字机器人的配套的辅助AI系统。

核心能力：
- 阻抗原理机械手辅助练字
- 智能姿态监测（MediaPipe）
- 三维度字体识别评分
- PSO-PID控制算法
- ABAQUS仿真验证（60万+次疲劳寿命）

伴侣性格：
    - {nature}

规则：
    1. 每次只回1条消息
    2. 禁止任何场景或状态描述性文字
    3. 匹配用户的语言
    4. 有需要的话可以用emoji表情
    5. 用符合伴侣性格的方式对话
    6. 回复的内容要充分体现伴侣的性格特征
你必须严格遵守上述规则来回复用户。"""


# ========== 页面标题 ==========
st.title("辅助AI系统")

try:
    st.logo("resources/logo.png")
except:
    pass

# ========== 侧边栏 ==========
with st.sidebar:
    st.subheader("AI控制面板")

    if st.button("新建会话", width="stretch", icon="✏️"):
        save_session()
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()

    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(session, width="stretch", icon="📄", key=f"load_{session}",
                         type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            if st.button("", width="stretch", icon="❌️", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    st.divider()

    st.subheader("管理信息")
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    nature = st.text_area("性格", placeholder="请输入性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

# ========== 聊天展示区 ==========
st.text(f"会话名称: {st.session_state.current_session}")

# 显示历史消息
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# ========== AI回复函数 ==========
def get_ai_response():
    """获取AI回复并显示"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": get_system_prompt()},
            *st.session_state.messages
        ],
        stream=True
    )

    response_message = st.empty()
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_session()


# ========== 处理语音输入（录音完成后自动发送）==========
if st.session_state.voice_mode and not st.session_state.processing_voice:
    st.markdown("---")
    st.info("🎙️ 点击下方开始录音，说完话后点击停止，语音将自动转文字并发送")
    
    # 录音组件
    audio_data = st.audio_input("录音", label_visibility="collapsed", key="voice_recorder")
    
    if audio_data is not None:
        # 用户已完成录音
        st.session_state.processing_voice = True
        
        # 转文字
        with st.spinner("🎤 识别中..."):
            recognized_text = recognize_speech(audio_data.getvalue())
        
        if recognized_text:
            # 直接添加到聊天记录（用户消息）
            st.session_state.messages.append({"role": "user", "content": recognized_text})
            save_session()
            
            # 重置语音模式
            st.session_state.voice_mode = False
            st.session_state.processing_voice = False
            
            # 刷新页面显示新消息
            st.rerun()
        else:
            st.error("语音识别失败，请重试")
            st.session_state.processing_voice = False
    
    # 取消按钮
    if st.button("取消", key="cancel_voice"):
        st.session_state.voice_mode = False
        st.session_state.processing_voice = False
        st.rerun()

# 如果刚刚添加了语音消息，立即获取AI回复
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    # 检查上一条是否是刚添加的（通过检查assistant是否已回复）
    if len(st.session_state.messages) == 1 or st.session_state.messages[-2]["role"] != "assistant":
        get_ai_response()
        st.rerun()

# ========== 输入区域 ==========
input_container = st.container()

with input_container:
    # 文本输入和语音按钮并排
    col_input, col_voice = st.columns([8, 1])
    
    with col_input:
        user_input = st.text_input(
            "输入消息",
            label_visibility="collapsed",
            placeholder="请输入您要问的问题",
            key="text_input"
        )
    
    with col_voice:
        # 语音按钮 🎤 放在输入框旁边
        if st.button("🎤", help="语音输入", key="voice_btn", use_container_width=True):
            st.session_state.voice_mode = True
            st.rerun()

# ========== 处理文本输入 ==========
if user_input and user_input.strip():
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    save_session()
    
    # 获取AI回复
    get_ai_response()
    
    # 清空输入框
    st.session_state.text_input = ""
    st.rerun()

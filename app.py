import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
from agno.media import Image as AgnoImage
from agno.tools.duckduckgo import DuckDuckGoTools
from typing import Optional
from pathlib import Path
import tempfile
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Initialize agents
def initialize_agents(api_key: str):
    try:
        model = Gemini(id="gemini-2.0-flash-exp", api_key=api_key)

        therapist_agent = Agent(
            model=model,
            name="Therapist Agent",
            instructions=[
                "You are an empathetic therapist that:",
                "1. Listens with empathy and validates feelings",
                "2. Uses gentle humor to lighten the mood",
                "3. Shares relatable breakup experiences",
                "4. Offers comforting words and encouragement",
                "5. Analyzes both text and image inputs for emotional context"
            ],
            markdown=True
        )

        closure_agent = Agent(
            model=model,
            name="Closure Agent",
            instructions=[
                "You are a closure specialist that:",
                "1. Creates emotional messages for unsent feelings",
                "2. Helps express raw, honest emotions",
                "3. Formats messages clearly with headers",
                "4. Ensures tone is heartfelt and authentic"
            ],
            markdown=True
        )

        routine_planner_agent = Agent(
            model=model,
            name="Routine Planner Agent",
            instructions=[
                "You are a recovery routine planner that:",
                "1. Designs 7-day recovery challenges",
                "2. Includes fun activities and self-care tasks",
                "3. Suggests social media detox strategies",
                "4. Creates empowering playlists"
            ],
            markdown=True
        )

        brutal_honesty_agent = Agent(
            model=model,
            name="Brutal Honesty Agent",
            tools=[DuckDuckGoTools()],
            instructions=[
                "You are a direct feedback specialist that:",
                "1. Gives raw, objective feedback about breakups",
                "2. Explains relationship failures clearly",
                "3. Uses blunt, factual language",
                "4. Provides reasons to move forward"
            ],
            markdown=True
        )

        return therapist_agent, closure_agent, routine_planner_agent, brutal_honesty_agent

    except Exception as e:
        st.error(f"Error initializing agents: {str(e)}")
        return None, None, None, None

# ----------------------------- Streamlit UI -----------------------------

st.set_page_config(page_title="💔 Breakup Recovery Squad", page_icon="💔", layout="wide")
st.title("💔 Breakup Recovery Squad")
st.markdown("### Your AI-powered breakup recovery team is here to help! Share your feelings and chat screenshots below.")

# Sidebar
with st.sidebar:
    st.header("🔑 API Configuration")
    api_key = st.text_input("Enter your Gemini API Key", type="password", help="Get from [Google AI Studio](https://makersuite.google.com/app/apikey)")
    st.markdown("---")
    st.subheader("🙋 Feedback?")
    st.text_area("How can we improve this app?")

if not api_key:
    st.warning("🔐 Please enter your Gemini API Key in the sidebar.")
    st.stop()

# Main input area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📖 Share Your Feelings")
    user_input = st.text_area("How are you feeling?", height=150, placeholder="Tell us your story...")

with col2:
    st.subheader("🖼️ Upload Chat Screenshots")
    uploaded_files = st.file_uploader("(Optional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    for file in uploaded_files or []:
        st.image(file, caption=file.name, use_container_width=True)

def process_images(files):
    processed = []
    for file in files:
        try:
            tmp_path = os.path.join(tempfile.gettempdir(), file.name)
            with open(tmp_path, "wb") as f:
                f.write(file.getbuffer())
            processed.append(AgnoImage(filepath=Path(tmp_path)))
        except Exception as e:
            logger.error(f"Image error: {e}")
    return processed

# Analysis + Recovery Plan
if st.button("💝 Get Recovery Plan"):
    if not user_input and not uploaded_files:
        st.warning("Please provide your feelings or upload images.")
        st.stop()

    with st.spinner("🧠 Initializing your recovery team..."):
        therapist, closure, planner, honest = initialize_agents(api_key)

    if not all([therapist, closure, planner, honest]):
        st.error("Initialization failed. Check your API key.")
        st.stop()

    images = process_images(uploaded_files)

    st.markdown("## 🤝 Your Recovery Squad Results")

    # 🤗 Therapist Support
    with st.spinner("🤗 Getting emotional support..."):
        res = therapist.run(message=f"Analyze and comfort:\n{user_input}", images=images)
        st.markdown("### 🤗 Emotional Support", help="Gentle and validating guidance from your therapist.")
        st.info(res.content)

    # ✍️ Closure
    with st.spinner("✍️ Creating closure messages..."):
        res = closure.run(message=f"Help write unsent messages:\n{user_input}", images=images)
        st.markdown("### ✍️ Closure Guidance", help="Messages and rituals to let go.")
        st.success(res.content)

    # 📅 7-Day Recovery Plan
    with st.spinner("📅 Building your routine..."):
        res = planner.run(message=f"Design a 7-day challenge:\n{user_input}", images=images)
        st.markdown("### 📅 Your Recovery Plan", help="Daily healing tasks and activities.")
        st.warning(res.content)

    # 💪 Brutal Honesty
    with st.spinner("💪 Sharing honest truth..."):
        res = honest.run(message=f"Give me the truth:\n{user_input}", images=images)
        st.markdown("### 💪 Honest Feedback", help="No sugar-coating. Just truth.")
        st.error(res.content)

    st.success("✅ Personalized Recovery Plan Generated! Wishing you strength 💖")

# ---------------------- 💬 Continuous Chat Support -----------------------

st.divider()
st.markdown("## 🧠 Ongoing Support Chat")
st.markdown("Chat with your personal therapist whenever you need comfort or advice.")

# Setup chat session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input for live chat
user_chat_input = st.chat_input("Type your message here...")

if user_chat_input:
    st.session_state.chat_history.append(("user", user_chat_input))

    with st.spinner("💬 Therapist typing..."):
        try:
            chat_prompt = "\n".join(
                [f"User: {m[1]}" if m[0] == "user" else f"Therapist: {m[1]}" for m in st.session_state.chat_history]
            )
            chat_response = therapist.run(message=chat_prompt)
            reply = chat_response.content.strip()
            st.session_state.chat_history.append(("therapist", reply))
        except Exception as e:
            reply = "Something went wrong. Please try again."
            st.session_state.chat_history.append(("therapist", reply))
            logger.error(f"Chatbot error: {e}")

# Display chat
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.chat_message("🧍 You").markdown(msg)
    else:
        st.chat_message("🧠 Therapist").markdown(msg)

# Footer
st.divider()
st.markdown("<center><small>Made with ❤️ by the Breakup Recovery Squad</small></center>", unsafe_allow_html=True)

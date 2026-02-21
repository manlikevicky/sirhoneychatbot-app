import streamlit as st
import requests
import base64
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# =========================
# Load environment
# =========================
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}


# =========================
# Background image
# =========================
def set_bg(image_file):
    with open(image_file, "rb") as f:
        data = f.read()

    encoded = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/jpg;base64,{encoded}") no-repeat center center fixed;
            background-size: contain;   /* 👈 fit entire image */
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )



set_bg("bg.jpg")


# =========================
# Styling
# =========================
st.markdown(
    """
<style>
.bubble {
    padding: 10px 14px;
    border-radius: 18px;
    max-width: 70%;
    font-size: 15px;
    margin: 6px 0;
    display:inline-block;
}

div[data-testid="chat-message-user"] .bubble {
    background:#39ff14;
    color:black;
    margin-left:auto;
    border-bottom-right-radius:4px;
}

div[data-testid="chat-message-assistant"] .bubble {
    background:#4FC3F7;
    color:black;
    margin-right:auto;
    border-bottom-left-radius:4px;
}

.time {
    font-size:10px;
    opacity:0.6;
    margin-top:3px;
    text-align:right;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# Login
# =========================
if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    st.title("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user and pwd:
            st.session_state.logged = True
            st.rerun()
        else:
            st.warning("Enter credentials")

    st.stop()


# =========================
# Sidebar
# =========================
with st.sidebar:
    st.title("⚙️ Menu")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    uploaded_file = st.file_uploader("📎 Upload file")


# =========================
# Chat memory
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================
# OpenRouter AI function
# =========================
def ask_ai(prompt):
    payload = {
        "model": "mistralai/mistral-7b-instruct",  # free + fast
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"⚠️ Error {response.status_code}: {response.text}"


# =========================
# Display history
# =========================
for role, msg, t in st.session_state.messages:
    with st.chat_message(role, avatar="🧑" if role == "user" else "🤖"):
        st.markdown(
            f"""
            <div class="bubble">
                {msg}
                <div class="time">{t} ✓✓</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================
# Input
# =========================
user_input = st.chat_input("Message...")

if uploaded_file:
    user_input = f"File uploaded: {uploaded_file.name}"


# =========================
# Chat logic
# =========================
if user_input:
    now = datetime.now().strftime("%H:%M")

    st.session_state.messages.append(("user", user_input, now))

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()

        for dots in ["Typing.", "Typing..", "Typing..."]:
            placeholder.markdown(dots)
            time.sleep(0.3)

        reply = ask_ai(user_input)

        placeholder.markdown(
            f"""
            <div class="bubble">
                {reply}
                <div class="time">{now}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.session_state.messages.append(("assistant", reply, now))
    st.rerun()



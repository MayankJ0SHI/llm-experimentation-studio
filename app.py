import warnings
warnings.filterwarnings('ignore')

import streamlit as st
from dotenv import load_dotenv
import json
import time
import llm_provider as llm

load_dotenv()

# ---------------- CONFIG ---------------- #
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

# ---------------- PAGE ---------------- #
st.set_page_config(
    page_title="Prompt Playground + Chat",
    page_icon="🤖",
    layout="wide"
)

st.title("🧪 Prompt Playground + Chat")

# ---------------- LOAD CONFIG ---------------- #
config = load_config()

# ---------------- SIDEBAR ---------------- #
st.sidebar.header("⚙️ Settings")

provider_list = list(config["models"].keys())

provider = st.sidebar.selectbox(
    "Provider",
    provider_list,
    index=provider_list.index(config["provider"])
)

config["provider"] = provider

st.sidebar.caption(f"Model: {config['models'][provider]}")

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5)
max_tokens = st.sidebar.number_input("Max Tokens", 10, 500, 100)

compare_mode = st.sidebar.checkbox("Enable Comparison Mode")

# ---------------- SESSION INIT ---------------- #
if "history" not in st.session_state:
    st.session_state["history"] = [
        {"role": "assistant", "content": "Hello, How can I help you today?"}
    ]

# ---------------- RESET ---------------- #
if st.sidebar.button("Reset History ♻️"):
    st.session_state["history"] = [
        {"role": "assistant", "content": "Hello, How can I help you today?"}
    ]
    st.rerun()

# ---------------- DISPLAY CHAT ---------------- #
for msg in st.session_state["history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- COMPARISON INPUT ---------------- #
temp_list = []
if compare_mode:
    temp_input = st.sidebar.text_input(
        "Temperatures (comma separated)", "0.2,0.5,1.0"
    )
    try:
        temp_list = [float(t.strip()) for t in temp_input.split(",")]
    except:
        st.sidebar.error("Invalid temperature values")

# ---------------- USER INPUT ---------------- #
if prompt := st.chat_input("Type your message..."):

    # Add user message
    st.session_state["history"].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        llm_instance = llm.LLM_Provider(config)

        with st.spinner("Thinking..."):
            start_time = time.time()

            # -------- Comparison Mode -------- #
            if compare_mode and temp_list:
                results = llm_instance.compare_outputs(prompt, temp_list, max_tokens)

                end_time = time.time()
                elapsed = round(end_time - start_time, 2)

                st.subheader("📊 Comparison Results")
                st.caption(f"⏱️ Response Time: {elapsed}s")

                cols = st.columns(len(results))

                for i, res in enumerate(results):
                    with cols[i]:
                        st.markdown(f"### Temp: {res['temperature']}")

                        st.markdown(
                            f"""
                            <div style="
                                height: 400px;
                                overflow-y: auto;
                                padding: 10px;
                                border: 1px solid #444;
                                border-radius: 10px;
                                background-color: #0e1117;
                            ">
                                {res['output']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            # -------- Chat Mode -------- #
            else:
                response = llm_instance.chat(
                    history=st.session_state["history"][-6:],  # last 6 messages
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                end_time = time.time()
                elapsed = round(end_time - start_time, 2)

                # Add assistant response
                st.session_state["history"].append({
                    "role": "assistant",
                    "content": response
                })

                with st.chat_message("assistant"):
                    st.markdown(response)

                st.caption(f"⏱️ Response Time: {elapsed}s")

    except Exception as e:
        st.error(str(e))
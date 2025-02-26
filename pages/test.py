import streamlit as st
import os
import json
import google.generativeai as genai
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="JanSeva ChatBot", page_icon=":robot_face:", layout="wide")

# Configure API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyBwPlJcIvgqlEox7yGy22Q_jtaGH3bHgIY"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('GovrnSvc.csv')

df = load_data()

st.dataframe(df, use_container_width=True)

# Title
st.title("Chat with ***JanSeva AI***")

# Sidebar - Select Service
with st.sidebar:
    st.subheader("📌 Select Service")
    category = st.selectbox("Select Category", ["All"] + df["Category"].unique().tolist(), index=0)
    filtered_df = df if category == "All" else df[df["Category"] == category]
    service = st.selectbox("Select Service", filtered_df["Service"].unique().tolist(), index=None)

# Check if service is selected
if not service:
    st.warning("⚠️ Please select a service to start interacting with JanSeva AI.")
    st.stop()

# Display Service Info
service_info = df[df["Service"] == service]
if not service_info.empty:
    description = service_info["Description"].values[0]
    with st.container(border=True):
        st.write(f"**🏛️ Selected Service:** {service}\n\n**📃 Service Description:** {description}")

# Create Chat Directory
chat_dir = "chat_history"
os.makedirs(chat_dir, exist_ok=True)

# Get today's date for naming new chat files
today = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
chat_filename = os.path.join(chat_dir, f"chat_{today}.json")

# Load available chat names (only filenames without extensions)
chat_files = sorted(
    [f.replace(".json", "") for f in os.listdir(chat_dir) if f.endswith(".json")],
    reverse=True
)

# Sidebar - Chat Selection
with st.sidebar:
    st.subheader("💬 Past Chats")
    selected_chat = st.selectbox("📂 Select a Chat", chat_files, index=None, placeholder="Choose chat to load")

# Load selected chat history
if selected_chat:
    chat_path = os.path.join(chat_dir, f"{selected_chat}.json")
    with open(chat_path, "r") as file:
        st.session_state.chat_history = json.load(file)
else:
    st.session_state.chat_history = []

# Chat Container
chat_container = st.container(border=True, height=400)
question = st.chat_input("Ask JanSeva AI anything...")

# Display chat messages
with chat_container:
    for msg in st.session_state.chat_history:
        display_role = "You" if msg["role"] == "user" else "JanSeva"
        with st.chat_message(msg["role"]):
            st.markdown(f"**{display_role}:** {msg['content']}")

# User input

    if question:
        with st.chat_message("user"):
            st.markdown(f"**You:** {question}")

        with st.chat_message("assistant"):
            with st.spinner("JanSeva is responding..."):
                chat_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
                model = genai.GenerativeModel("gemini-1.5-flash")

                prompt = (
                    f"Your name is 'JanSeva AI', a government services chatbot. "
                    f"You assist users with government schemes, eligibility, application processes, and documents required. "
                    f"Always provide accurate and relevant responses based on the selected service: {service} under category {category}.\n\n"
                    f"Here is the ongoing conversation:\n{chat_context}\n\n"
                    f"Now, answer the latest question:\n{question}."
                )

                response = model.generate_content(prompt)
                result = response.text

            st.markdown(f"**JanSeva:** {result}")

            # Append to chat history
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.session_state.chat_history.append({"role": "assistant", "content": result})

        # Save chat history
        with open(chat_filename, "w") as file:
            json.dump(st.session_state.chat_history, file, indent=4)

# Sidebar - Start New Chat Button
with st.sidebar:
    if st.button("🆕 Start New Chat"):
        st.session_state.chat_history = []
        chat_filename = os.path.join(chat_dir, f"chat_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.json")
        with open(chat_filename, "w") as file:
            json.dump([], file)  # Create new empty chat file
        st.toast("Started a new chat session")
        st.rerun()


if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.toast("Chat history cleared")
    st.rerun()
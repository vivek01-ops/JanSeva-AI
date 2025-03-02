import streamlit as st
import os
import json
import google.generativeai as genai
import pandas as pd
import re

# Configure page
st.set_page_config(page_title="JanSeva ChatBot", page_icon=":robot_face:", layout="wide")

# Set up Google API key securely
os.environ["GOOGLE_API_KEY"] = "AIzaSyBwPlJcIvgqlEox7yGy22Q_jtaGH3bHgIY"  # Replace with your actual API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

st.title("Chat with ***JanSeva AI***")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv('GovrnSvc.csv')

df = load_data()

# Popover for government services
with st.popover("Explore Government Facilities and Services", icon="🔍", use_container_width=True):
    st.dataframe(df, use_container_width=True, hide_index=True)

# Chat history directory setup
chat_dir = "chat_history"
os.makedirs(chat_dir, exist_ok=True)

# Function to sanitize filenames
def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

# Load and save chat history functions
def load_chat_history(filename):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return []

def save_chat_history(filename, history):
    with open(filename, "w") as file:
        json.dump(history, file, indent=4)

# Sidebar for past chats
with st.sidebar:
    with st.container(border=True):
        st.subheader("Past Chats")
        chat_files = sorted(f.replace(".json", "") for f in os.listdir(chat_dir) if f.endswith(".json"))
        selected_chat = st.selectbox("📂 Select a Chat", ["New Chat"] + chat_files, index=0)

# Sidebar for selecting services
with st.sidebar:
    with st.container(border=True):
        st.subheader("Select Service")
        category = st.selectbox("Select Category", ["All"] + df["Category"].unique().tolist(), index=0)
        filtered_df = df if category == "All" else df[df["Category"] == category]
        service = st.selectbox("Select Service", filtered_df["Service"].unique().tolist(), index=None)

# Maintain service selection when switching chats
if selected_chat != "New Chat":
    service = selected_chat.replace("_", " ")

# Ensure service is selected
if service:
    service_info = df[df["Service"] == service]
    with st.container(border=True):
        if not service_info.empty:
            description = service_info["Description"].values[0]
            st.write(f"**Selected Service:** {service}\n\n**Service Description:** {description}")
else:
    st.warning("⚠️ We recommend to select a service or a past chat to start communication with JanSeva AI.")

# Chat history management
sanitized_service = sanitize_filename(service) if service else "new_chat"
chat_filename = os.path.join(chat_dir, f"{sanitized_service}.json")
chat_history = load_chat_history(chat_filename)

# Chat container
chat_container = st.container(border=True, height=340)

# FAQ pills
# faq_options = [
#     "How to apply for this service?", 
#     "Eligibility Criteria?",
#     "Documents Required",
#     "Application Process",
#     "Application Deadline"
# ]
# selected_pill = st.pills("Frequently Asked Questions", faq_options, selection_mode="single")

# If a pill is selected, it becomes the input question
question =  st.chat_input("Ask JanSeva AI anything...")

# Display chat history
with chat_container:
    for msg in chat_history:
        display_role = "You" if msg["role"] == "user" else "JanSeva"
        with st.chat_message(msg["role"]):
            st.markdown(f"**{display_role}:** {msg['content']}")
    
    # Process new questions
    if question:
        with st.chat_message("user"):
            st.markdown(f"**You:** {question}")
        
        with st.chat_message("assistant"):
            with st.spinner("JanSeva is responding..."):
                chat_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = (
                    f"Your name is 'JanSeva AI', and you provide government services information about schemes, benefits, "
                    f"eligibility, deadlines, application processes, and form submissions.\n\n"
                    f"User guidelines:\n"
                    f"User asking question is: {question} related to {service}\n"
                    f"- If asked about 'JanSeva AI', introduce yourself as an AI expert for government services.\n"
                    f"- Keep responses concise and informative.\n"
                    f"- If the user's query is about '{service}', provide details including steps, documents, and links.\n"
                    f"- If the query is unrelated, politely inform the user you assist only with government services.\n"
                    f"- Provide only official government website links when asked for references.\n\n"
                    f"Current conversation:\n{chat_context}\n\n"
                    f"Latest user question: {question}"
                )
                response = model.generate_content(prompt)
                result = response.text
            
            st.markdown(f"**JanSeva:** {result}")
            chat_history.append({"role": "user", "content": question})
            chat_history.append({"role": "assistant", "content": result})
            save_chat_history(chat_filename, chat_history)

if st.button("🗑️ Clear Chat"):
        chat_history = []
        save_chat_history(chat_filename, [])
        st.toast("Chat history cleared")
        st.rerun()

with st.sidebar:
    if st.button("🆕 Start New Chat", use_container_width=True):
        new_chat_filename = os.path.join(chat_dir, f"{sanitize_filename(service) if service else 'new_chat'}.json")
        save_chat_history(new_chat_filename, [])
        st.toast("Started a new chat session")
        st.rerun()

    if selected_chat != "New Chat" and st.button("🗑️ Delete Selected Chat", use_container_width=True, type="primary"):
        os.remove(os.path.join(chat_dir, f"{selected_chat}.json"))
        st.toast(f"Deleted chat: {selected_chat}")
        st.rerun()

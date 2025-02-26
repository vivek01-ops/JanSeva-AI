import streamlit as st
import os
import google.generativeai as genai
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="JanSeva ChatBot",
                   page_icon=":robot_face:", layout="wide",
                   initial_sidebar_state="auto")

# Configure API Key securely
os.environ["GOOGLE_API_KEY"] = "AIzaSyBwPlJcIvgqlEox7yGy22Q_jtaGH3bHgIY"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])



# Load data
@st.cache_data
def load_data():
    try:
        return pd.read_csv('GovrnSvc.csv')
    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
        return pd.DataFrame(columns=["Category", "Service", "Description"])  # Return empty DataFrame

df = load_data()

st.title("Chat with ***JanSeva AI***")

# Sidebar for selecting service
with st.popover("Select Service", icon="📌"):
    st.subheader("Select Service", divider="red")
    category = st.selectbox("Select Category", options=["All"] + df["Category"].dropna().unique().tolist(),
                            index=0, placeholder="Categories")
    filtered_df = df if category == "All" else df[df["Category"] == category]
    service = st.selectbox("Select Service", filtered_df["Service"].dropna().unique().tolist(),
                           index=None, placeholder="Services")

if service:
    service_info = df[df["Service"] == service]
    if not service_info.empty:
        description = service_info["Description"].values[0]
        with st.container(border=True):
            st.write(f"**🏛️Selected Service:** {service}\n\n**📃Service Description:** {description}")
    else:
        st.error("⚠️ Service details not found.")
        service = None  # Reset selection
else:
    st.warning("⚠️ Please select a service to start interacting with ***JanSeva AI***.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_container = st.container(border=True, height=356)
question = st.chat_input("Ask JanSeva AI anything...") if service else None
with chat_container:
    for msg in st.session_state.chat_history:
        role_display = "You" if msg["role"] == "user" else "JanSeva"
        with st.chat_message(msg["role"]):
            st.markdown(f"**{role_display}:** {msg['content']}")

    if question and service:
        with st.chat_message("user"):
            st.markdown(f"**You:** {question}")

        with st.chat_message("assistant"):
            with st.spinner("JanSeva AI is responding..."):
                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    chat_context = "\n".join(
                        [f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])

                    prompt = (f"Your name is 'JanSeva AI', and you are a government services chatbot that provides information "
                            f"about schemes, benefits, eligibility criteria, deadlines, application processes, and form submissions. "
                            f"Ensure responses are clear and relevant to '{service}' under category '{category}'.\n\n"
                            f"User guidelines:\n"
                            f"- If a user asks about 'JanSeva AI', introduce yourself as an AI expert for government services.\n"
                            f"- Always keep responses concise and informative.\n"
                            f"- Avoid unnecessary introductions unless a new conversation starts.\n"
                            f"- If the user's query is about '{service}', provide a detailed answer including steps, documents, and official links.\n"
                            f"- If the query is unrelated, politely inform the user you assist only with government services.\n"
                            f"- Provide only official government website links when asked for external references.\n\n"
                            f"Current conversation:\n{chat_context}\n\n"
                            f"Latest user question: {question}")

                    response = model.generate_content(prompt)
                    result = response.text if response else "⚠️ No response generated."

                except Exception as e:
                    result = f"❌ An error occurred: {str(e)}"

            st.markdown(f"**JanSeva:** {result}")

            # Save conversation history
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.chat_history.append({"role": "user", "content": question, "timestamp": timestamp})
            st.session_state.chat_history.append({"role": "assistant", "content": result, "timestamp": timestamp})

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.toast("Chat history cleared")
    st.rerun()

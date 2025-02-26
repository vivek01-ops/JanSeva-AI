import streamlit as st
import time

st.set_page_config(page_title="JanSeva AI", page_icon="🏛️", layout="wide")

st.markdown(
    """
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        text-align: center;
    }
    .small-font {
        font-size:18px !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<p class='big-font'>Welcome to JanSeva AI</p>", unsafe_allow_html=True)
st.markdown("<p class='small-font'>Your AI Assistant for Government Services</p>", unsafe_allow_html=True)

st.image("https://source.unsplash.com/1200x500/?government,service", use_container_width=True)

st.write("JanSeva AI is designed to assist citizens in accessing information about various government services effortlessly.")

st.markdown("### How JanSeva AI Helps:")
st.write("✅ AI Chatbot for answering government service-related queries")
st.write("✅ Information on RTO, Education, Healthcare, Banking, and more")
st.write("✅ Text-to-Speech (TTS) for better accessibility")
st.write("✅ Easy-to-navigate interface for all users")

col1, col2 = st.columns(2)
with col1:
    if st.button("Get Started 🏛️"):
        st.switch_page("pages/Chatbot.py")
with col2:
    if st.button("Learn More 📚"):
        st.switch_page("Education")

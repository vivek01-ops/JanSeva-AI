import streamlit as st
import sqlite3
import pandas as pd
import time

st.set_page_config(page_title="JanSeva AI", page_icon="🏛️", layout="centered", initial_sidebar_state="collapsed")

# Hide sidebar on homepage
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        .centered { text-align: center; }
        # .big-text { font-size: 3em; font-weight: bold; }
        .subtext { font-size: 1.2em; color: #555; }
        .button-container { display: flex; justify-content: center; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for authentication
if "auth" not in st.session_state:
    st.session_state.auth = False

# Show Welcome Page or Authentication System
if not st.session_state.auth:
    st.markdown('<p class="big-text centered", style="font-size: 3em; font-weight: bold;">🤖 Welcome to <span style="color:#0078FF;">JanSeva AI</span></p>', unsafe_allow_html=True)
    st.markdown('<p class="subtext centered">Your AI-powered assistant for government services and schemes.</p>', unsafe_allow_html=True)

    # Animated loading effect
    with st.empty():
        for i in range(3):
            st.markdown(f'<p class="centered">Loading JanSeva AI{"." * (i+1)}</p>', unsafe_allow_html=True)
            time.sleep(1)
            st.empty()

    # Get Started button (Navigates to authentication system)
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("🚀 Get Started", use_container_width=True):
        st.session_state.auth = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
else:
    # -------------------------- Authentication System --------------------------
    st.title("JanSeva AI")
    st.header("Your AI Assistant for Government Services")

    login, register = st.tabs(["Login", "Register"])

    # Database connection
    def create_conc():
        return sqlite3.connect("user_data.db")

    # Table creation
    def create_table():
        conn = create_conc()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            name TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,  
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

    create_table()

    @st.cache_data
    def load_data():
        try:
            return pd.read_csv('JanSeva States.csv')
        except Exception as e:
            st.error(f"Error in loading data: {e}")
            return pd.DataFrame(columns=["State", "District"])

    df = load_data()

    # -------------------------- Registration Section --------------------------
    with register:
        with st.container(border=True):
            st.subheader("Register to JanSeva AI", divider="red")

            name = st.text_input("Name", placeholder="Enter Your Name")
            email = st.text_input("Email", placeholder="Enter Your Email")

            col1, col2 = st.columns(2)
            with col1:
                state = st.selectbox("State", df['State'].dropna().unique().tolist(), key="state", index=None, placeholder="Select a State")

            with col2:  
                if state:
                    district_list = df[df['State'] == state]['District'].dropna().unique().tolist()
                else:
                    district_list = []
                district = st.selectbox("District", district_list, key="district", index=None, placeholder="Select a District")

            username = st.text_input("Username", placeholder="Enter Your Username")
            password = st.text_input("Password", type="password", placeholder="Enter Your Password")

            def register_user(name, state, district, email, username, password):
                conn = create_conc()
                cursor = conn.cursor()

                # Check if the email or username already exists
                cursor.execute("SELECT * FROM users WHERE email = ? OR username = ?", (email, username))
                existing_user = cursor.fetchone()

                if existing_user:
                    st.error("Username or Email already exists! Please try another one.")
                else:
                    try:
                        cursor.execute("INSERT INTO users (name, state, district, email, username, password) VALUES (?, ?, ?, ?, ?, ?)",
                                    (name, state, district, email, username, password))
                        conn.commit()
                        st.success("Registration Successful! You can now log in.")
                    except sqlite3.IntegrityError:
                        st.error("This email or username is already registered. Try a different one.")
                    except Exception as e:
                        st.error(f"Error in registration: {e}")
                    finally:
                        conn.close()

        if st.button("Register"):
            if name and state and district and email and username and password:
                register_user(name, state, district, email, username, password)
            else:
                st.warning("Please fill all fields!")

    # -------------------------- Login Section --------------------------
    with login:
        with st.container(border=True):
            st.subheader("Login to JanSeva AI", divider="red")

            username = st.text_input("Username", placeholder="Enter Your Username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter Your Password", key="login_pass")

            def verify_login(username, password):
                conn = create_conc()
                cursor = conn.cursor()
                query = "SELECT * FROM users WHERE username = ? AND password = ?"
                cursor.execute(query, (username, password))
                result = cursor.fetchone()
                conn.close()  
                return result

        if st.button("Login"):
            if username and password:
                user = verify_login(username, password)
                if user:
                    st.success("Login Successful!")
                    st.toast(f"Welcome to JanSeva AI ***{user[0]}***!") 
                    st.switch_page("pages/JanSeva-AI.py") 
                else:
                    st.error("Invalid credentials! Please try again.")
            else:
                st.error("Please fill all fields!")

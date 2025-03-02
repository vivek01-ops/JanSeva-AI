import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="JanSeva AI", page_icon="🏛️", layout="centered", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """, 
    unsafe_allow_html=True
)

# st.markdown(
#     """
#     <style>
#     .big-font {
#         font-size:20px !important;
#         font-weight: bold;
#         text-align: center;
#     }
#     .small-font {
#         font-size:18px !important;
#         text-align: center;
#     }
#     </style>
#     """, unsafe_allow_html=True)

st.title("JanSeva AI")
st.header("Your AI Assistant for Government Services")

# st.markdown("<p class='big-font'>Welcome to JanSeva AI</p>", unsafe_allow_html=True)
# st.markdown("<p class='small-font'>Your AI Assistant for Government Services</p>", unsafe_allow_html=True)
# st.markdown("")

# Tabs for Registration and Login
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
            if state != "Select a State":
                district_list = df[df['State'] == state]['District'].dropna().unique().tolist()
            else:
                district_list = []
            district = st.selectbox("District",district_list, key="district", index=None, placeholder="Select a District")
        
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
        if name and state != "Select a State" and district != "Select a District" and email and username and password:
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

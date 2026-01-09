# app.py
# Hospital Management System GUI - Streamlit version with all modules
# Run: streamlit run app.py

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ─── Page configuration ────────────────────────────────────────────────
st.set_page_config(
    page_title="MedCare Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Database connection ───────────────────────────────────────────────
def get_db_connection():
    conn = sqlite3.connect('hospital.db', check_same_thread=False)
    return conn

def init_database():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Patients table
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            dob TEXT,
            gender TEXT,
            phone TEXT UNIQUE,
            address TEXT,
            blood_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# ─── Session state for login ───────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ─── Sidebar with all your modules ─────────────────────────────────────
with st.sidebar:
    st.title("🏥 MedCare HMS")
    st.markdown("---")
    
    if st.session_state.logged_in:
        page = st.radio(
            "Main Modules",
            options=[
                "📊 Dashboard",
                "👥 Patients",
                "👨‍⚕️ Doctors",
                "👩‍⚕️ Staff / Employees",
                "🧪 Lab & Investigations",
                "💊 Pharmacy Inventory",
                "📅 Appointments",
                "🏢 Departments",
                "📈 Reports"
            ]
        )
        st.markdown("---")
        if st.button("🚪 Logout", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    else:
        page = "Login"

# ─── Login screen ──────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.title("MedCare Hospital Management System")
    st.subheader("Login (Demo Mode)")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if username.strip() == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
                st.info("Use:   **admin**  /  **admin123**")
    st.stop()

# ─── Main content ──────────────────────────────────────────────────────
st.title(f"MedCare Hospital → {page}")
st.markdown("---")

# Dashboard
if page == "📊 Dashboard":
    col1, col2, col3 = st.columns(3)
    
    conn = get_db_connection()
    try:
        patient_count = pd.read_sql_query("SELECT COUNT(*) as cnt FROM patients", conn)['cnt'][0]
    except:
        patient_count = 0
    
    col1.metric("Total Patients", patient_count)
    col2.metric("Active Doctors", "0 (module in progress)")
    col3.metric("System Status", "Online")
    conn.close()

# Patients - with search + basic add
elif page == "👥 Patients":
    tab1, tab2 = st.tabs(["📋 Patient List", "➕ Add New Patient"])
    
    with tab1:
        search = st.text_input("Search by name or phone", "")
        
        conn = get_db_connection()
        query = "SELECT * FROM patients ORDER BY id DESC"
        if search:
            query = "SELECT * FROM patients WHERE first_name LIKE ? OR last_name LIKE ? OR phone LIKE ? ORDER BY id DESC"
            df = pd.read_sql_query(query, conn, params=(f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            df = pd.read_sql_query(query, conn)
        conn.close()
        
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            fname = st.text_input("First Name*")
            lname = st.text_input("Last Name*")
            phone = st.text_input("Phone Number*")
        with col2:
            gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
            dob = st.date_input("Date of Birth")
            blood = st.selectbox("Blood Group", ["A+","A-","B+","B-","O+","O-","AB+","AB-","Unknown"])
        
        if st.button("Register Patient", type="primary"):
            if fname and lname and phone:
                conn = get_db_connection()
                try:
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO patients 
                        (first_name, last_name, phone, gender, dob, blood_type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (fname, lname, phone, gender, str(dob), blood))
                    conn.commit()
                    st.success("Patient registered successfully!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("This phone number is already registered!")
                finally:
                    conn.close()
            else:
                st.warning("Please fill all required fields (*)")

# All other modules (placeholders - ready for future expansion)
else:
    st.info(f"""
    ### {page}
    
    This module is prepared for implementation.
    
    You can add full CRUD (Create, Read, Update, Delete) operations here  
    using the same pattern as the **Patients** module above.
    
    Current status: **placeholder / in development**
    """)

# Footer
st.markdown("---")
st.caption(f"MedCare Hospital Management System • {datetime.now().strftime('%Y-%m-%d')}")

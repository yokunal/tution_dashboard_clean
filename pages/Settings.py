"""Settings Page."""
import streamlit as st
from lib.database import SheetsDatabaseManager

def refresh_page():
    """Clear cache and rerun the page."""
    st.cache_data.clear()
    st.rerun()

st.title("⚙️ Settings")

st.markdown("#### 🔑 Tutor Information")
tutor_name = st.text_input("Tutor Name", value=st.session_state.get('tutor_name', ''))
tutor_email = st.text_input("Tutor Email (optional)", value=st.session_state.get('tutor_email', ''))

if st.button("💾 Save Settings"):
    st.session_state['tutor_name'] = tutor_name
    st.session_state['tutor_email'] = tutor_email
    st.success("Settings saved successfully!")

st.markdown("---")
st.markdown("#### 🔗 Database Connection")
st.info("Connected to Google Sheets - Tution_Log_AI")

# Connection test
if st.button("🔄 Test Connection"):
    try:
        db = SheetsDatabaseManager()
        students = db.get_all_students()
        st.success(f"✅ Connection successful! Found {len(students)} students.")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

st.markdown("---")
st.markdown("#### 📊 Data Management")

st.warning("⚠️ Data refresh will clear cached data and reload from Google Sheets.")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Refresh All Data"):
        refresh_page()
        st.success("Data refreshed!")

with col2:
    if st.button("🗑️ Clear Session State"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session state cleared! Please refresh the page.")

st.markdown("---")
st.markdown("#### 🗂️ Worksheet Status")

try:
    db = st.session_state.db
    worksheet_names = [ws.title for ws in db.spreadsheet.worksheets()]
    
    for ws_name in ['Students', 'Teaching_Logs', 'Homework', 'Tests']:
        if ws_name in worksheet_names:
            st.write(f"✅ {ws_name}")
        else:
            st.write(f"❌ {ws_name} - Not found")
except Exception as e:
    st.error(f"Error checking worksheets: {e}")

st.markdown("---")
st.markdown("##### About")
st.caption("""
**Student Profile Tracker v1.0**

AI-Powered Tutoring Management System featuring:
- 📋 Student Management
- 📝 Teaching Log Tracking
- 📚 Homework Management  
- 📊 Test Results Recording
- 🤖 AI-Generated Progress Reports
- 📄 PDF Export with Latin-1 Encoding Support
""")

st.markdown("---")
st.markdown("##### API Status")

try:
    secrets = st.secrets
    minimax_configured = bool(secrets.get("minimax", {}).get("api_key", ""))
    gcp_configured = bool(secrets.get("gcp_service_account", {}).get("client_email", ""))
    
    if minimax_configured:
        st.success("✅ MiniMax API configured")
    else:
        st.warning("⚠️ MiniMax API not configured - AI reports disabled")
    
    if gcp_configured:
        st.success("✅ Google Cloud credentials configured")
    else:
        st.warning("⚠️ GCP credentials not configured - Sheets sync disabled")
except Exception as e:
    st.error(f"Error checking API status: {e}")

"""Students Page - Manage students."""
import streamlit as st
import pandas as pd
from lib.database import SheetsDatabaseManager

def refresh_page():
    """Clear cache and rerun the page."""
    st.cache_data.clear()
    st.rerun()

st.title("👨‍🎓 Student Management")

# Refresh button
if st.button("🔄 Refresh Data"):
    refresh_page()

tab1, tab2 = st.tabs(["📋 View Students", "➕ Add New Student"])

with tab1:
    try:
        db = st.session_state.db
        students = db.get_all_students()
        
        if students:
            df = pd.DataFrame(students)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("##### Select a student to view details:")
            student_names = [""] + [s.get('name', '') for s in students]
            selected = st.selectbox("Student", options=student_names)
            
            if selected:
                for s in students:
                    if s.get('name', '') == selected:
                        st.json(s)
        else:
            st.info("No students found. Add your first student!")
    except Exception as e:
        st.error(f"Error loading students: {e}")

with tab2:
    with st.form("add_student_form"):
        name = st.text_input("Student Name*")
        grade = st.text_input("Grade/Class")
        school = st.text_input("School")
        subject = st.text_input("Subject")
        parent_contact = st.text_input("Parent Contact")
        email = st.text_input("Email")
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("➕ Add Student")
        if submitted:
            if name:
                data = {
                    'name': name, 'grade': grade, 'school': school,
                    'subject': subject, 'parent_contact': parent_contact,
                    'email': email, 'notes': notes
                }
                result = st.session_state.db.add_student(data)
                if result:
                    st.success("Student added successfully!")
                    refresh_page()
                else:
                    st.error("Failed to add student")
            else:
                st.warning("Please enter student name")

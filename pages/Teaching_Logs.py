"""Teaching Logs Page."""
import streamlit as st
import pandas as pd
from datetime import datetime
from lib.database import SheetsDatabaseManager

def refresh_page():
    """Clear cache and rerun the page."""
    st.cache_data.clear()
    st.rerun()

st.title("📝 Teaching Logs")

# Refresh button
if st.button("🔄 Refresh Data"):
    refresh_page()

try:
    db = st.session_state.db
    students = db.get_all_students()
    logs = db.get_teaching_logs()
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        student_filter = st.selectbox("Filter by Student", ["All"] + [s.get('name', '') for s in students])
    with col2:
        month_filter = st.selectbox("Filter by Month", ["All"] + [str(i) for i in range(1, 13)])
    
    # Display logs
    filtered_logs = logs
    if student_filter != "All":
        filtered_logs = [l for l in filtered_logs if l.get('student_name', '') == student_filter]
    if month_filter != "All":
        month_val = int(float(str(month_filter)))
        filtered_logs = [l for l in filtered_logs if int(float(str(l.get('month', 0)))) == month_val]
    
    st.write(f"Showing {len(filtered_logs)} log entries")
    
    if filtered_logs:
        df = pd.DataFrame(filtered_logs)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No teaching logs found matching your filters.")
    
    # Add new log
    st.markdown("---")
    st.subheader("➕ Add New Teaching Log")
    
    with st.form("add_log_form"):
        student_options = [s.get('name', '') for s in students]
        student_name = st.selectbox("Student*", student_options)
        date = st.date_input("Date", value=datetime.now())
        hours = st.number_input("Hours", min_value=0.5, max_value=8.0, value=1.0, step=0.5)
        topic = st.text_input("Topic Covered*")
        chapter_number = st.text_input("Chapter Number")
        chapter_name = st.text_input("Chapter Name")
        homework_completed = st.checkbox("Homework Reviewed & Completed")
        homework_shown = st.checkbox("Homework Shown to Teacher")
        notes = st.text_area("Session Notes")
        
        submitted = st.form_submit_button("➕ Add Log Entry")
        if submitted:
            if topic and student_name:
                student_id = next((s.get('student_id', '') for s in students if s.get('name', '') == student_name), '')
                data = {
                    'student_id': student_id,
                    'student_name': student_name,
                    'date': date.strftime('%Y-%m-%d'),
                    'hours': hours,
                    'topic': topic,
                    'chapter_number': chapter_number,
                    'chapter_name': chapter_name,
                    'homework_review_completed': homework_completed,
                    'homework_review_shown': homework_shown,
                    'notes': notes,
                    'month': date.month,
                    'year': date.year
                }
                result = db.add_teaching_log(data)
                if result:
                    st.success("Teaching log added!")
                    refresh_page()
                else:
                    st.error("Failed to add log")
            else:
                st.warning("Please fill in required fields (Topic)")

except Exception as e:
    st.error(f"Error loading teaching logs: {e}")

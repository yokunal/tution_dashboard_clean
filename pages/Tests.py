"""Tests Page."""
import streamlit as st
import pandas as pd
from datetime import datetime
from lib.database import SheetsDatabaseManager

def refresh_page():
    """Clear cache and rerun the page."""
    st.cache_data.clear()
    st.rerun()

st.title("📊 Test Results")

# Refresh button
if st.button("🔄 Refresh Data"):
    refresh_page()

try:
    db = st.session_state.db
    students = db.get_all_students()
    tests = db.get_all_tests()
    
    # Filter
    student_filter = st.selectbox("Filter by Student", ["All"] + [s.get('name', '') for s in students])
    
    filtered_tests = tests
    if student_filter != "All":
        filtered_tests = [t for t in filtered_tests if t.get('student_name', '') == student_filter]
    
    st.write(f"Showing {len(filtered_tests)} test records")
    
    if filtered_tests:
        df = pd.DataFrame(filtered_tests)
        st.dataframe(df, use_container_width=True)
        
        # Performance summary
        if filtered_tests:
            avg_percentage = sum(float(t.get('percentage', 0)) for t in filtered_tests) / len(filtered_tests)
            st.metric("Average Score", f"{avg_percentage:.1f}%")
    
    # Add test
    st.markdown("---")
    st.subheader("➕ Add New Test")
    
    with st.form("add_test_form"):
        student_name = st.selectbox("Student*", [s.get('name', '') for s in students])
        test_date = st.date_input("Test Date", value=datetime.now())
        test_topic = st.text_input("Test Topic*")
        chapter_ref = st.text_input("Chapter Reference")
        marks = st.number_input("Marks Scored", min_value=0, value=80)
        total_marks = st.number_input("Total Marks", min_value=1, value=100)
        remarks = st.text_area("Remarks")
        
        submitted = st.form_submit_button("➕ Add Test")
        if submitted:
            if test_topic:
                data = {
                    'student_id': next((s.get('student_id', '') for s in students if s.get('name', '') == student_name), ''),
                    'student_name': student_name,
                    'test_date': test_date.strftime('%Y-%m-%d'),
                    'test_topic': test_topic,
                    'chapter_ref': chapter_ref,
                    'marks_scored': marks,
                    'total_marks': total_marks,
                    'remarks': remarks
                }
                result = db.add_test(data)
                if result:
                    st.success("Test added!")
                    refresh_page()
                else:
                    st.error("Failed to add test")
            else:
                st.warning("Please enter test topic")

except Exception as e:
    st.error(f"Error loading tests: {e}")

"""Student Profile Tracker - Main Application."""
import streamlit as st
import pandas as pd
from datetime import datetime
from lib.database import SheetsDatabaseManager
from lib.ai_client import generate_progress_report
from lib.pdf_generator import get_pdf_bytes

# Page configuration
st.set_page_config(
    page_title="Student Profile Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main color scheme */
    :root {
        --primary-color: #2E7D32;
        --secondary-color: #4CAF50;
        --accent-color: #81C784;
        --background-light: #E8F5E9;
        --text-dark: #1B5E20;
    }
    
    /* Stylized cards */
    .report-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #2E7D32;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* Status badges */
    .status-active {
        background-color: #4CAF50;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
    }
    
    .status-inactive {
        background-color: #9E9E9E;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
    }
    
    /* Sidebar styling */
    .css-sidebar .css-1d391kg {
        background-color: #E8F5E9;
    }
    
    /* Custom button styling */
    .stButton > button {
        background-color: #2E7D32;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #4CAF50;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    try:
        st.session_state.db = SheetsDatabaseManager()
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        st.stop()

def refresh_page():
    """Clear cache and rerun the page."""
    st.cache_data.clear()
    st.rerun()

# Sidebar navigation
st.sidebar.markdown("## 📚 Student Profile Tracker")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "📋 Dashboard",
        "👨‍🎓 Students",
        "📝 Teaching Logs",
        "📚 Homework",
        "📊 Tests",
        "🤖 AI Report Generator",
        "⚙️ Settings"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Refresh Data")
if st.sidebar.button("🔄 Refresh All Data"):
    refresh_page()

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Logged in as:** {st.session_state.get('tutor_name', 'Tutor')}")

# Main content based on selected page
if page == "📋 Dashboard":
    st.title("📋 Dashboard")
    
    try:
        db = st.session_state.db
        students = db.get_all_students()
        logs = db.get_teaching_logs()
        homework = db.get_all_homework()
        tests = db.get_all_tests()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Students", len(students))
        with col2:
            st.metric("Teaching Sessions", len(logs))
        with col3:
            st.metric("Homework Tasks", len(homework))
        with col4:
            st.metric("Tests Recorded", len(tests))
        
        st.markdown("---")
        
        # Recent activity
        st.subheader("📊 Recent Activity")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Recent Teaching Sessions")
            recent_logs = sorted(logs, key=lambda x: str(x.get('date', '')), reverse=True)[:5]
            for log in recent_logs:
                st.write(f"📅 {log.get('date', 'N/A')} - {log.get('student_name', 'N/A')} ({log.get('hours', 0)} hrs)")
        
        with col2:
            st.markdown("##### Recent Homework")
            recent_hw = sorted(homework, key=lambda x: str(x.get('assigned_date', '')), reverse=True)[:5]
            for hw in recent_hw:
                status = "✅" if hw.get('completed', False) else "⏳"
                st.write(f"{status} {hw.get('description', 'N/A')[:40]}... - {hw.get('student_name', 'N/A')}")
    
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

elif page == "👨‍🎓 Students":
    st.title("👨‍🎓 Student Management")
    
    tab1, tab2 = st.tabs(["📋 View Students", "➕ Add New Student"])
    
    with tab1:
        try:
            db = st.session_state.db
            students = db.get_all_students()
            
            if students:
                df = pd.DataFrame(students)
                st.dataframe(df, use_container_width=True)
                
                st.markdown("##### Select a student to view details:")
                selected = st.selectbox("Student", options=[""] + [s.get('name', '') for s in students])
                
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
            
            if st.form_submit_button("Add Student"):
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

elif page == "📝 Teaching Logs":
    st.title("📝 Teaching Logs")
    
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
            student_name = st.selectbox("Student*", [s.get('name', '') for s in students])
            date = st.date_input("Date", value=datetime.now())
            hours = st.number_input("Hours", min_value=0.5, max_value=8.0, value=1.0, step=0.5)
            topic = st.text_input("Topic Covered*")
            chapter_number = st.text_input("Chapter Number")
            chapter_name = st.text_input("Chapter Name")
            homework_completed = st.checkbox("Homework Reviewed & Completed")
            homework_shown = st.checkbox("Homework Shown to Teacher")
            notes = st.text_area("Session Notes")
            
            if st.form_submit_button("Add Log Entry"):
                if topic and student_name:
                    data = {
                        'student_id': next((s.get('student_id', '') for s in students if s.get('name', '') == student_name), ''),
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
                    st.warning("Please fill in required fields")
    
    except Exception as e:
        st.error(f"Error loading teaching logs: {e}")

elif page == "📚 Homework":
    st.title("📚 Homework Management")
    
    try:
        db = st.session_state.db
        students = db.get_all_students()
        homework = db.get_all_homework()
        
        # Filter
        col1, col2 = st.columns(2)
        with col1:
            student_filter = st.selectbox("Filter by Student", ["All"] + [s.get('name', '') for s in students])
        
        filtered_hw = homework
        if student_filter != "All":
            filtered_hw = [h for h in filtered_hw if h.get('student_name', '') == student_filter]
        
        st.write(f"Showing {len(filtered_hw)} homework entries")
        
        # Summary cards
        col1, col2, col3 = st.columns(3)
        completed = len([h for h in filtered_hw if h.get('completed', False)])
        pending = len(filtered_hw) - completed
        
        with col1:
            st.metric("Total", len(filtered_hw))
        with col2:
            st.metric("Completed", completed)
        with col3:
            st.metric("Pending", pending)
        
        if filtered_hw:
            df = pd.DataFrame(filtered_hw)
            st.dataframe(df, use_container_width=True)
        
        # Add homework
        st.markdown("---")
        st.subheader("➕ Add New Homework")
        
        with st.form("add_homework_form"):
            student_name = st.selectbox("Student*", [s.get('name', '') for s in students])
            assigned_date = st.date_input("Assigned Date", value=datetime.now())
            due_date = st.date_input("Due Date")
            description = st.text_area("Homework Description*")
            chapter_ref = st.text_input("Chapter Reference")
            
            if st.form_submit_button("Add Homework"):
                if description:
                    data = {
                        'student_id': next((s.get('student_id', '') for s in students if s.get('name', '') == student_name), ''),
                        'student_name': student_name,
                        'assigned_date': assigned_date.strftime('%Y-%m-%d'),
                        'due_date': due_date.strftime('%Y-%m-%d') if due_date else '',
                        'description': description,
                        'chapter_ref': chapter_ref
                    }
                    result = db.add_homework(data)
                    if result:
                        st.success("Homework added!")
                        refresh_page()
                    else:
                        st.error("Failed to add homework")
                else:
                    st.warning("Please enter homework description")
    
    except Exception as e:
        st.error(f"Error loading homework: {e}")

elif page == "📊 Tests":
    st.title("📊 Test Results")
    
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
            
            if st.form_submit_button("Add Test"):
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

elif page == "🤖 AI Report Generator":
    st.title("🤖 AI Progress Report Generator")
    
    try:
        db = st.session_state.db
        students = db.get_all_students()
        
        tutor_name = st.text_input("Tutor Name", value=st.session_state.get('tutor_name', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            selected_student = st.selectbox("Select Student*", [s.get('name', '') for s in students])
        with col2:
            month = st.selectbox("Month", [str(i) for i in range(1, 13)], index=datetime.now().month - 1)
        
        year = st.selectbox("Year", [str(y) for y in range(datetime.now().year - 2, datetime.now().year + 1)])
        
        if st.button("🚀 Generate AI Report"):
            if selected_student and tutor_name:
                with st.spinner("Generating report..."):
                    # Get student data
                    student_data = next((s for s in students if s.get('name', '') == selected_student), {})
                    
                    # Get teaching logs for the month
                    logs = db.get_teaching_logs(
                        student_id=student_data.get('student_id', ''),
                        month=int(float(str(month))),
                        year=int(float(str(year)))
                    )
                    
                    # Generate report
                    report = generate_progress_report(
                        student_data=student_data,
                        teaching_logs=logs,
                        tutor_name=tutor_name,
                        month=month,
                        year=year
                    )
                    
                    # Store in session state
                    st.session_state['generated_report'] = report
                    st.session_state['report_student'] = selected_student
                    st.session_state['report_tutor'] = tutor_name
                    st.session_state['report_month'] = month
                    st.session_state['report_year'] = year
        
        # Display and edit report
        if 'generated_report' in st.session_state:
            st.markdown("---")
            st.subheader("📄 Generated Report")
            
            # Styled box display
            st.markdown("""
            <div class="report-box">
            <h4>Progress Report</h4>
            <pre style="white-space: pre-wrap; font-family: inherit;">{}</pre>
            </div>
            """.format(st.session_state['generated_report']), unsafe_allow_html=True)
            
            # Inline editing
            st.markdown("#### ✏️ Edit Report")
            edited_report = st.text_area(
                "Edit the report below:",
                value=st.session_state['generated_report'],
                height=400,
                key="report_editor"
            )
            
            st.markdown("---")
            st.subheader("💾 Save & Download")
            
            # Download PDF button
            pdf_bytes = get_pdf_bytes(
                report_content=edited_report,
                student_name=st.session_state['report_student'],
                tutor_name=st.session_state['report_tutor'],
                month=st.session_state['report_month'],
                year=st.session_state['report_year']
            )
            
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_bytes,
                file_name=f"Progress_Report_{st.session_state['report_student']}_{st.session_state['report_month']}_{st.session_state['report_year']}.pdf",
                mime="application/pdf"
            )
            
            # Also allow copying edited text
            if st.button("📋 Copy Edited Report to Clipboard"):
                st.code(edited_report, language=None)
                st.success("Report content displayed above for copying!")
    
    except Exception as e:
        st.error(f"Error in report generator: {e}")

elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    st.markdown("#### 🔑 Tutor Information")
    tutor_name = st.text_input("Tutor Name", value=st.session_state.get('tutor_name', ''))
    
    if st.button("Save Settings"):
        st.session_state['tutor_name'] = tutor_name
        st.success("Settings saved!")
    
    st.markdown("---")
    st.markdown("#### 🔗 Database Connection")
    st.info("Connected to Google Sheets - Tution_Log_AI")
    
    st.markdown("---")
    st.markdown("#### 📊 Data Management")
    
    if st.button("🔄 Refresh All Data"):
        refresh_page()
    
    st.markdown("---")
    st.markdown("##### About")
    st.caption("Student Profile Tracker v1.0 - AI-Powered Tutoring Management System")

# Standalone testing
if __name__ == "__main__":
    print("This app is run with: streamlit run app.py")

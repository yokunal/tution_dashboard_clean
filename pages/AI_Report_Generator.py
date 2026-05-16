"""AI Report Generator Page."""
import streamlit as st
from datetime import datetime
from lib.database import SheetsDatabaseManager
from lib.ai_client import generate_progress_report
from lib.pdf_generator import get_pdf_bytes

def refresh_page():
    """Clear cache and rerun the page."""
    st.cache_data.clear()
    st.rerun()

st.title("🤖 AI Progress Report Generator")

# Refresh button
if st.button("🔄 Refresh Data"):
    refresh_page()

st.markdown("""
<style>
    .report-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #2E7D32;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .report-content {
        white-space: pre-wrap;
        font-family: inherit;
        color: #1B5E20;
    }
</style>
""", unsafe_allow_html=True)

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
    
    # Custom prompt option
    with st.expander("⚙️ Advanced Options"):
        custom_prompt = st.text_area("Custom Prompt (optional)", 
                                    placeholder="Leave empty to use default prompt...")
    
    if st.button("🚀 Generate AI Report", type="primary"):
        if selected_student and tutor_name:
            with st.spinner("Generating report with AI... Please wait..."):
                try:
                    # Get student data
                    student_data = next((s for s in students if s.get('name', '') == selected_student), {})
                    
                    # Get teaching logs for the month
                    month_int = int(float(str(month)))
                    year_int = int(float(str(year)))
                    logs = db.get_teaching_logs(
                        student_id=student_data.get('student_id', ''),
                        month=month_int,
                        year=year_int
                    )
                    
                    # Generate report
                    report = generate_progress_report(
                        student_data=student_data,
                        teaching_logs=logs,
                        tutor_name=tutor_name,
                        month=month,
                        year=year,
                        custom_prompt=custom_prompt if custom_prompt else ""
                    )
                    
                    # Store in session state
                    st.session_state['generated_report'] = report
                    st.session_state['report_student'] = selected_student
                    st.session_state['report_tutor'] = tutor_name
                    st.session_state['report_month'] = month
                    st.session_state['report_year'] = year
                    st.session_state['report_logs'] = logs
                    
                    st.success("Report generated successfully!")
                except Exception as e:
                    st.error(f"Error generating report: {e}")
        else:
            st.warning("Please enter tutor name and select a student")
    
    # Display and edit report
    if 'generated_report' in st.session_state:
        st.markdown("---")
        st.subheader("📄 Generated Report")
        
        # Styled box display
        st.markdown('<div class="report-box">', unsafe_allow_html=True)
        st.markdown(f"**Progress Report for {st.session_state['report_student']}**")
        st.markdown(f"*Period: {st.session_state['report_month']}/{st.session_state['report_year']}*")
        st.markdown(f"*Tutor: {st.session_state['report_tutor']}*")
        st.markdown("---")
        st.markdown(f'<div class="report-content">{st.session_state["generated_report"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Inline editing
        st.markdown("---")
        st.subheader("✏️ Edit Report")
        st.caption("You can edit the report text below before downloading:")
        
        edited_report = st.text_area(
            "Edit the report below:",
            value=st.session_state['generated_report'],
            height=400,
            key="report_editor"
        )
        
        st.markdown("---")
        st.subheader("💾 Save & Download")
        
        col1, col2 = st.columns(2)
        with col1:
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
        
        with col2:
            if st.button("📋 Copy Report Text"):
                st.code(edited_report, language=None)
                st.success("Report text displayed above for copying!")
        
        # Session info
        st.markdown("---")
        st.caption(f"""
        📊 Report generated from {len(st.session_state.get('report_logs', []))} teaching sessions.
        """)

except Exception as e:
    st.error(f"Error in report generator: {e}")

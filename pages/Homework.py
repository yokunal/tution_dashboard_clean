"""Homework Page."""
import streamlit as st
import pandas as pd
from datetime import datetime
from lib.database import SheetsDatabaseManager

def refresh_page():
    """Clear cache and rerun the page."""
    from lib.database import _cache
    global _cache
    _cache = {}
    st.rerun()

st.title("📚 Homework Management")

if st.button("🔄 Refresh Data"):
    refresh_page()

try:
    db = st.session_state.db
    students = db.get_all_students()
    homework = db.get_all_homework(use_cache=False)
    
    # Summary cards
    col1, col2, col3 = st.columns(3)
    total_hw = len(homework)
    completed_hw = len([h for h in homework if str(h.get('completed', 'No')).lower() in ['yes', 'true']])
    pending_hw = total_hw - completed_hw
    
    with col1:
        st.metric("Total", total_hw)
    with col2:
        st.metric("Completed", completed_hw)
    with col3:
        st.metric("Pending", pending_hw)
    
    # Filter by student
    st.markdown("---")
    student_filter = st.selectbox("Filter by Student", ["All"] + [s.get('name', '') for s in students])
    
    filtered_hw = homework
    if student_filter != "All":
        filtered_hw = [h for h in filtered_hw if h.get('student_name', '') == student_filter]
    
    st.write(f"Showing {len(filtered_hw)} homework entries")
    
    # ========== MARK HOMEWORK DONE/NOT DONE ==========
    st.markdown("### ✅ Mark Homework Done / Not Done")
    st.caption("Click the button to toggle completion status:")
    
    if filtered_hw:
        for idx, hw in enumerate(filtered_hw):
            is_completed = str(hw.get('completed', 'No')).lower() in ['yes', 'true']
            is_shown = str(hw.get('shown_to_teacher', 'No')).lower() in ['yes', 'true']
            
            col1, col2, col3, col4, col5 = st.columns([4, 1, 1, 1, 1])
            
            with col1:
                status_emoji = "✅" if is_completed else "⏳"
                desc = hw.get('homework_description', hw.get('description', 'N/A'))[:45]
                st.write(f"{status_emoji} **{desc}**")
                st.caption(f"👤 {hw.get('student_name', 'N/A')} | 📅 Due: {hw.get('due_date', 'N/A')}")
            
            with col2:
                if is_completed:
                    st.success("Done")
                else:
                    st.warning("Pending")
            
            with col3:
                if is_shown:
                    st.info("Shown")
                else:
                    st.caption("Not Shown")
            
            with col4:
                btn_label = "↩️ Undo" if is_completed else "✓ Done"
                if st.button(btn_label, key=f"toggle_{idx}"):
                    # Toggle the completion status
                    new_status = not is_completed
                    result = db.update_homework_completion(
                        row_index=idx,
                        completed=new_status,
                        shown=is_shown,
                        notes=hw.get('completion_notes', '')
                    )
                    if result:
                        st.rerun()
                    else:
                        st.error("Failed to update")
            
            with col5:
                st.write("")  # spacer
            
            st.divider()
    
    # ========== VIEW ALL (DATA TABLE) ==========
    st.markdown("---")
    st.subheader("📋 View All Homework")
    
    if filtered_hw:
        # Format for display
        display_df = []
        for hw in filtered_hw:
            display_df.append({
                'Description': hw.get('homework_description', hw.get('description', '')),
                'Student': hw.get('student_name', ''),
                'Due Date': hw.get('due_date', ''),
                'Chapter': hw.get('chapter_ref', ''),
                'Completed': hw.get('completed', 'No'),
                'Shown': hw.get('shown_to_teacher', 'No')
            })
        df = pd.DataFrame(display_df)
        st.dataframe(df, use_container_width=True)
    
    # ========== ADD NEW HOMEWORK ==========
    st.markdown("---")
    st.subheader("➕ Add New Homework")
    
    with st.form("add_homework_form"):
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.selectbox("Student*", [s.get('name', '') for s in students])
            assigned_date = st.date_input("Assigned Date", value=datetime.now())
        with col2:
            due_date = st.date_input("Due Date")
            chapter_ref = st.text_input("Chapter Reference", placeholder="e.g., Chapter 5")
        
        description = st.text_area("Homework Description*", placeholder="Enter homework details...")
        
        submitted = st.form_submit_button("➕ Add Homework", type="primary")
        if submitted:
            if description:
                data = {
                    'student_name': student_name,
                    'assigned_date': assigned_date.strftime('%Y-%m-%d'),
                    'due_date': due_date.strftime('%Y-%m-%d') if due_date else '',
                    'homework_description': description,
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
    st.error(f"Error: {e}")

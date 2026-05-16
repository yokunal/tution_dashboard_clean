"""AI client for report generation using MiniMax API."""
import streamlit as st
import requests
import json
from datetime import datetime

def generate_progress_report(student_data, teaching_logs, tutor_name="", month="", year="", custom_prompt=""):
    """
    Generate a progress report using MiniMax AI.
    
    Args:
        student_data: dict with student information
        teaching_logs: list of teaching log entries
        tutor_name: name of the tutor
        month: month for the report
        year: year for the report
        custom_prompt: optional custom prompt to override default
    
    Returns:
        str: Generated report text
    """
    try:
        secrets = st.secrets
        api_key = secrets.get("minimax", {}).get("api_key", "")
        base_url = secrets.get("minimax", {}).get("base_url", "https://api.minimax.chat")
        
        if not api_key:
            return "Error: MiniMax API key not configured. Please add it to .streamlit/secrets.toml"
        
        # Build context from teaching logs
        logs_summary = ""
        total_hours = 0
        topics_covered = set()
        
        for log in teaching_logs:
            if isinstance(log, dict):
                date = log.get('date', 'N/A')
                hours = float(log.get('hours', 0))
                topic = log.get('topic', 'N/A')
                notes = log.get('notes', '')
                chapter = log.get('chapter_name', log.get('chapter_number', ''))
                
                total_hours += hours
                topics_covered.add(topic)
                logs_summary += f"- Date: {date}, Chapter: {chapter}, Topic: {topic}, Hours: {hours}, Notes: {notes}\n"
        
        # Build default prompt
        student_name = student_data.get('name', 'Unknown Student')
        grade = student_data.get('grade', 'N/A')
        school = student_data.get('school', 'N/A')
        subject = student_data.get('subject', 'N/A')
        
        default_prompt = f"""Generate a detailed monthly progress report for a student.

**Student Details:**
- Name: {student_name}
- Grade: {grade}
- School: {school}
- Subject: {subject}

**Tutor:** {tutor_name}
**Period:** {month}/{year}

**Teaching Sessions Summary:**
Total Hours: {total_hours:.1f}
Topics Covered: {', '.join(topics_covered) if topics_covered else 'N/A'}

Session Details:
{logs_summary}

Please generate a comprehensive progress report with the following sections:
1. Executive Summary
2. Academic Progress
3. Areas of Strength
4. Areas for Improvement
5. Homework Completion Status
6. Test Performance Summary
7. Recommendations for Next Month
8. Conclusion

Make the report professional, detailed, and specific to the data provided. Include specific examples from the teaching sessions where applicable."""

        prompt = custom_prompt if custom_prompt else default_prompt
        
        # Make API call to MiniMax
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "MiniMax-Text-01",
            "messages": [
                {"role": "system", "content": "You are a professional educational report writer. Generate detailed, accurate, and encouraging progress reports for tutors and parents."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            f"{base_url}/v1/text/chatcompletion_pro",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "Error: Unexpected API response format"
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            return f"Error generating report: {error_msg}\n\nPlease try again or contact support if the issue persists."
            
    except Exception as e:
        error_msg = str(e)
        return f"Error generating report: {error_msg}\n\nThe report generation encountered an issue. Please check your API configuration and try again."

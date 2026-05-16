"""Google Sheets database manager for student profile tracker."""
import os
import gspread
from google.oauth2 import service_account
from datetime import datetime
import pandas as pd
import streamlit as st
from functools import lru_cache
import json

# Module-level cache
_cache = {}

class SheetsDatabaseManager:
    """Manages all Google Sheets operations for the tutoring application."""
    
    def __init__(self, spreadsheet_url=None):
        """Initialize the database manager with Google Sheets connection."""
        self._connected = False
        self._client = None
        self._spreadsheet = None
        
        try:
            # Load credentials from JSON file if it exists, otherwise use Streamlit secrets
            credentials_json_path = "credentials/google_service_account.json"
            
            if os.path.exists(credentials_json_path):
                with open(credentials_json_path, 'r') as f:
                    cred_data = json.load(f)
                credentials = service_account.Credentials.from_service_account_info(
                    cred_data,
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
            else:
                # Load credentials from Streamlit secrets
                secrets = st.secrets
                
                credentials = service_account.Credentials.from_service_account_info(
                    {
                        "type": "service_account",
                        "project_id": secrets.get("gcp_service_account", {}).get("project_id", ""),
                        "private_key_id": secrets.get("gcp_service_account", {}).get("private_key_id", ""),
                        "private_key": secrets.get("gcp_service_account", {}).get("private_key", "").replace("\\n", "\n"),
                        "client_email": secrets.get("gcp_service_account", {}).get("client_email", ""),
                        "token_uri": secrets.get("gcp_service_account", {}).get("token_uri", ""),
                    },
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
            
            self._client = gspread.authorize(credentials)
            
            # Use provided URL or get from secrets
            if spreadsheet_url:
                self._spreadsheet = self._client.open_by_url(spreadsheet_url)
            else:
                spreadsheet_id = st.secrets.get("spreadsheet", {}).get("id", "") if 'secrets' in dir(st) else ""
                if spreadsheet_id:
                    self._spreadsheet = self._client.open_by_key(spreadsheet_id)
                else:
                    spreadsheet_name = "Tutor_Assistant_Database"
                    self._spreadsheet = self._client.open(spreadsheet_name)
            
            self._ensure_worksheets()
            self._connected = True
            
        except Exception as e:
            raise Exception(f"Error initializing database: {e}")
    
    @property
    def spreadsheet(self):
        return self._spreadsheet
    
    def _ensure_worksheets(self):
        """Ensure all required worksheets exist with correct headers."""
        worksheet_names = [ws.title for ws in self._spreadsheet.worksheets()]
        
        # Create Students worksheet if not exists
        if 'Students' not in worksheet_names:
            self._spreadsheet.add_worksheet('Students', rows=100, cols=10)
            ws = self._spreadsheet.worksheet('Students')
            ws.update('A1', [['student_id', 'name', 'grade', 'school', 'subject', 'parent_contact', 'email', 'start_date', 'status', 'notes']])
        
        # Create Teaching_Logs worksheet if not exists
        if 'Teaching_Logs' not in worksheet_names:
            self._spreadsheet.add_worksheet('Teaching_Logs', rows=1000, cols=15)
            ws = self._spreadsheet.worksheet('Teaching_Logs')
            ws.update('A1', [['log_id', 'student_id', 'student_name', 'date', 'hours', 'topic', 
                              'chapter_number', 'chapter_name', 'homework_review_completed', 
                              'homework_review_shown', 'notes', 'month', 'year', 'created_at']])
        
        # Create Homework worksheet if not exists
        if 'Homework' not in worksheet_names:
            self._spreadsheet.add_worksheet('Homework', rows=500, cols=12)
            ws = self._spreadsheet.worksheet('Homework')
            ws.update('A1', [['homework_id', 'student_id', 'student_name', 'assigned_date', 'due_date',
                              'description', 'chapter_ref', 'completed', 'shown_to_teacher',
                              'completion_notes', 'session_log_id']])
        
        # Create Tests worksheet if not exists
        if 'Tests' not in worksheet_names:
            self._spreadsheet.add_worksheet('Tests', rows=500, cols=10)
            ws = self._spreadsheet.worksheet('Tests')
            ws.update('A1', [['test_id', 'student_id', 'student_name', 'test_date', 'chapter_ref',
                              'test_topic', 'marks_scored', 'total_marks', 'percentage', 'remarks']])
    
    def _clear_cache(self):
        """Clear module-level cache."""
        global _cache
        _cache = {}
    
    # ========== STUDENT METHODS ==========
    
    def get_all_students(self, use_cache=True):
        """Get all students from the Students worksheet."""
        cache_key = "students_all"
        
        if use_cache and cache_key in _cache:
            return _cache[cache_key]
        
        try:
            ws = self._spreadsheet.worksheet('Students')
            expected_headers = ['name', 'class_level', 'school', 'added_date', 'notes']
            records = ws.get_all_records(expected_headers=expected_headers)
            # Filter out empty rows
            result = [r for r in records if r.get('name', '').strip()]
            _cache[cache_key] = result
            return result
        except Exception as e:
            raise Exception(f"Error fetching students: {e}")
    
    def get_student(self, student_id):
        """Get a specific student by ID."""
        try:
            students = self.get_all_students()
            for student in students:
                if str(student.get('student_id', '')) == str(student_id):
                    return student
            return None
        except Exception as e:
            raise Exception(f"Error fetching student: {e}")
    
    def add_student(self, data_dict):
        """Add a new student to the database."""
        try:
            ws = self._spreadsheet.worksheet('Students')
            import uuid
            student_id = str(uuid.uuid4())[:8]
            
            row = [
                student_id,
                data_dict.get('name', ''),
                data_dict.get('grade', ''),
                data_dict.get('school', ''),
                data_dict.get('subject', ''),
                data_dict.get('parent_contact', ''),
                data_dict.get('email', ''),
                data_dict.get('start_date', datetime.now().strftime('%Y-%m-%d')),
                data_dict.get('status', 'active'),
                data_dict.get('notes', '')
            ]
            ws.append_row(row)
            self._clear_cache()
            return student_id
        except Exception as e:
            raise Exception(f"Error adding student: {e}")
    
    def update_student(self, student_id, data_dict):
        """Update an existing student."""
        try:
            ws = self._spreadsheet.worksheet('Students')
            records = ws.get_all_records()
            
            for idx, record in enumerate(records, start=2):
                if str(record.get('student_id', '')) == str(student_id):
                    headers = ['name', 'grade', 'school', 'subject', 'parent_contact', 'email', 'start_date', 'status', 'notes']
                    for i, header in enumerate(headers):
                        if header in data_dict:
                            ws.update_cell(idx, i + 2, data_dict[header])
                    self._clear_cache()
                    return True
            return False
        except Exception as e:
            raise Exception(f"Error updating student: {e}")
    
    # ========== TEACHING LOG METHODS ==========
    
    def get_teaching_logs(self, student_id=None, month=None, year=None, use_cache=True):
        """Get teaching logs, optionally filtered by student and/or month/year."""
        cache_key = f"logs_{student_id}_{month}_{year}"
        
        if use_cache and cache_key in _cache:
            return _cache[cache_key]
        
        try:
            ws = self._spreadsheet.worksheet('Teaching_Logs')
            records = ws.get_all_records()
            
            filtered = records
            if student_id:
                filtered = [r for r in filtered if str(r.get('student_id', '')) == str(student_id)]
            if month:
                month_val = int(float(str(month)))
                filtered = [r for r in filtered if int(float(str(r.get('month', 0)))) == month_val]
            if year:
                year_val = int(float(str(year)))
                filtered = [r for r in filtered if int(float(str(r.get('year', 0)))) == year_val]
            
            _cache[cache_key] = filtered
            return filtered
        except Exception as e:
            raise Exception(f"Error fetching teaching logs: {e}")
    
    def add_teaching_log(self, data_dict):
        """Add a new teaching log entry."""
        try:
            ws = self._spreadsheet.worksheet('Teaching_Logs')
            import uuid
            log_id = str(uuid.uuid4())[:8]
            
            row = [
                log_id,
                data_dict.get('student_id', ''),
                data_dict.get('student_name', ''),
                data_dict.get('date', datetime.now().strftime('%Y-%m-%d')),
                data_dict.get('hours', 0),
                data_dict.get('topic', ''),
                data_dict.get('chapter_number', ''),
                data_dict.get('chapter_name', ''),
                data_dict.get('homework_review_completed', False),
                data_dict.get('homework_review_shown', False),
                data_dict.get('notes', ''),
                data_dict.get('month', datetime.now().month),
                data_dict.get('year', datetime.now().year),
                datetime.now().isoformat()
            ]
            ws.append_row(row)
            self._clear_cache()
            return log_id
        except Exception as e:
            raise Exception(f"Error adding teaching log: {e}")
    
    # ========== HOMEWORK METHODS ==========
    
    def get_all_homework(self, student_id=None, use_cache=True):
        """Get all homework entries, optionally filtered by student."""
        cache_key = f"homework_{student_id}"
        
        if use_cache and cache_key in _cache:
            return _cache[cache_key]
        
        try:
            ws = self._spreadsheet.worksheet('Homework')
            expected_headers = ['assigned_date', 'due_date', 'student_name', 'homework_description', 
                               'chapter_ref', 'completed', 'shown_to_teacher', 'notes', 'completion_notes']
            records = ws.get_all_records(expected_headers=expected_headers)
            
            # Filter out empty rows
            records = [r for r in records if r.get('student_name', '').strip() or r.get('homework_description', '').strip()]
            
            if student_id:
                result = [r for r in records if str(r.get('student_name', '')) == str(student_id)]
            else:
                result = records
            
            _cache[cache_key] = result
            return result
        except Exception as e:
            raise Exception(f"Error fetching homework: {e}")
    
    def add_homework(self, data_dict):
        """Add a new homework entry."""
        try:
            ws = self._spreadsheet.worksheet('Homework')
            
            row = [
                data_dict.get('assigned_date', datetime.now().strftime('%Y-%m-%d')),
                data_dict.get('due_date', ''),
                data_dict.get('student_name', ''),
                data_dict.get('homework_description', data_dict.get('description', '')),
                data_dict.get('chapter_ref', ''),
                'No',  # completed
                'No',  # shown_to_teacher
                data_dict.get('notes', ''),
                ''  # completion_notes
            ]
            ws.append_row(row, value_input_option='USER_ENTERED')
            self._clear_cache()
            return True
        except Exception as e:
            raise Exception(f"Error adding homework: {e}")
    
    def update_homework_completion(self, row_index, completed, shown, notes=""):
        """Update homework completion status by row index."""
        try:
            ws = self._spreadsheet.worksheet('Homework')
            # Row index in gspread is 1-based, row 1 is header, row 2+ is data
            actual_row = row_index + 2  # +1 for header, +1 for 1-based index
            
            ws.update_cell(actual_row, 6, 'Yes' if completed else 'No')  # completed column
            ws.update_cell(actual_row, 7, 'Yes' if shown else 'No')  # shown_to_teacher column
            ws.update_cell(actual_row, 9, notes)  # completion_notes column
            
            self._clear_cache()
            return True
        except Exception as e:
            raise Exception(f"Error updating homework: {e}")
    
    def get_homework_by_student_month(self, student_id, month, year):
        """Get homework for a student in a specific month/year."""
        try:
            all_homework = self.get_all_homework(student_id, use_cache=False)
            
            month_val = int(float(str(month)))
            year_val = int(float(str(year)))
            
            filtered = []
            for hw in all_homework:
                try:
                    assigned_date = hw.get('assigned_date', '')
                    if assigned_date:
                        hw_date = datetime.strptime(str(assigned_date), '%Y-%m-%d')
                        if hw_date.month == month_val and hw_date.year == year_val:
                            filtered.append(hw)
                except Exception:
                    pass
            
            return filtered
        except Exception as e:
            raise Exception(f"Error fetching homework: {e}")
    
    def get_last_homework_for_student(self, student_id):
        """Get the most recent uncompleted homework for a student."""
        try:
            all_homework = self.get_all_homework(student_id, use_cache=False)
            
            # Filter uncompleted
            uncompleted = [hw for hw in all_homework if not hw.get('completed', False)]
            
            if not uncompleted:
                return None
            
            # Sort by assigned_date descending
            uncompleted.sort(key=lambda x: str(x.get('assigned_date', '')), reverse=True)
            return uncompleted[0]
        except Exception as e:
            raise Exception(f"Error fetching last homework: {e}")
    
    # ========== TEST METHODS ==========
    
    def get_all_tests(self, student_id=None, use_cache=True):
        """Get all test entries, optionally filtered by student."""
        cache_key = f"tests_{student_id}"
        
        if use_cache and cache_key in _cache:
            return _cache[cache_key]
        
        try:
            ws = self._spreadsheet.worksheet('Tests')
            records = ws.get_all_records()
            
            if student_id:
                result = [r for r in records if str(r.get('student_id', '')) == str(student_id)]
            else:
                result = records
            
            _cache[cache_key] = result
            return result
        except Exception as e:
            raise Exception(f"Error fetching tests: {e}")
    
    def add_test(self, data_dict):
        """Add a new test entry."""
        try:
            ws = self._spreadsheet.worksheet('Tests')
            import uuid
            test_id = str(uuid.uuid4())[:8]
            
            # Calculate percentage if marks provided
            marks = float(data_dict.get('marks_scored', 0))
            total = float(data_dict.get('total_marks', 100))
            percentage = (marks / total * 100) if total > 0 else 0
            
            row = [
                test_id,
                data_dict.get('student_id', ''),
                data_dict.get('student_name', ''),
                data_dict.get('test_date', datetime.now().strftime('%Y-%m-%d')),
                data_dict.get('chapter_ref', ''),
                data_dict.get('test_topic', ''),
                data_dict.get('marks_scored', 0),
                data_dict.get('total_marks', 100),
                percentage,
                data_dict.get('remarks', '')
            ]
            ws.append_row(row)
            self._clear_cache()
            return test_id
        except Exception as e:
            raise Exception(f"Error adding test: {e}")
    
    def get_tests_by_student_month(self, student_id, month, year):
        """Get tests for a student in a specific month/year."""
        try:
            all_tests = self.get_all_tests(student_id, use_cache=False)
            
            month_val = int(float(str(month)))
            year_val = int(float(str(year)))
            
            filtered = []
            for test in all_tests:
                try:
                    test_date = test.get('test_date', '')
                    if test_date:
                        t_date = datetime.strptime(str(test_date), '%Y-%m-%d')
                        if t_date.month == month_val and t_date.year == year_val:
                            filtered.append(test)
                except Exception:
                    pass
            
            return filtered
        except Exception as e:
            raise Exception(f"Error fetching tests: {e}")


# Standalone function for testing connection
def test_connection():
    """Test the Google Sheets connection."""
    try:
        db = SheetsDatabaseManager()
        students = db.get_all_students(use_cache=False)
        logs = db.get_teaching_logs(use_cache=False)
        homework = db.get_all_homework(use_cache=False)
        tests = db.get_all_tests(use_cache=False)
        
        worksheets = [ws.title for ws in db.spreadsheet.worksheets()]
        
        return {
            "success": True,
            "students": len(students),
            "logs": len(logs),
            "homework": len(homework),
            "tests": len(tests),
            "worksheets": worksheets
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

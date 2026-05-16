"""PDF Generator for progress reports using fpdf2."""
from fpdf import FPDF
import os

def safe_text(text):
    """
    Convert text to Latin-1 encoding, replacing unsupported characters.
    This ensures compatibility with PDF generation.
    """
    if text is None:
        return ""
    if isinstance(text, str):
        return text.encode('latin-1', errors='replace').decode('latin-1')
    return str(text).encode('latin-1', errors='replace').decode('latin-1')

def generate_pdf_report(
    student_name,
    tutor_name,
    month,
    year,
    report_content,
    output_path="progress_report.pdf"
):
    """
    Generate a PDF report with all sections and signature line.
    
    Args:
        student_name: Name of the student
        tutor_name: Name of the tutor
        month: Report month
        year: Report year
        report_content: The AI-generated report content
        output_path: Path where PDF will be saved
    
    Returns:
        str: Path to generated PDF file
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font('Helvetica', 'B', 16)
    pdf.multi_cell(0, 10, safe_text("TUTORING PROGRESS REPORT"), align='C')
    pdf.ln(5)
    
    # Header Information
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, safe_text(f"Student: {student_name}"), ln=True)
    pdf.cell(0, 8, safe_text(f"Tutor: {tutor_name}"), ln=True)
    pdf.cell(0, 8, safe_text(f"Period: {month}/{year}"), ln=True)
    pdf.ln(10)
    
    # Horizontal line
    pdf.set_draw_color(0, 0, 0)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Report Content
    pdf.set_font('Helvetica', '', 11)
    
    if report_content:
        sections = report_content.split('\n')
        for line in sections:
            line = line.strip()
            if not line:
                pdf.ln(3)
                continue
            
            # Check for section headers (usually lines ending with : or all caps)
            is_header = line.isupper() or line.endswith(':') or line.startswith('#')
            
            if is_header and len(line) < 100:
                pdf.ln(3)
                pdf.set_font('Helvetica', 'B', 12)
                pdf.multi_cell(0, 6, safe_text(line))
                pdf.set_font('Helvetica', '', 11)
            else:
                pdf.multi_cell(0, 6, safe_text(line))
    
    pdf.ln(15)
    
    # Signature Line
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, safe_text("Tutor Signature:"), ln=True)
    pdf.ln(10)
    pdf.set_draw_color(0, 0, 0)
    pdf.line(10, pdf.get_y(), 90, pdf.get_y())
    pdf.ln(8)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, safe_text("Date: ___________________"), ln=True)
    
    # Save PDF
    pdf.output(output_path)
    return output_path

def get_pdf_bytes(report_content, student_name, tutor_name, month, year):
    """
    Generate PDF and return as bytes for download.
    """
    from io import BytesIO
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font('Helvetica', 'B', 16)
    pdf.multi_cell(0, 10, safe_text("TUTORING PROGRESS REPORT"), align='C')
    pdf.ln(5)
    
    # Header Information
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, safe_text(f"Student: {student_name}"), ln=True)
    pdf.cell(0, 8, safe_text(f"Tutor: {tutor_name}"), ln=True)
    pdf.cell(0, 8, safe_text(f"Period: {month}/{year}"), ln=True)
    pdf.ln(10)
    
    # Horizontal line
    pdf.set_draw_color(0, 0, 0)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Report Content
    pdf.set_font('Helvetica', '', 11)
    
    if report_content:
        sections = report_content.split('\n')
        for line in sections:
            line = line.strip()
            if not line:
                pdf.ln(3)
                continue
            
            is_header = line.isupper() or line.endswith(':') or line.startswith('#')
            
            if is_header and len(line) < 100:
                pdf.ln(3)
                pdf.set_font('Helvetica', 'B', 12)
                pdf.multi_cell(0, 6, safe_text(line))
                pdf.set_font('Helvetica', '', 11)
            else:
                pdf.multi_cell(0, 6, safe_text(line))
    
    pdf.ln(15)
    
    # Signature Line
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, safe_text("Tutor Signature:"), ln=True)
    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 90, pdf.get_y())
    pdf.ln(8)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, safe_text("Date: ___________________"), ln=True)
    
    # Return bytes
    return pdf.output()

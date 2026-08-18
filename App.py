import io
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = Flask(__name__)

# Paletas de color predefinidas
COLOR_THEMES = {
    'blue': {'primary': '#1A365D', 'secondary': '#2B6CB0', 'text': '#2D3748', 'line': '#CBD5E0'},
    'dark': {'primary': '#1A202C', 'secondary': '#4A5568', 'text': '#2D3748', 'line': '#E2E8F0'},
    'green': {'primary': '#1C4532', 'secondary': '#2F855A', 'text': '#2D3748', 'line': '#C6F6D5'},
    'grey': {'primary': '#2D3748', 'secondary': '#718096', 'text': '#4A5568', 'line': '#E2E8F0'}
}

def build_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    theme = COLOR_THEMES.get(data.get('theme', 'blue'), COLOR_THEMES['blue'])
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CVTitle', parent=styles['Heading1'], fontSize=22, leading=26,
        textColor=colors.HexColor(theme['primary']), spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'CVSubtitle', parent=styles['Normal'], fontSize=9, leading=13,
        textColor=colors.HexColor('#718096'), spaceAfter=10
    )
    
    section_style = ParagraphStyle(
        'CVSection', parent=styles['Heading2'], fontSize=13, leading=17,
        textColor=colors.HexColor(theme['secondary']), spaceBefore=10, spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'CVBody', parent=styles['Normal'], fontSize=9.5, leading=13.5,
        textColor=colors.HexColor(theme['text']), spaceAfter=6
    )

    story = []

    # Encabezado
    story.append(Paragraph(data.get('fullName', 'Sin Nombre'), title_style))
    
    contact_info = [v for v in [
        data.get('email'), data.get('phone'), data.get('location'),
        data.get('linkedin'), data.get('github')
    ] if v]
    
    if contact_info:
        story.append(Paragraph(" • ".join(contact_info), subtitle_style))
    
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(theme['line']), spaceAfter=10))

    # Perfil / Resumen Profesional (Opcional)
    if data.get('summary'):
        story.append(Paragraph("Perfil Profesional", section_style))
        story.append(Paragraph(data['summary'].replace('\n', '<br/>'), body_style))

    # Educación
    if data.get('education'):
        story.append(Paragraph("Educación", section_style))
        story.append(Paragraph(data['education'].replace('\n', '<br/>'), body_style))

    # Experiencia Laboral (Opcional)
    if data.get('experience'):
        story.append(Paragraph("Experiencia Laboral", section_style))
        story.append(Paragraph(data['experience'].replace('\n', '<br/>'), body_style))

    # Proyectos Destacados (Opcional)
    if data.get('projects'):
        story.append(Paragraph("Proyectos Destacados", section_style))
        story.append(Paragraph(data['projects'].replace('\n', '<br/>'), body_style))

    # Cursos y Certificaciones (Opcional)
    if data.get('courses'):
        story.append(Paragraph("Cursos y Certificaciones", section_style))
        story.append(Paragraph(data['courses'].replace('\n', '<br/>'), body_style))

    # Habilidades / Idiomas (Opcional)
    if data.get('skills'):
        story.append(Paragraph("Habilidades y Tecnologías", section_style))
        story.append(Paragraph(data['skills'].replace('\n', '<br/>'), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = {
        'theme': request.form.get('theme', 'blue'),
        'fullName': request.form.get('fullName'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'location': request.form.get('location'),
        'linkedin': request.form.get('linkedin'),
        'github': request.form.get('github'),
        'summary': request.form.get('summary'),
        'education': request.form.get('education'),
        'experience': request.form.get('experience'),
        'projects': request.form.get('projects'),
        'courses': request.form.get('courses'),
        'skills': request.form.get('skills')
    }
    
    pdf_buffer = build_pdf(data)
    filename = f"CV_{data['fullName'].replace(' ', '_')}.pdf" if data['fullName'] else "Curriculum.pdf"
    
    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
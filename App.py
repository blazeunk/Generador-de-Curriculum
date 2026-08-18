import io
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = Flask(__name__)

def build_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CVTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'CVSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=12
    )
    
    section_style = ParagraphStyle(
        'CVSection',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'CVBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6
    )

    story = []

    # Encabezado: Nombre y Datos de Contacto
    story.append(Paragraph(data.get('fullName', 'Sin Nombre'), title_style))
    
    contact_info = []
    if data.get('email'): contact_info.append(data['email'])
    if data.get('phone'): contact_info.append(data['phone'])
    if data.get('location'): contact_info.append(data['location'])
    if data.get('linkedin'): contact_info.append(data['linkedin'])
    
    if contact_info:
        story.append(Paragraph(" | ".join(contact_info), subtitle_style))
    
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=10))

    # Nivel Académico
    if data.get('education'):
        story.append(Paragraph("Educación", section_style))
        story.append(Paragraph(data['education'].replace('\n', '<br/>'), body_style))

    # Experiencia Laboral (Opcional)
    if data.get('experience'):
        story.append(Paragraph("Experiencia Laboral", section_style))
        story.append(Paragraph(data['experience'].replace('\n', '<br/>'), body_style))

    # Cursos y Certificaciones (Opcional)
    if data.get('courses'):
        story.append(Paragraph("Cursos y Certificaciones", section_style))
        story.append(Paragraph(data['courses'].replace('\n', '<br/>'), body_style))

    # Habilidades / Idiomas (Opcional)
    if data.get('skills'):
        story.append(Paragraph("Habilidades e Idiomas", section_style))
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
        'fullName': request.form.get('fullName'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'location': request.form.get('location'),
        'linkedin': request.form.get('linkedin'),
        'education': request.form.get('education'),
        'experience': request.form.get('experience'),
        'courses': request.form.get('courses'),
        'skills': request.form.get('skills')
    }
    
    pdf_buffer = build_pdf(data)
    filename = f"CV_{data['fullName'].replace(' ', '_')}.pdf" if data['fullName'] else "Curriculum.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
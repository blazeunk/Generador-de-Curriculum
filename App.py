import io
import base64
from PIL import Image as PILImage
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import sys
import os
import signal
import threading

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

COLOR_THEMES = {
    'blue': {'primary': '#1A365D', 'secondary': '#2B6CB0', 'text': '#2D3748', 'line': '#CBD5E0'},
    'dark': {'primary': '#1A202C', 'secondary': '#4A5568', 'text': '#2D3748', 'line': '#E2E8F0'},
    'green': {'primary': '#1C4532', 'secondary': '#2F855A', 'text': '#2D3748', 'line': '#C6F6D5'},
    'grey': {'primary': '#2D3748', 'secondary': '#718096', 'text': '#4A5568', 'line': '#E2E8F0'}
}

def build_pdf(data, photo_base64=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    theme = COLOR_THEMES.get(data.get('theme', 'blue'), COLOR_THEMES['blue'])
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CVTitle', parent=styles['Heading1'], fontSize=20, leading=24,
        textColor=colors.HexColor(theme['primary']), spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'CVSubtitle', parent=styles['Normal'], fontSize=9, leading=13,
        textColor=colors.HexColor('#718096'), spaceAfter=4
    )
    
    section_style = ParagraphStyle(
        'CVSection', parent=styles['Heading2'], fontSize=12, leading=16,
        textColor=colors.HexColor(theme['secondary']), spaceBefore=8, spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'CVBody', parent=styles['Normal'], fontSize=9.5, leading=13.5,
        textColor=colors.HexColor(theme['text']), spaceAfter=6
    )

    story = []

    # Encabezado (Texto)
    header_text_elements = [
        Paragraph(data.get('fullName', 'Sin Nombre'), title_style)
    ]
    
    contact_info = [v for v in [
        data.get('email'), data.get('phone'), data.get('location'),
        data.get('linkedin'), data.get('github')
    ] if v]
    
    if contact_info:
        header_text_elements.append(Paragraph(" • ".join(contact_info), subtitle_style))

    # Procesar foto con Pillow -> BytesIO
    img_element = None
    if photo_base64 and len(photo_base64.strip()) > 0:
        try:
            if ',' in photo_base64:
                photo_base64 = photo_base64.split(',')[1]
            
            raw_bytes = base64.b64decode(photo_base64)
            pil_img = PILImage.open(io.BytesIO(raw_bytes))
            
            if pil_img.mode in ('RGBA', 'P'):
                pil_img = pil_img.convert('RGB')
                
            img_io = io.BytesIO()
            # Guardar en alta calidad
            pil_img.save(img_io, format='JPEG', quality=95) 
            img_io.seek(0)
            
            img_element = RLImage(img_io, width=1.1*inch, height=1.3*inch)
        except Exception as e:
            print("Error procesando imagen: {}".format(e))
            img_element = None

    if img_element:
        # Tabla para ubicar texto a la izquierda (432pt) y foto a la derecha (100pt)
        header_table = Table([[header_text_elements, img_element]], colWidths=[432, 100])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(header_table)
    else:
        story.extend(header_text_elements)
    
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(theme['line']), spaceBefore=8, spaceAfter=10))

    sections = [
        ('Perfil Profesional', 'summary'),
        ('Educación', 'education'),
        ('Experiencia Laboral', 'experience'),
        ('Proyectos Destacados', 'projects'),
        ('Cursos y Certificaciones', 'courses'),
        ('Habilidades y Tecnologías', 'skills'),
        ('Idiomas', 'languages')
    ]

    for title, key in sections:
        if data.get(key):
            story.append(Paragraph(title, section_style))
            story.append(Paragraph(data[key].replace('\n', '<br/>'), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

def extract_form_data(req):
    return {
        'theme': req.form.get('theme', 'blue'),
        'fullName': req.form.get('fullName'),
        'email': req.form.get('email'),
        'phone': req.form.get('phone'),
        'location': req.form.get('location'),
        'linkedin': req.form.get('linkedin'),
        'github': req.form.get('github'),
        'summary': req.form.get('summary'),
        'education': req.form.get('education'),
        'experience': req.form.get('experience'),
        'projects': req.form.get('projects'),
        'courses': req.form.get('courses'),
        'skills': req.form.get('skills'),
        'languages': req.form.get('languages')
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    data = extract_form_data(request)
    photo_b64 = request.form.get('photo_b64')
    pdf_buffer = build_pdf(data, photo_b64)
    return send_file(pdf_buffer, mimetype='application/pdf')

@app.route('/generate', methods=['POST'])
def generate():
    data = extract_form_data(request)
    photo_b64 = request.form.get('photo_b64')
    pdf_buffer = build_pdf(data, photo_b64)
    filename = f"CV_{data['fullName'].replace(' ', '_')}.pdf" if data['fullName'] else "Curriculum.pdf"
    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    # Apaga el proceso de Flask limpiamente
    def stop_server():
        os.kill(os.getpid(), signal.SIGINT)
        
    threading.Timer(1, stop_server).start()
    return 'Servidor cerrado', 200

if __name__ == '__main__':
    app.run(debug=True)
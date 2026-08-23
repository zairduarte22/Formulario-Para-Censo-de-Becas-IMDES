from flask import Flask, render_template, request, send_file, session, url_for, flash, redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os
from datetime import date, datetime
import gspread
import textwrap
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(32)

# Crear carpeta uploads si no existe
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Configuración de Google Sheets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_json = os.path.join(BASE_DIR, 'becas.json')
gc = gspread.service_account(filename=ruta_json)
sh = gc.open('BD').sheet1

@app.route('/')
def index():
    fecha_actual = date.today().isoformat()
    return render_template('formulario.html', fecha_actual=fecha_actual)

@app.route('/generar_pdf', methods=['POST'])
def generar_pdf():
    try:
        data_form = request.form
        cedula = data_form.get('cedula').strip()
        cedulas_existentes = sh.col_values(7)

        if cedula in cedulas_existentes:
            return render_template('error.html')

        # Convertimos a dict y guardamos las listas como texto unido por comas
        data_para_sesion = data_form.to_dict()
        data_para_sesion['dificultades'] = ", ".join(data_form.getlist('dificultades'))
        data_para_sesion['apoyos'] = ", ".join(data_form.getlist('apoyos'))

        session['data'] = data_para_sesion

        # Guardar en Google Sheets (usando los datos procesados)
        fila = [
            data_para_sesion.get('fecha'), data_para_sesion.get('estado'),
            data_para_sesion.get('municipio'), data_para_sesion.get('parroquia'),
            data_para_sesion.get('sector'), data_para_sesion.get('nombres_completos'),
            data_para_sesion.get('cedula'), data_para_sesion.get('genero'),
            data_para_sesion.get('fecha_nacimiento'), data_para_sesion.get('direccion'),
            data_para_sesion.get('correo'), data_para_sesion.get('telefono'),
            data_para_sesion.get('institucion'), data_para_sesion.get('grado'),
            data_para_sesion.get('turno'), data_para_sesion.get('tipo_institucion'),
            data_para_sesion.get('num_personas'), data_para_sesion.get('num_hermanos'),
            data_para_sesion.get('fuente_ingreso'), data_para_sesion.get('trabaja'),
            data_para_sesion.get('dificultades'), data_para_sesion.get('apoyos'),
            data_para_sesion.get('banco'), data_para_sesion.get('tipo_cuenta'),
            data_para_sesion.get('numero_cuenta'), data_para_sesion.get('servicio_comunitario'),
            data_para_sesion.get('horarios'), data_para_sesion.get('ubicacion_universidad')
        ]
        sh.append_row(fila)

        return redirect(url_for('confirmacion'))

    except Exception as e:
        print(f"Error en generar_pdf: {e}")
        flash("Hubo un error inesperado.", "error")
        return redirect(url_for('index'))

@app.route('/descargar_pdf')
def descargar_pdf():
    data = session.get('data')
    if not data:
        return "No hay datos disponibles para generar el PDF. Por favor, intente llenar el formulario de nuevo.", 400

    # Crear el buffer para el PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # 1. Cargar y dibujar imagen de fondo
    img_path = os.path.join('static', 'becas.png')
    try:
        img = ImageReader(img_path)
        pil_img = Image.open(img_path)
        img_width, img_height = pil_img.size

        # Escalar imagen a tamaño carta manteniendo aspecto
        scale = min(width / img_width, height / img_height)
        new_width = img_width * scale
        new_height = img_height * scale
        c.drawImage(img, 0, height - new_height, width=new_width, height=new_height)
    except Exception as e:
        print(f"Error cargando imagen: {e}")

    # 2. Configuración de fuente y Fecha
    c.setFont("Helvetica", 10)
    fecha_html = data.get('fecha', '') # "2026-02-09"

    if fecha_html and '-' in fecha_html:
        partes = fecha_html.split('-') # ['2026', '02', '09']
        fecha_final = f"{partes[2]}/{partes[1]}/{partes[0]}" # "09/02/2026"
    else:
        fecha_final = fecha_html

    c.drawString(520, height - 115, fecha_final)

    # 3. UBICACIÓN GEOGRÁFICA
    base_y = height - 185
    c.drawString(90, base_y, data.get('estado', ''))
    c.drawString(161, base_y + 2, data.get('municipio', ''))

    parroquia = data.get('parroquia', '')
    if parroquia == 'EL ROSARIO':
        c.drawString(300, 618, 'X')
    elif parroquia == 'SIXTO ZAMBRANO':
        c.drawString(320, 610, 'X')
    elif parroquia == 'DONALDO GARCÍA':
        c.drawString(320, 602, 'X')

    c.drawString(450, base_y, data.get('sector', ''))

    # 4. DATOS GENERALES DEL ESTUDIANTE
    base_y = height - 250
    c.drawString(60, base_y, data.get('nombres_completos', ''))
    c.drawString(270, base_y, data.get('cedula', ''))
    c.drawString(380, base_y, data.get('genero', ''))

    fecha_nacimiento_html = data.get('fecha_nacimiento', '') # "2026-02-09"

    if fecha_nacimiento_html and '-' in fecha_nacimiento_html:
        partes = fecha_nacimiento_html.split('-') # ['2026', '02', '09']
        fecha_nacimiento_final = f"{partes[2]}/{partes[1]}/{partes[0]}" # "09/02/2026"
    else:
        fecha_nacimiento_final = fecha_nacimiento_html

    c.drawString(470, base_y, fecha_nacimiento_final)

    direccion = data.get('direccion', '')
    lineas = textwrap.wrap(direccion, width=40, break_long_words=True)

    if len(lineas) > 1:
        base_y = height - 271
        c.setFont("Helvetica", 8)
    else:
        base_y = height - 273
        c.setFont("Helvetica", 10)
    for i, linea in enumerate(lineas):
        # Restamos 12 puntos de altura por cada línea nueva
        c.drawString(60, base_y - (i * 10), linea)

    base_y = height - 273
    c.drawString(322, base_y, data.get('correo', ''))
    c.drawString(470, base_y, data.get('telefono', ''))

    base_y = height - 297
    turno = data.get('turno', '')
    if turno == 'DIURNO': c.drawString(450, base_y, 'X')
    elif turno == 'VESPERTINO': c.drawString(505, base_y, 'X')
    elif turno == 'NOCTURNO': c.drawString(550, base_y, 'X')

    # 1. Obtenemos el texto
    institucion = data.get('institucion', '')
    lineas = textwrap.wrap(institucion, width=44, break_long_words=True)

    if len(lineas) > 1:
        base_y = height - 312
        c.setFont("Helvetica", 5)
    else:
        base_y = height - 320

    for i, linea in enumerate(lineas):
        # Restamos 12 puntos de altura por cada línea nueva
        c.drawString(60, base_y - (i * 12), linea)

    c.setFont("Helvetica", 10)
    base_y = height - 320
    c.drawString(300, base_y, data.get('grado', ''))

    base_y = height - 322
    tipo_inst = data.get('tipo_institucion', '')
    if tipo_inst == 'PUBLICA': c.drawString(452, base_y, 'X')
    elif tipo_inst == 'PRIVADA': c.drawString(510, base_y, 'X')

    # 5. SITUACIÓN SOCIOECONÓMICA
    base_y = height - 394
    c.drawString(70, base_y, data.get('num_personas', ''))
    c.drawString(185, base_y, data.get('num_hermanos', ''))

    fuente = data.get('fuente_ingreso', '')
    if fuente == 'FORMAL': c.drawString(330, base_y, 'X')
    elif fuente == 'INFORMAL': c.drawString(330, base_y - 6, 'X')

    trabaja = data.get('trabaja', '')
    if trabaja == 'SI': c.drawString(438, base_y - 5, 'X')
    elif trabaja == 'NO': c.drawString(475, base_y - 5, 'X')

    # 6. NECESIDADES ESPECÍFICAS (Lectura de strings de sesión)
    base_y = height - 497
    dificultades = data.get('dificultades', '') # Es un string tipo "utiles, transporte"

    if 'utiles' in dificultades: c.drawString(261, base_y, 'X')
    if 'matricula' in dificultades: c.drawString(261, base_y - 12, 'X')
    if 'transporte' in dificultades: c.drawString(261, base_y - 24, 'X')
    if 'tecnologia' in dificultades: c.drawString(261, base_y - 36, 'X')
    if 'alimentacion' in dificultades: c.drawString(261, base_y - 48, 'X')
    if 'hospedaje' in dificultades: c.drawString(261, base_y - 60, 'X')

    apoyos = data.get('apoyos', '')
    if 'ayuda_economica' in apoyos: c.drawString(544, base_y, 'X')
    if 'material_escolar' in apoyos: c.drawString(544, base_y - 12, 'X')
    if 'transporte_apoyo' in apoyos: c.drawString(544, base_y - 24, 'X')
    if 'alimentacion_apoyo' in apoyos: c.drawString(544, base_y - 36, 'X')
    if 'beca' in apoyos: c.drawString(544, base_y - 48, 'X')
    if 'empleo' in apoyos: c.drawString(544, base_y - 60, 'X')

    # 7. DATOS BANCARIOS
    base_y = height - 612
    c.drawString(60, base_y, data.get('banco', ''))
    c.drawString(300, base_y, data.get('tipo_cuenta', ''))
    c.drawString(60, height - 644, data.get('numero_cuenta', ''))

    # Finalizar PDF
    c.save()
    buffer.seek(0)

    # Limpiar datos de sesión para que no se repitan por accidente
    # session.pop('data', None) # Opcional: descomenta si quieres vaciarla tras descargar

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'beca_{data.get("cedula")}_{datetime.now().strftime("%Y%m%d")}.pdf'
    )


@app.route('/confirmacion')
def confirmacion():
    return render_template('confirmacion.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
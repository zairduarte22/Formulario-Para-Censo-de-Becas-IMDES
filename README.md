# Sistema de Becas Estudiantiles "Prof. Dilio Gutiérrez"

Sistema web desarrollado con Flask para la recopilación de información de solicitudes de becas estudiantiles y generación automática de PDFs con los datos ingresados.

## Características

- Formulario web interactivo y responsive
- Validación de campos obligatorios
- Generación automática de PDF con la información del formulario
- Diseño moderno y profesional
- Compatibilidad con dispositivos móviles

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Navega al directorio del proyecto:
```bash
cd becas_app
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Inicia la aplicación:
```bash
python app.py
```

2. Abre tu navegador y accede a:
```
http://localhost:5000
```

3. Completa el formulario con los datos del estudiante

4. Haz clic en "GENERAR PDF" para descargar el documento

## Estructura del Proyecto

```
becas_app/
│
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias del proyecto
├── static/
│   └── becas.png         # Imagen del formulario original
├── templates/
│   └── formulario.html   # Plantilla del formulario web
└── uploads/              # Carpeta para archivos temporales
```

## Secciones del Formulario

1. **Ubicación Geográfica**: Estado, municipio, parroquia y sector
2. **Datos Generales del Estudiante**: Información personal y académica
3. **Situación Socioeconómica**: Composición familiar y fuentes de ingreso
4. **Necesidades Específicas**: Dificultades económicas y tipos de apoyo requeridos
5. **Datos Bancarios**: Información bancaria para transferencias

## Tecnologías Utilizadas

- **Flask**: Framework web de Python
- **ReportLab**: Generación de documentos PDF
- **Pillow**: Procesamiento de imágenes
- **HTML/CSS**: Interfaz de usuario

## Notas

- El PDF generado incluye todos los datos del formulario superpuestos sobre la imagen del formulario original
- Los archivos PDF se descargan automáticamente con el formato: `beca_estudiantil_YYYYMMDD_HHMMSS.pdf`
- El formulario incluye validación en el cliente para asegurar que todos los campos requeridos estén completos

## Personalización

Para personalizar la aplicación:

- Modifica `templates/formulario.html` para cambiar el diseño del formulario
- Ajusta las coordenadas en `app.py` (función `generar_pdf`) para cambiar la posición del texto en el PDF
- Cambia la imagen en `static/becas.png` para usar un formato diferente

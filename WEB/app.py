from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from markupsafe import escape
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Necesaria para usar session

def obtener_idioma():
    lang = request.args.get("lang")
    
    # Si viene en la URL, lo guardamos
    if lang in ["es", "en", "ru"]:
        session["lang"] = lang
    
    # Si no hay nada guardado, usamos español por defecto
    return session.get("lang", "es")

# --- CONFIGURACIÓN DE CARGA ---
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- LÓGICA DE TIEMPO PARA EL TEMÁTICO ---

def obtener_hora_actual():
    """Calcula la hora para decidir si aplicar estilos de día o noche"""
    ahora = datetime.now()
    hora_formateada = ahora.strftime("%H:%M")
    hora_solo = int(ahora.strftime("%H"))
    return hora_formateada, hora_solo

@app.context_processor
def inject_hora_actual():
    """Inyecta variables de tiempo globalmente en todos los archivos HTML (Jinja2)"""
    hora_formateada, hora_solo = obtener_hora_actual()
    return dict(hora_actual=hora_formateada, hora_solo=hora_solo)

# --- RUTAS DE NAVEGACIÓN (VISTAS) ---

@app.route("/")
def presentacion():
    return render_template('index.html', lang=obtener_idioma())

@app.route("/Web")
def habilidades():
    return render_template('web.html', lang=obtener_idioma())

@app.route("/Juegos")
def juegos():
    return render_template('juegos.html', lang=obtener_idioma())

@app.route("/Hacking")
def hacking():
    return render_template('hacking.html', lang=obtener_idioma())

@app.route("/Suma")
def suma():
    return render_template('Suma.html', lang=obtener_idioma())

@app.route("/Soporte")
def soporte():
    return render_template('soporte.html', lang=obtener_idioma())

@app.route("/ProyectosIA")
def proyectos_ia():
    return render_template('ProyectosIA.html', lang=obtener_idioma())

# --- LÓGICA DE PROCESAMIENTO DE DATOS ---

@app.route("/sumapy", methods=["POST"])
def sumapy():
    """
    Recibe dos números por POST, realiza la operación en el servidor
    y responde con un JSON para que la página no tenga que recargarse.
    """
    try:
        num1 = float(request.form["num1"])
        num2 = float(request.form["num2"])
        result = num1 + num2
        return jsonify({"sum_result": float(result)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/clasificar_web", methods=["POST"])
def clasificar_web():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    modelo = request.form.get("modelo") # Obtener el modelo seleccionado

    url_ia = "http://ia-service:8080/clasificar" # URL del microservicio IA
    archivos = {'file': (file.filename, file.stream, file.mimetype)}
    datos = {'modelo': modelo}  # Enviar el modelo seleccionado al microservicio

    response = requests.post(url_ia, files=archivos, data=datos)
    return jsonify(response.json())

if __name__ == '__main__':
    # Ejecuta el servidor. Debug=True permite ver errores en tiempo real durante el desarrollo.
    # host='0.0.0.0' es CRÍTICO para Docker
    app.run(debug=False, host='0.0.0.0', port=5000)
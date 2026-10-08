from flask import Flask, request, jsonify, redirect, url_for, flash, session
import tensorflow as tf
import joblib
import numpy as np
import os

app = Flask(__name__)

# Carga de modelos de inteligencia artificial
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    extractor = tf.keras.models.load_model(os.path.join(BASE_DIR, 'modelo_extractor.h5'))
    modeloCNN = tf.keras.models.load_model(os.path.join(BASE_DIR, 'modelo_CNN.h5'))
    modeloTL = tf.keras.models.load_model(os.path.join(BASE_DIR, 'modelo_comidas.h5'))
    kmeans = joblib.load(os.path.join(BASE_DIR, 'modelo_kmeans.pkl'))
    print("¡Modelos cargados exitosamente desde rutas absolutas!")
except Exception as e:
    print(f"ERROR CRÍTICO AL CARGAR MODELOS: {e}")

# Diccionario de mapeo: Traduce el número de cluster de K-Means a una categoría humana.
# Basado en el análisis visual de los 15 clusters en Colab.
mapeo_clusters = {
    0: "Pizza", 6: "Pizza", 14: "Pizza",
    1: "Hamburguesa", 4: "Hamburguesa", 5: "Hamburguesa", 8: "Hamburguesa", 9: "Hamburguesa", 10: "Hamburguesa",
    2: "Perro Caliente", 7: "Perro Caliente", 12: "Perro Caliente",
    13: "Ilustración de Hamburguesa",
    11: "Empaque de comida",
    3: "Foto de comida con contexto"
}

# Mapeo para el modelo de clasificación
mapeo_comidas_tl = {0: "Hamburguesa", 1: "Perro Caliente", 2: "Pizza"}

# Mapeo para el modelo CNN
mapeo_animales_cnn = {0: "Babuino", 1: "Jirafa"}

def predecir_categoria(ruta_imagen, modelo):
    # 1. Carga básica común
    img = tf.keras.preprocessing.image.load_img(ruta_imagen, target_size=(224, 224))
    x = tf.keras.preprocessing.image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    
    if modelo == 1:
        # K-Means usa MobileNetV2 -> Rango [-1, 1]
        x_mobile = tf.keras.applications.mobilenet_v2.preprocess_input(x.copy())
        print("Modelo K-Means: Procesando...")
        vector = extractor.predict(x_mobile)
        cluster_detectado = kmeans.predict(vector)[0]
        return mapeo_clusters.get(cluster_detectado, "Desconocido")

    elif modelo == 2:
        # Transfer Learning usa MobileNetV2 -> Rango [-1, 1]
        x_mobile = tf.keras.applications.mobilenet_v2.preprocess_input(x.copy())
        print("Modelo TL: Procesando...")
        prediccion = modeloTL.predict(x_mobile)
        indice = np.argmax(prediccion, axis=1)[0]
        return mapeo_comidas_tl.get(indice, f"Clase {indice}")
    
    else:
        # CNN PERSONALIZADA -> Rango [0, 1]
        x_cnn = x / 255.0 
        print("Modelo CNN personalizado: Procesando con escala 1/255...")
        prediccion = modeloCNN.predict(x_cnn)
        print(f"Salida cruda del modelo CNN: {prediccion}")
        indice = np.argmax(prediccion, axis=1)[0]
        return mapeo_animales_cnn.get(indice, f"Clase {indice}")

# --- CONFIGURACIÓN DE CARGA ---
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ruta para la Clasificacion de Imágenes
@app.route("/clasificar", methods=["POST"])
def clasificar():
    if 'file' not in request.files:
        return jsonify({"error": "No hay archivo"}), 400
    
    file = request.files['file']
    modelo = int(request.form.get('modelo'))
    if file.filename == '':
        return jsonify({"error": "Archivo vacío"}), 400

    if file:
        # Guardar imagen temporalmente
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        try:
            # Llamamos a tu función mágica de IA
            resultado = predecir_categoria(filepath, modelo)
            
            # Borrar la imagen después de procesar para no llenar el disco
            os.remove(filepath) 
            
            return jsonify({"categoria": resultado})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
if __name__ == '__main__':
    # Ejecuta el servidor. Debug=True permite ver errores en tiempo real durante el desarrollo.
    # host='0.0.0.0' es CRÍTICO para Docker
    app.run(debug=False, host='0.0.0.0', port=8080)
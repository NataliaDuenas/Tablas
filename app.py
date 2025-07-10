from flask import Flask, render_template, request, send_file
import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
RESULT_FILE = 'static/codigos_leidos.txt'

# Crear carpeta de subida si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = []

    if request.method == 'POST':
        # Limpiar carpeta de subidas anterior
        for f in os.listdir(UPLOAD_FOLDER):
            os.remove(os.path.join(UPLOAD_FOLDER, f))

        files = request.files.getlist('images')
        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Leer imagen y decodificar códigos
            image = cv2.imread(filepath)
            if image is None:
                resultados.append((filename, "Error al leer"))
                continue

            barcodes = decode(image)
            if not barcodes:
                resultados.append((filename, "sin código"))
            else:
                for barcode in barcodes:
                    dato = barcode.data.decode("utf-8")
                    resultados.append((filename, dato))

        # Guardar resultados en archivo txt
        with open(RESULT_FILE, "w") as f:
            for nombre, codigo in resultados:
                f.write(f"{nombre}: {codigo}\n")

    return render_template('index.html', resultados=resultados)

@app.route('/descargar')
def descargar():
    return send_file(RESULT_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

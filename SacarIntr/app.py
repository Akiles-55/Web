import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, send_file
import io

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'separated_audio'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index(tracks=None):
    return render_template('index.html', tracks=tracks)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        # Guardar el archivo subido
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Ejecutar Demucs para extraer las pistas
        command = ["demucs", filepath, "-o", app.config['OUTPUT_FOLDER']]
        subprocess.run(command, check=True)

        # Extraer el nombre del archivo sin la extensión
        filename_without_ext = os.path.splitext(file.filename)[0]
        separated_folder = os.path.join(app.config['OUTPUT_FOLDER'], filename_without_ext)

        # Verificar si el directorio de las pistas separadas existe
        if os.path.exists(separated_folder):
            # Listar las pistas separadas
            tracks = [os.path.join(separated_folder, track) for track in os.listdir(separated_folder) if track.endswith('.wav')]

            # Mostrar las pistas en el index
            return render_template('index.html', tracks=tracks)

        else:
            return "Error: No se encontraron las pistas separadas."

@app.route('/download/<path:track>')
def download_file(track):
    with open(track, 'rb') as f:
        return send_file(io.BytesIO(f.read()), mimetype='audio/wav', as_attachment=True, download_name=os.path.basename(track))

if __name__ == '__main__':
    app.run(debug=True)

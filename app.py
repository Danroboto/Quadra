from flask import Flask, request, jsonify
from flask_cors import CORS
from db_config import get_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/puestos', methods=['GET'])
def get_puestos():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT p.*, 
               IFNULL(AVG(c.calificacion), 0) AS promedio_calificacion,
               COUNT(c.id) AS total_comentarios
        FROM puestos p
        LEFT JOIN comentarios c ON p.id = c.puesto_id
        GROUP BY p.id
    """)
    puestos = cur.fetchall()

    cur.close()
    conn.close()

    for puesto in puestos:
        puesto['promedio_calificacion'] = float(puesto['promedio_calificacion'])

    return jsonify(puestos)

@app.route('/puestos', methods=['POST'])
def crear_puesto():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    latitud = request.form.get('latitud')
    longitud = request.form.get('longitud')
    foto = request.files.get('foto')

    if not all([nombre, descripcion, latitud, longitud, foto]):
        return jsonify({'error': 'Faltan datos'}), 400

    filename = foto.filename
    foto.save(f'static/uploads/{filename}')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO puestos (nombre, descripcion, latitud, longitud, foto)
        VALUES (%s, %s, %s, %s, %s)
    """, (nombre, descripcion, latitud, longitud, filename))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Puesto creado'}), 201

@app.route('/puestos/<int:puesto_id>/comentarios', methods=['POST'])
def agregar_comentario(puesto_id):
    data = request.get_json()
    comentario = data.get('comentario')
    calificacion = data.get('calificacion')

    if not comentario or not calificacion:
        return jsonify({'error': 'Comentario y calificación son requeridos'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO comentarios (puesto_id, comentario, calificacion)
        VALUES (%s, %s, %s)
    """, (puesto_id, comentario, calificacion))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Comentario agregado correctamente'}), 201

if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from config.config import config
import hashlib  # Importa hashlib para el cifrado de contraseñas

login_routes = Blueprint('login', __name__)

# Configura CORS para permitir todas las solicitudes desde cualquier origen
app = Flask(__name__)
CORS(app, resources={r"/login/*": {"origins": ["http://localhost:4200", "http://127.0.0.1:4200"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})

config_db = config["database"]

PREFIX = "/login"

# Configuración de la base de datos
def db_config():
    try:
        connection = mysql.connector.connect(
            host=config_db["host"],
            port=config_db["port"],
            user=config_db["user"],
            password=config_db["password"],
            database=config_db["database"]
        )
        return connection
    except Error as err:
        print(f"Error connecting to the database: {err}")
        return None

# Buscar usuario por email
def find_user_by_email(email):
    conn = db_config()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Cifrado de la contraseña
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()  # Usar SHA-256 para cifrar la contraseña

# Registro de usuario
@login_routes.route(f"{PREFIX}/register", methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Cifra la contraseña antes de guardarla
    hashed_password = hash_password(password)

    conn = db_config()
    if conn is None:
        return jsonify({'message': 'Conexión a la base de datos fallida'}), 500

    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO users (name, email, password) VALUES (%s, %s, %s)''',
                       (name, email, hashed_password))  # Guardamos la contraseña cifrada
        conn.commit()
        return jsonify({'message': 'Usuario registrado correctamente'}), 200
    except Error as err:
        return jsonify({'message': f'Error al registrar el usuario: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@login_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    # Buscar usuario por correo
    user = find_user_by_email(email)

    if user:
        # Compara la contraseña cifrada
        if user['password'] == hash_password(password):
            return jsonify({"message": "Inicio de sesión exitoso"}), 200
        else:
            print(f"Contraseña incorrecta para el usuario: {email}")  # Añadir log
            return jsonify({"message": "Credenciales inválidas"}), 401
    else:
        print(f"Usuario no encontrado: {email}")  # Añadir log
        return jsonify({"message": "Credenciales inválidas"}), 401

# Agregar manejo para las solicitudes OPTIONS (para CORS)
@app.route('/login', methods=['OPTIONS'])
def handle_options():
    response = jsonify()
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response

# Registra las rutas de login
app.register_blueprint(login_routes)

# Levantar la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

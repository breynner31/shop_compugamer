from flask import Blueprint, jsonify, request, send_from_directory
import mysql.connector
import os
import logging
from mysql.connector import Error
from werkzeug.utils import secure_filename
from config.config import config

# Configuración básica
home_routes = Blueprint('home', __name__)
config_db = config["database"]

# Configuración para manejo de archivos (imágenes)
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Extensiones permitidas

# Asegurarse de que la carpeta de subida exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Función para establecer la conexión con la base de datos
def db_config():
    try:
        connection = mysql.connector.connect(
            host=config_db["host"],
            port=config_db["port"],
            user=config_db["user"],
            password=config_db["password"],
            database=config_db["database"]
        )
        if connection.is_connected():
            logging.info("Conexión exitosa a la base de datos.")
            return connection
        else:
            logging.error("No se pudo conectar a la base de datos.")
            return None
    except Error as err:
        logging.error(f"Error al conectar con la base de datos: {err}")
        return None


# Función para verificar que el archivo es una imagen válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Ruta para obtener productos
@home_routes.route('/home', methods=['GET'])
def obtener_productos_home():
    try:
        logging.info("Intentando conectar a la base de datos...")
        connection = db_config()
        if connection is None:
            return jsonify({'message': 'Error en la conexión a la base de datos'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM productos')  # Asegúrate de que la tabla `productos` existe
        productos = cursor.fetchall()
        cursor.close()
        connection.close()

        if len(productos) == 0:
            return jsonify({'message': 'No hay productos disponibles'}), 200

        # Asignar la ruta de imagen correctamente
        for producto in productos:
            imagen = producto['imagen']
            if isinstance(imagen, bytes):
                imagen = imagen.decode('utf-8')

            # Verificar si la imagen ya tiene el prefijo '/uploads/'
            if imagen.startswith('uploads/'):
                producto['imagen'] = f"/{imagen}"  # Ya tiene el prefijo correcto
            else:
                producto['imagen'] = f"/uploads/{imagen}"  # Añadir el prefijo si no lo tiene

        return jsonify(productos), 200
    except Exception as e:
        logging.error(f"Error al obtener productos: {e}")
        return jsonify({'message': f'Error al obtener productos: {str(e)}'}), 500


# Ruta para registrar productos
@home_routes.route('/productos', methods=['POST'])
def registrar_producto():
    try:
        logging.info("Solicitud POST a /productos recibida")

        # Verificar que se haya enviado un archivo de imagen
        if 'imagen' not in request.files:
            return jsonify({'message': 'No se ha enviado ninguna imagen'}), 400

        imagen = request.files['imagen']
        if imagen.filename == '':
            return jsonify({'message': 'No se seleccionó ninguna imagen'}), 400

        if imagen and allowed_file(imagen.filename):
            # Guardar la imagen en el servidor
            filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(UPLOAD_FOLDER, filename)
            logging.info(f"Guardando imagen en: {imagen_path}")
            imagen.save(imagen_path)

            # Obtener los datos del producto
            data = request.form  # Usamos form para recibir texto y archivo
            nombre = data['name']
            descripcion = data['descripcion']
            precio = data['precio']

            # Conexión a la base de datos
            connection = db_config()
            if connection is None:
                return jsonify({'message': 'Error en la conexión a la base de datos'}), 500

            cursor = connection.cursor()
            query = 'INSERT INTO productos (name, descripcion, precio, imagen) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (nombre, descripcion, precio, filename))
            connection.commit()

            cursor.close()
            connection.close()

            return jsonify({'message': 'Producto registrado exitosamente'}), 201
        else:
            return jsonify({'message': 'Archivo de imagen no válido'}), 400
    except Exception as e:
        logging.error(f"Error al registrar producto: {e}")
        return jsonify({'message': f'Error al registrar el producto: {str(e)}'}), 500
    

# Ruta para servir imágenes
@home_routes.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        logging.error(f"Error al servir archivo: {e}")
        return jsonify({'message': f'Error al servir el archivo: {str(e)}'}), 500


# Ruta para eliminar productos
@home_routes.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    try:
        # Conexión a la base de datos
        connection = db_config()
        if connection is None:
            return jsonify({'message': 'Error en la conexión a la base de datos'}), 500

        cursor = connection.cursor()

        # Verificar si el producto existe
        cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
        producto = cursor.fetchone()
        if producto is None:
            return jsonify({'message': 'Producto no encontrado'}), 404

        # Eliminar el producto
        cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'message': 'Producto eliminado exitosamente'}), 200
    except Exception as e:
        logging.error(f"Error al eliminar producto: {e}")
        return jsonify({'message': f'Error al eliminar el producto: {str(e)}'}), 500
    

# Ruta para obtener un producto por ID
@home_routes.route('/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    try:
        logging.info(f"Solicitud GET a /productos/{id} recibida para obtener producto")
        
        # Conexión a la base de datos
        connection = db_config()
        if connection is None:
            return jsonify({'message': 'Error en la conexión a la base de datos'}), 500
        
        # Obtener el producto de la base de datos
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
        producto = cursor.fetchone()

        if producto is None:
            return jsonify({'message': 'Producto no encontrado'}), 404
        
        # Crear un diccionario con los datos del producto, excluyendo la imagen binaria
        producto_data = {
            'id': producto[0],
            'name': producto[1],
            'descripcion': producto[2],
            'precio': producto[3],
            'imagen': producto[4].decode('utf-8') if isinstance(producto[4], bytes) else producto[4]  # Convertir la imagen a string si es de tipo bytes
        }

        cursor.close()
        connection.close()

        return jsonify(producto_data), 200
    except Exception as e:
        logging.error(f"Error al obtener producto: {e}")
        return jsonify({'message': f'Error al obtener el producto: {str(e)}'}), 500




# Ruta para editar productos
@home_routes.route('/productos/<int:id>', methods=['PUT'])
def editar_producto(id):
    try:
        logging.info("Solicitud PUT a /productos recibida para editar producto con id %s", id)

        # Conexión a la base de datos
        connection = db_config()
        if connection is None:
            return jsonify({'message': 'Error en la conexión a la base de datos'}), 500

        # Obtener los datos del formulario
        data = request.form  # Usamos form para recibir texto y archivo
        nombre = data.get('name')
        descripcion = data.get('descripcion')
        precio = data.get('precio')

        # Verificar si se ha enviado un archivo de imagen
        imagen = None
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen.filename != '' and allowed_file(imagen.filename):
                # Guardar la nueva imagen
                filename = secure_filename(imagen.filename)
                imagen_path = os.path.join(UPLOAD_FOLDER, filename)
                imagen.save(imagen_path)
                imagen = filename

        # Actualizar los campos del producto
        cursor = connection.cursor()

        # Verificar si el producto existe
        cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
        producto = cursor.fetchone()
        if producto is None:
            return jsonify({'message': 'Producto no encontrado'}), 404

        # Preparar la consulta de actualización
        query = '''
            UPDATE productos
            SET name = %s, descripcion = %s, precio = %s
        '''
        values = [nombre, descripcion, precio]
        
        # Si hay una nueva imagen, añadirla a la consulta
        if imagen:
            query += ', imagen = %s'
            values.append(imagen)

        query += ' WHERE id = %s'
        values.append(id)

        cursor.execute(query, tuple(values))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'message': 'Producto actualizado exitosamente'}), 200
    except Exception as e:
        logging.error(f"Error al editar producto: {e}")
        return jsonify({'message': f'Error al editar el producto: {str(e)}'}), 500

from flask import Blueprint, jsonify, request
from mysql.connector import Error
import logging
from config.config import config
import mysql.connector
import base64

# Configuración básica
productos_vendidos_routes = Blueprint('productos_vendidos', __name__)
config_db = config["database"]

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


# Endpoint para marcar un producto como vendido
@productos_vendidos_routes.route('/productos/<int:id>/vendido', methods=['POST'])
def marcar_como_vendido(id):
    try:
        connection = db_config()
        if connection is None:
            return jsonify({'message': 'Error en la conexión a la base de datos'}), 500

        cursor = connection.cursor()

        # Verificar si el producto existe
        cursor.execute('SELECT name, descripcion, precio, imagen FROM productos WHERE id = %s', (id,))
        producto = cursor.fetchone()

        if producto is None:
            return jsonify({'message': 'Producto no encontrado'}), 404

        # Mover el producto a la tabla de vendidos
        cursor.execute('''
            INSERT INTO productos_vendidos (name, descripcion, precio, imagen)
            SELECT name, descripcion, precio, imagen FROM productos WHERE id = %s
        ''', (id,))
        cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'message': f'Producto "{producto[0]}" marcado como vendido y movido a la lista de vendidos.'}), 200
    except Exception as e:
        logging.error(f"Error al marcar producto como vendido: {e}")
        return jsonify({'message': f'Error al marcar producto como vendido: {str(e)}'}), 500


@productos_vendidos_routes.route('/productos_vendidos', methods=['GET'])
def obtener_productos_vendidos():
    try:
        connection = db_config()
        if connection is None:
            return jsonify({'message': 'Error en la conexión a la base de datos'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT  name  FROM productos_vendidos')
        productos_vendidos = cursor.fetchall()


        cursor.close()
        connection.close()

        if not productos_vendidos:
            logging.info("No hay productos vendidos en la base de datos.")
            return jsonify({'message': 'No hay productos vendidos.'}), 200

        return jsonify(productos_vendidos), 200
    except Exception as e:
        logging.error(f"Error al obtener productos vendidos: {e}")
        return jsonify({'message': f'Error al obtener productos vendidos: {str(e)}'}), 500


@productos_vendidos_routes.route('/productos_vendidos/<int:id>', methods=['DELETE'])
def eliminar_producto_vendido(id):
    try:
        connection = db_config()
        if connection is None:
            return jsonify({'message': 'Error en la conexión a la base de datos'}), 500

        cursor = connection.cursor()

        # Verificar si el producto existe
        cursor.execute('SELECT id, name FROM productos_vendidos WHERE id = %s', (id,))
        producto = cursor.fetchone()

        if producto is None:
            return jsonify({'message': 'Producto no encontrado'}), 404

        # Eliminar el producto de la tabla de vendidos
        cursor.execute('DELETE FROM productos_vendidos WHERE id = %s', (id,))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'message': f'Producto "{producto[1]}" eliminado de la lista de vendidos.'}), 200
    except Exception as e:
        logging.error(f"Error al eliminar producto: {e}")
        return jsonify({'message': f'Error al eliminar producto: {str(e)}'}), 500
    


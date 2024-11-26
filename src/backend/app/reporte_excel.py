import pandas as pd
from flask import Blueprint, jsonify, request, send_file
from mysql.connector import Error
import logging
from config.config import config
import mysql.connector
from io import BytesIO

reporte_excel_routes = Blueprint('reporte_excel', __name__)
config_db = config["database"]
logging.basicConfig(level=logging.INFO)

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

@reporte_excel_routes.route('/productos_vendidos/exportar', methods=['GET'])
def exportar_productos_vendidos():
    try:
        # Conectar a la base de datos
        connection = db_config()
        if connection is None:
            return jsonify({'message': 'Error en la conexión a la base de datos'}), 500

        # Consultar los productos vendidos
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT id, name, descripcion, precio, imagen FROM productos_vendidos')
        productos_vendidos = cursor.fetchall()

        cursor.close()
        connection.close()

        if not productos_vendidos:
            logging.info("No hay productos vendidos en la base de datos.")
            return jsonify({'message': 'No hay productos vendidos para exportar.'}), 200

        # Crear un DataFrame con los productos vendidos
        df = pd.DataFrame(productos_vendidos)

        # Guardar el DataFrame en un archivo Excel en memoria
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        # Enviar el archivo Excel para descarga
        return send_file(
            output,
            as_attachment=True,
            download_name="productos_vendidos.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        logging.error(f"Error al exportar productos vendidos: {e}")
        return jsonify({'message': f'Error al exportar productos vendidos: {str(e)}'}), 500

from flask import Flask
from home import home_routes
from login import login_routes  # Importar las rutas desde home.py
from flask_cors import CORS
from reporte_excel import reporte_excel_routes
from productos_vendidos import productos_vendidos_routes

app = Flask(__name__)

# Habilitar CORS si es necesario
CORS(app, resources={r"/*": {"origins": ["http://localhost:4200", "http://127.0.0.1:9001"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})

# Registrar el blueprint
app.register_blueprint(home_routes)
app.register_blueprint(login_routes)
app.register_blueprint(reporte_excel_routes)
app.register_blueprint(productos_vendidos_routes)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)

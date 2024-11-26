import os 

config = {
    'login': {
        'host': os.getenv('HOST', '0.0.0.0'),
        'port': os. getenv('PORT', 5003),
        'debug': os.getenv('DEBUG', False)
    },
    'database': {
        'host': os.getenv('DB_HOST', '52.73.166.14'),
        'port': os.getenv('PORT', 3306),
        'user': os.getenv('USER', 'root'),
        'password': os.getenv('PASSWORD', '3XM5gj7U1/97P=£'),
        'database': os.getenv('DATABASE', 'db_compugamer')
    }
}
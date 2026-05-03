from flask import Flask, render_template
import urllib.request

app = Flask(__name__)
APPS = [
    {'id': 1,  'nombre': 'Clientes',     'icono': '👤', 'puerto': 5001, 'host': 'app1-clientes',  'ip_abrir': 'localhost'},
    {'id': 2,  'nombre': 'Citas',        'icono': '📅', 'puerto': 5002, 'host': 'app2-citas',     'ip_abrir': 'localhost'},
    {'id': 3,  'nombre': 'Servicios',    'icono': '✂',  'puerto': 5003, 'host': 'app3-servicios', 'ip_abrir': 'localhost'},
    {'id': 4,  'nombre': 'Barberos',     'icono': '💈', 'puerto': 5004, 'host': 'app4-barberos',  'ip_abrir': 'localhost'},
    {'id': 5,  'nombre': 'Productos',    'icono': '🧴', 'puerto': 5005, 'host': 'app5-productos', 'ip_abrir': 'localhost'},
    {'id': 6,  'nombre': 'Ventas',       'icono': '💰', 'puerto': 5006, 'host': 'app6-ventas',    'ip_abrir': 'localhost'},
    {'id': 7,  'nombre': 'Proveedores',  'icono': '🚚', 'puerto': 5007, 'host': '192.168.1.18',   'ip_abrir': '192.168.1.18'},
    {'id': 8,  'nombre': 'Gastos',       'icono': '📊', 'puerto': 5008, 'host': '192.168.1.18',   'ip_abrir': '192.168.1.18'},
    {'id': 9,  'nombre': 'Turnos',       'icono': '🕐', 'puerto': 5009, 'host': '192.168.1.18',   'ip_abrir': '192.168.1.18'},
    {'id': 10, 'nombre': 'Reportes',     'icono': '📈', 'puerto': 5010, 'host': '192.168.1.18',   'ip_abrir': '192.168.1.18'},
    {'id': 11, 'nombre': 'Fidelización', 'icono': '⭐', 'puerto': 5011, 'host': '192.168.1.18',   'ip_abrir': '192.168.1.18'},
    {'id': 12, 'nombre': 'Sucursales',   'icono': '📍', 'puerto': 5012, 'host': '192.168.1.18',   'ip_abrir': '192.168.1.18'},
]
def ping(host, puerto):
    try:
        urllib.request.urlopen(f'http://{host}:{puerto}', timeout=1)
        return True
    except:
        return False

@app.route('/')
def index():
    apps = [{**a, 'activo': ping(a['host'], a['puerto'])} for a in APPS]
    return render_template('dashboard.html', apps=apps)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
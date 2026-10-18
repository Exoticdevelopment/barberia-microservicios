from flask import Flask, render_template
import os
import urllib.request

app = Flask(__name__)

# Host que usa el navegador para abrir cada app (los puertos están publicados en la máquina que corre Docker).
PUBLIC_HOST = os.getenv('PUBLIC_HOST', 'localhost')

APPS = [
    {'id': 1,  'nombre': 'Clientes',     'icono': '👤', 'puerto': 5001, 'host': 'app1-clientes',      'grupo': 'operacion'},
    {'id': 2,  'nombre': 'Citas',        'icono': '📅', 'puerto': 5002, 'host': 'app2-citas',         'grupo': 'operacion'},
    {'id': 3,  'nombre': 'Servicios',    'icono': '✂',  'puerto': 5003, 'host': 'app3-servicios',     'grupo': 'operacion'},
    {'id': 4,  'nombre': 'Barberos',     'icono': '💈', 'puerto': 5004, 'host': 'app4-barberos',      'grupo': 'operacion'},
    {'id': 5,  'nombre': 'Productos',    'icono': '🧴', 'puerto': 5005, 'host': 'app5-productos',     'grupo': 'operacion'},
    {'id': 6,  'nombre': 'Ventas',       'icono': '💰', 'puerto': 5006, 'host': 'app6-ventas',        'grupo': 'operacion'},
    {'id': 7,  'nombre': 'Proveedores',  'icono': '🚚', 'puerto': 5007, 'host': 'app7-proveedores',   'grupo': 'administracion'},
    {'id': 8,  'nombre': 'Gastos',       'icono': '📊', 'puerto': 5008, 'host': 'app8-gastos',        'grupo': 'administracion'},
    {'id': 9,  'nombre': 'Turnos',       'icono': '🕐', 'puerto': 5009, 'host': 'app9-turnos',        'grupo': 'administracion'},
    {'id': 10, 'nombre': 'Reportes',     'icono': '📈', 'puerto': 5010, 'host': 'app10-reportes',     'grupo': 'administracion'},
    {'id': 11, 'nombre': 'Fidelización', 'icono': '⭐', 'puerto': 5011, 'host': 'app11-fidelizacion', 'grupo': 'administracion'},
    {'id': 12, 'nombre': 'Sucursales',   'icono': '📍', 'puerto': 5012, 'host': 'app12-sucursales',   'grupo': 'administracion'},
]

def ping(host, puerto):
    try:
        urllib.request.urlopen(f'http://{host}:{puerto}', timeout=1)
        return True
    except Exception:
        return False

@app.route('/')
def index():
    apps = [{**a, 'activo': ping(a['host'], a['puerto'])} for a in APPS]
    return render_template('dashboard.html', apps=apps, public_host=PUBLIC_HOST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

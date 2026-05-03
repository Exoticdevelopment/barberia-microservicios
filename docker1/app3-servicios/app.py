from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    precio = db.Column(db.Float)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    servicios = Servicio.query.all()
    return render_template('index.html', servicios=servicios, modulo='Servicios')

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        s = Servicio(
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            precio=float(request.form['precio'])
        )
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', servicio=None, modulo='Servicios')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    s = Servicio.query.get_or_404(id)
    if request.method == 'POST':
        s.nombre = request.form['nombre']
        s.descripcion = request.form['descripcion']
        s.precio = float(request.form['precio'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', servicio=s, modulo='Servicios')

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Servicio.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    servicios = Servicio.query.all()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['id', 'nombre', 'descripcion', 'precio'])
    for s in servicios:
        writer.writerow([s.id, s.nombre, s.descripcion, s.precio])
    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = 'attachment; filename=servicios.csv'
    output.headers['Content-type'] = 'text/csv'
    return output

@app.route('/importar', methods=['POST'])
def importar():
    archivo = request.files['archivo']
    stream = io.StringIO(archivo.stream.read().decode('utf-8'))
    reader = csv.DictReader(stream)
    for row in reader:
        if not Servicio.query.get(int(row['id'])):
            db.session.add(Servicio(
                nombre=row['nombre'],
                descripcion=row['descripcion'],
                precio=float(row['precio'])
            ))
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)
    
    
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    ultima_visita = db.Column(db.String(20))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    clientes = Cliente.query.all()
    return render_template('index.html', clientes=clientes, modulo='Clientes')

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        c = Cliente(
            nombre=request.form['nombre'],
            telefono=request.form['telefono'],
            ultima_visita=request.form['ultima_visita']
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', cliente=None, modulo='Clientes')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    c = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        c.nombre = request.form['nombre']
        c.telefono = request.form['telefono']
        c.ultima_visita = request.form['ultima_visita']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', cliente=c, modulo='Clientes')

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Cliente.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    clientes = Cliente.query.all()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['id', 'nombre', 'telefono', 'ultima_visita'])
    for c in clientes:
        writer.writerow([c.id, c.nombre, c.telefono, c.ultima_visita])
    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = 'attachment; filename=clientes.csv'
    output.headers['Content-type'] = 'text/csv'
    return output

@app.route('/importar', methods=['POST'])
def importar():
    archivo = request.files['archivo']
    stream = io.StringIO(archivo.stream.read().decode('utf-8'))
    reader = csv.DictReader(stream)
    for row in reader:
        if not Cliente.query.get(int(row['id'])):
            db.session.add(Cliente(
                nombre=row['nombre'],
                telefono=row['telefono'],
                ultima_visita=row['ultima_visita']
            ))
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
    
    
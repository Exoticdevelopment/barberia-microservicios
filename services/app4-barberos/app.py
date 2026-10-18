from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Barbero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    turno = db.Column(db.String(50))
    especialidad = db.Column(db.String(100))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    barberos = Barbero.query.all()
    return render_template('index.html', barberos=barberos, modulo='Barberos')

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        b = Barbero(
            nombre=request.form['nombre'],
            turno=request.form['turno'],
            especialidad=request.form['especialidad']
        )
        db.session.add(b)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', barbero=None, modulo='Barberos')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    b = Barbero.query.get_or_404(id)
    if request.method == 'POST':
        b.nombre = request.form['nombre']
        b.turno = request.form['turno']
        b.especialidad = request.form['especialidad']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', barbero=b, modulo='Barberos')

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Barbero.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    barberos = Barbero.query.all()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['id', 'nombre', 'turno', 'especialidad'])
    for b in barberos:
        writer.writerow([b.id, b.nombre, b.turno, b.especialidad])
    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = 'attachment; filename=barberos.csv'
    output.headers['Content-type'] = 'text/csv'
    return output

@app.route('/importar', methods=['POST'])
def importar():
    archivo = request.files['archivo']
    stream = io.StringIO(archivo.stream.read().decode('utf-8'))
    reader = csv.DictReader(stream)
    for row in reader:
        if not Barbero.query.get(int(row['id'])):
            db.session.add(Barbero(
                nombre=row['nombre'],
                turno=row['turno'],
                especialidad=row['especialidad']
            ))
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=False)
    
    
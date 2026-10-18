from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False)
    barbero = db.Column(db.String(100), nullable=False)
    servicio = db.Column(db.String(100))
    fecha = db.Column(db.String(20))
    hora = db.Column(db.String(10))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    citas = Cita.query.all()
    return render_template('index.html', citas=citas, modulo='Citas')

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        c = Cita(
            cliente=request.form['cliente'],
            barbero=request.form['barbero'],
            servicio=request.form['servicio'],
            fecha=request.form['fecha'],
            hora=request.form['hora']
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', cita=None, modulo='Citas')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    c = Cita.query.get_or_404(id)
    if request.method == 'POST':
        c.cliente = request.form['cliente']
        c.barbero = request.form['barbero']
        c.servicio = request.form['servicio']
        c.fecha = request.form['fecha']
        c.hora = request.form['hora']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', cita=c, modulo='Citas')

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Cita.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    citas = Cita.query.all()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['id', 'cliente', 'barbero', 'servicio', 'fecha', 'hora'])
    for c in citas:
        writer.writerow([c.id, c.cliente, c.barbero, c.servicio, c.fecha, c.hora])
    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = 'attachment; filename=citas.csv'
    output.headers['Content-type'] = 'text/csv'
    return output

@app.route('/importar', methods=['POST'])
def importar():
    archivo = request.files['archivo']
    stream = io.StringIO(archivo.stream.read().decode('utf-8'))
    reader = csv.DictReader(stream)
    for row in reader:
        if not Cita.query.get(int(row['id'])):
            db.session.add(Cita(
                cliente=row['cliente'],
                barbero=row['barbero'],
                servicio=row['servicio'],
                fecha=row['fecha'],
                hora=row['hora']
            ))
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
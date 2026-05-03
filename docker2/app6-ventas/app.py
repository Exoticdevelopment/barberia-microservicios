from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servicio = db.Column(db.String(100), nullable=False)
    monto = db.Column(db.Float)
    metodo_pago = db.Column(db.String(50))
    fecha = db.Column(db.String(20))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    ventas = Venta.query.all()
    total = sum(v.monto for v in ventas if v.monto)
    return render_template('index.html', ventas=ventas, total=total, modulo='Ventas')

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        v = Venta(
            servicio=request.form['servicio'],
            monto=float(request.form['monto']),
            metodo_pago=request.form['metodo_pago'],
            fecha=request.form['fecha']
        )
        db.session.add(v)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', venta=None, modulo='Ventas')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    v = Venta.query.get_or_404(id)
    if request.method == 'POST':
        v.servicio = request.form['servicio']
        v.monto = float(request.form['monto'])
        v.metodo_pago = request.form['metodo_pago']
        v.fecha = request.form['fecha']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', venta=v, modulo='Ventas')

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Venta.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    ventas = Venta.query.all()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['id', 'servicio', 'monto', 'metodo_pago', 'fecha'])
    for v in ventas:
        writer.writerow([v.id, v.servicio, v.monto, v.metodo_pago, v.fecha])
    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = 'attachment; filename=ventas.csv'
    output.headers['Content-type'] = 'text/csv'
    return output

@app.route('/importar', methods=['POST'])
def importar():
    archivo = request.files['archivo']
    stream = io.StringIO(archivo.stream.read().decode('utf-8'))
    reader = csv.DictReader(stream)
    for row in reader:
        if not Venta.query.get(int(row['id'])):
            db.session.add(Venta(
                servicio=row['servicio'],
                monto=float(row['monto']),
                metodo_pago=row['metodo_pago'],
                fecha=row['fecha']
            ))
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=False)
    
    
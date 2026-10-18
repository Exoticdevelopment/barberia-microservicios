from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.secret_key = 'barberia8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Gasto(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    concepto = db.Column(db.String(150), nullable=False)
    monto    = db.Column(db.Float)
    fecha    = db.Column(db.String(20))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    items = Gasto.query.all()
    return render_template('index.html', items=items)

@app.route('/nuevo', methods=['GET','POST'])
def nuevo():
    if request.method == 'POST':
        db.session.add(Gasto(
            concepto=request.form['concepto'],
            monto=float(request.form['monto']),
            fecha=request.form['fecha']
        ))
        db.session.commit()
        flash('Gasto agregado')
        return redirect(url_for('index'))
    return render_template('form.html', item=None)

@app.route('/editar/<int:id>', methods=['GET','POST'])
def editar(id):
    item = Gasto.query.get_or_404(id)
    if request.method == 'POST':
        item.concepto = request.form['concepto']
        item.monto = float(request.form['monto'])
        item.fecha = request.form['fecha']
        db.session.commit()
        flash('Actualizado')
        return redirect(url_for('index'))
    return render_template('form.html', item=item)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Gasto.query.get_or_404(id))
    db.session.commit()
    flash('Eliminado')
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','concepto','monto','fecha'])
    for r in Gasto.query.all():
        cw.writerow([r.id, r.concepto, r.monto, r.fecha])
    out = make_response(si.getvalue())
    out.headers['Content-Disposition'] = 'attachment; filename=gastos.csv'
    out.headers['Content-type'] = 'text/csv'
    return out

@app.route('/importar', methods=['POST'])
def importar():
    f = request.files.get('archivo')
    if f:
        reader = csv.DictReader(io.StringIO(f.read().decode('utf-8')))
        for row in reader:
            if not Gasto.query.get(int(row['id'])):
                db.session.add(Gasto(
                    id=int(row['id']),
                    concepto=row['concepto'],
                    monto=float(row['monto']),
                    fecha=row['fecha']
                ))
        db.session.commit()
        flash('Importado correctamente')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=False)
    
    
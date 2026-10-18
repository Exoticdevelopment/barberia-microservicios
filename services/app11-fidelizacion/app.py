from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.secret_key = 'barberia11'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Fidelizacion(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    cliente   = db.Column(db.String(100), nullable=False)
    puntos    = db.Column(db.Integer)
    descuento = db.Column(db.String(20))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    items = Fidelizacion.query.all()
    return render_template('index.html', items=items)

@app.route('/nuevo', methods=['GET','POST'])
def nuevo():
    if request.method == 'POST':
        db.session.add(Fidelizacion(
            cliente=request.form['cliente'],
            puntos=int(request.form['puntos']),
            descuento=request.form['descuento']
        ))
        db.session.commit()
        flash('Cliente agregado')
        return redirect(url_for('index'))
    return render_template('form.html', item=None)

@app.route('/editar/<int:id>', methods=['GET','POST'])
def editar(id):
    item = Fidelizacion.query.get_or_404(id)
    if request.method == 'POST':
        item.cliente = request.form['cliente']
        item.puntos = int(request.form['puntos'])
        item.descuento = request.form['descuento']
        db.session.commit()
        flash('Actualizado')
        return redirect(url_for('index'))
    return render_template('form.html', item=item)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Fidelizacion.query.get_or_404(id))
    db.session.commit()
    flash('Eliminado')
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','cliente','puntos','descuento'])
    for r in Fidelizacion.query.all():
        cw.writerow([r.id, r.cliente, r.puntos, r.descuento])
    out = make_response(si.getvalue())
    out.headers['Content-Disposition'] = 'attachment; filename=fidelizacion.csv'
    out.headers['Content-type'] = 'text/csv'
    return out

@app.route('/importar', methods=['POST'])
def importar():
    f = request.files.get('archivo')
    if f:
        reader = csv.DictReader(io.StringIO(f.read().decode('utf-8')))
        for row in reader:
            if not Fidelizacion.query.get(int(row['id'])):
                db.session.add(Fidelizacion(
                    id=int(row['id']),
                    cliente=row['cliente'],
                    puntos=int(row['puntos']),
                    descuento=row['descuento']
                ))
        db.session.commit()
        flash('Importado correctamente')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=False)
    
    
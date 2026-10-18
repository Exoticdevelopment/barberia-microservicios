from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.secret_key = 'barberia10'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Reporte(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    mes          = db.Column(db.String(20), nullable=False)
    total_ventas = db.Column(db.Float)
    total_gastos = db.Column(db.Float)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    items = Reporte.query.all()
    return render_template('index.html', items=items)

@app.route('/nuevo', methods=['GET','POST'])
def nuevo():
    if request.method == 'POST':
        db.session.add(Reporte(
            mes=request.form['mes'],
            total_ventas=float(request.form['total_ventas']),
            total_gastos=float(request.form['total_gastos'])
        ))
        db.session.commit()
        flash('Reporte agregado')
        return redirect(url_for('index'))
    return render_template('form.html', item=None)

@app.route('/editar/<int:id>', methods=['GET','POST'])
def editar(id):
    item = Reporte.query.get_or_404(id)
    if request.method == 'POST':
        item.mes = request.form['mes']
        item.total_ventas = float(request.form['total_ventas'])
        item.total_gastos = float(request.form['total_gastos'])
        db.session.commit()
        flash('Actualizado')
        return redirect(url_for('index'))
    return render_template('form.html', item=item)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Reporte.query.get_or_404(id))
    db.session.commit()
    flash('Eliminado')
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','mes','total_ventas','total_gastos'])
    for r in Reporte.query.all():
        cw.writerow([r.id, r.mes, r.total_ventas, r.total_gastos])
    out = make_response(si.getvalue())
    out.headers['Content-Disposition'] = 'attachment; filename=reportes.csv'
    out.headers['Content-type'] = 'text/csv'
    return out

@app.route('/importar', methods=['POST'])
def importar():
    f = request.files.get('archivo')
    if f:
        reader = csv.DictReader(io.StringIO(f.read().decode('utf-8')))
        for row in reader:
            if not Reporte.query.get(int(row['id'])):
                db.session.add(Reporte(
                    id=int(row['id']),
                    mes=row['mes'],
                    total_ventas=float(row['total_ventas']),
                    total_gastos=float(row['total_gastos'])
                ))
        db.session.commit()
        flash('Importado correctamente')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=False)
    
    
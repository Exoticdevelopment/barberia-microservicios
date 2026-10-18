from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.secret_key = 'barberia9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Turno(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    barbero     = db.Column(db.String(100), nullable=False)
    fecha       = db.Column(db.String(20))
    hora_inicio = db.Column(db.String(10))
    hora_fin    = db.Column(db.String(10))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    items = Turno.query.all()
    return render_template('index.html', items=items)

@app.route('/nuevo', methods=['GET','POST'])
def nuevo():
    if request.method == 'POST':
        db.session.add(Turno(
            barbero=request.form['barbero'],
            fecha=request.form['fecha'],
            hora_inicio=request.form['hora_inicio'],
            hora_fin=request.form['hora_fin']
        ))
        db.session.commit()
        flash('Turno agregado')
        return redirect(url_for('index'))
    return render_template('form.html', item=None)

@app.route('/editar/<int:id>', methods=['GET','POST'])
def editar(id):
    item = Turno.query.get_or_404(id)
    if request.method == 'POST':
        item.barbero = request.form['barbero']
        item.fecha = request.form['fecha']
        item.hora_inicio = request.form['hora_inicio']
        item.hora_fin = request.form['hora_fin']
        db.session.commit()
        flash('Actualizado')
        return redirect(url_for('index'))
    return render_template('form.html', item=item)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Turno.query.get_or_404(id))
    db.session.commit()
    flash('Eliminado')
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','barbero','fecha','hora_inicio','hora_fin'])
    for r in Turno.query.all():
        cw.writerow([r.id, r.barbero, r.fecha, r.hora_inicio, r.hora_fin])
    out = make_response(si.getvalue())
    out.headers['Content-Disposition'] = 'attachment; filename=turnos.csv'
    out.headers['Content-type'] = 'text/csv'
    return out

@app.route('/importar', methods=['POST'])
def importar():
    f = request.files.get('archivo')
    if f:
        reader = csv.DictReader(io.StringIO(f.read().decode('utf-8')))
        for row in reader:
            if not Turno.query.get(int(row['id'])):
                db.session.add(Turno(
                    id=int(row['id']),
                    barbero=row['barbero'],
                    fecha=row['fecha'],
                    hora_inicio=row['hora_inicio'],
                    hora_fin=row['hora_fin']
                ))
        db.session.commit()
        flash('Importado correctamente')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=False)
    
    
    
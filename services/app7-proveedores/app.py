from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.secret_key = 'barberia7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Proveedor(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(100), nullable=False)
    producto = db.Column(db.String(100))
    contacto = db.Column(db.String(100))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    items = Proveedor.query.all()
    return render_template('index.html', items=items)

@app.route('/nuevo', methods=['GET','POST'])
def nuevo():
    if request.method == 'POST':
        db.session.add(Proveedor(
            nombre=request.form['nombre'],
            producto=request.form['producto'],
            contacto=request.form['contacto']
        ))
        db.session.commit()
        flash('Proveedor agregado')
        return redirect(url_for('index'))
    return render_template('form.html', item=None)

@app.route('/editar/<int:id>', methods=['GET','POST'])
def editar(id):
    item = Proveedor.query.get_or_404(id)
    if request.method == 'POST':
        item.nombre = request.form['nombre']
        item.producto = request.form['producto']
        item.contacto = request.form['contacto']
        db.session.commit()
        flash('Actualizado')
        return redirect(url_for('index'))
    return render_template('form.html', item=item)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Proveedor.query.get_or_404(id))
    db.session.commit()
    flash('Eliminado')
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','nombre','producto','contacto'])
    for r in Proveedor.query.all():
        cw.writerow([r.id, r.nombre, r.producto, r.contacto])
    out = make_response(si.getvalue())
    out.headers['Content-Disposition'] = 'attachment; filename=proveedores.csv'
    out.headers['Content-type'] = 'text/csv'
    return out

@app.route('/importar', methods=['POST'])
def importar():
    f = request.files.get('archivo')
    if f:
        reader = csv.DictReader(io.StringIO(f.read().decode('utf-8')))
        for row in reader:
            if not Proveedor.query.get(int(row['id'])):
                db.session.add(Proveedor(
                    id=int(row['id']),
                    nombre=row['nombre'],
                    producto=row['producto'],
                    contacto=row['contacto']
                ))
        db.session.commit()
        flash('Importado correctamente')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=False)
    
    
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import csv, io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer)
    precio = db.Column(db.Float)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    productos = Producto.query.all()
    return render_template('index.html', productos=productos, modulo='Productos')

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        p = Producto(
            nombre=request.form['nombre'],
            stock=int(request.form['stock']),
            precio=float(request.form['precio'])
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', producto=None, modulo='Productos')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    p = Producto.query.get_or_404(id)
    if request.method == 'POST':
        p.nombre = request.form['nombre']
        p.stock = int(request.form['stock'])
        p.precio = float(request.form['precio'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html', producto=p, modulo='Productos')

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.session.delete(Producto.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    productos = Producto.query.all()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['id', 'nombre', 'stock', 'precio'])
    for p in productos:
        writer.writerow([p.id, p.nombre, p.stock, p.precio])
    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = 'attachment; filename=productos.csv'
    output.headers['Content-type'] = 'text/csv'
    return output

@app.route('/importar', methods=['POST'])
def importar():
    archivo = request.files['archivo']
    stream = io.StringIO(archivo.stream.read().decode('utf-8'))
    reader = csv.DictReader(stream)
    for row in reader:
        if not Producto.query.get(int(row['id'])):
            db.session.add(Producto(
                nombre=row['nombre'],
                stock=int(row['stock']),
                precio=float(row['precio'])
            ))
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)
    
    
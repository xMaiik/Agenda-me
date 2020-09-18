from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL,MySQLdb
import bcrypt

#Configuracion con la base de datos
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_contraseña'] = ''
app.config['MYSQL_DB'] = 'agendame'
mysql = MySQL(app)

valor = True
#Ruta de registro
@app.route('/agregar', methods=["GET", "POST"])
def registro():
    if request.method == 'GET':
        return render_template("registro.html")
    else:
        usuario = request.form['usuario']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        contraseña = request.form['contraseña'].encode('utf-8')
        contraseña2 = request.form['contraseña2'].encode('utf-8')

        # Validacion de contraseñas
        if contraseña == contraseña2:

            #Encriptacion de contraseña
            hash_contraseña = bcrypt.hashpw(contraseña, bcrypt.gensalt())

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (usuario, nombre, apellidos, contraseña) VALUES (%s,%s,%s,%s)",(usuario,nombre,apellidos,hash_contraseña,))
            mysql.connection.commit()
            session['usuario'] = request.form['usuario']
            session['nombre'] = request.form['nombre']
            return redirect(url_for('iniciar'))
        else:
            flash('Las contraselas no coinciden')
            return redirect(url_for('agregar'))


# Ruta de registro
@app.route('/iniciar',methods=["GET","POST"])
def iniciar():

    # busca si el usuario esta en la bd
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM usuarios WHERE usuario=%s",(usuario,))
        user = curl.fetchone()
        curl.close()


        if user == None:
            flash('error')
            return redirect(url_for('iniciar'))
        
        # busca si la contraseña le pertenece al usuario

        if len(user) > 0:
            if bcrypt.hashpw(contraseña, user["contraseña"].encode('utf-8')) == user["contraseña"].encode('utf-8'):
                session['usuario'] = user['usuario']
                session['nombre'] = user['nombre']
                global valor
                valor= user.get('usuario')
                print(valor)
                return redirect(url_for('Index'))
                

            else:
                flash('El usuario o la contraseña')
                return redirect(url_for('iniciar'))
        
    else:
        return render_template("inicio.html")

#Ruta de bandeja
@app.route('/bandeja')
def Index():
    global valor
    curs = mysql.connection.cursor()
    curs.execute('SELECT * FROM eventos')
    datos = curs.fetchall()
    print (datos)

    if request.method == 'POST':
        buscar = request.form['buscar']
        cur = mysql.connection.cursor()
        print (buscar)
        cur.execute('SET @var1='buscar'; SELECT * FROM eventos WHERE titulo, descripcion, dia, fecha, hora = @var1')
        datos = curs.fetchall()
        print (datos)
        mysql.connection.commit()

    return render_template('bandeja.html', datos = datos, lis = valor)

@app.route('/agregar_eventos', methods = ['POST'])
def agregar_eventos():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        dia = request.form['dia']
        fecha = request.form['fecha']
        hora = request.form['hora']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO eventos(titulo, descripcion, dia, fecha, hora) VALUES (%s, %s, %s, %s, %s)',
        (titulo, descripcion, dia, fecha, hora))
        mysql.connection.commit()

        return redirect(url_for('Index'))
    
@app.route('/eliminar/<string:id>')
def eliminar(id):
    curs = mysql.connection.cursor()
    curs.execute('DELETE FROM eventos WHERE id = {0}'.format(id))
    mysql.connection.commit()
    return redirect(url_for('Index'))

#Editar
@app.route('/editar/<id>', methods = ['POST', 'GET'])
def get_eventos(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM eventos WHERE id = %s', (id))
    dato = cur.fetchall()
    print(dato[0])
    return render_template('actualizar.html', evento = dato[0])

#Actualizar
@app.route('/actualizar/<id>', methods=['POST'])
def actualizar(id):
    if request.method == 'POST':
        titulo= request.form['titulo']
        descripcion = request.form['descripcion']
        dia = request.form['dia']
        fecha = request.form['fecha']
        hora = request.form['hora']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE eventos
            SET titulo = %s,
                descripcion = %s,
                dia = %s,
                fecha = %s,
                hora = %s
            WHERE id = %s
        """, (titulo, descripcion, dia, fecha, hora, id))
        mysql.connection.commit()
        return redirect(url_for('Index'))



if __name__ == '__main__':
    app.secret_key = "^A%DJAJU^JJ123"
    app.run(debug=True)
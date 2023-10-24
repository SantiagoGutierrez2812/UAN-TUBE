# Importar las bibliotecas necesarias
from flask import Flask
from flask import render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config["MYSQL_HOST"] = "localhost" # La dirección de la base de datos
app.config["MYSQL_USER"] = "root" # El nombre de usuario de la base de datos
app.config["MYSQL_PASSWORD"] = "" # La contraseña de la base de datos
app.config["MYSQL_DB"] = "proyectodb" # El nombre de la base de datos
app.config["MYSQL_CURSORCLASS"] = "DictCursor" # Usar un cursor que devuelve resultados como diccionarios
mysql = MySQL(app)

# Ruta para la página de inicio
@app.route("/")
def home():
    return render_template("index.html")

# Ruta para la página de dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# Ruta para la página de inicio de sesión
@app.route("/login", methods = ["GET","POST"])
def login():
    mensaje = None  # Variable para almacenar mensajes de error, por defecto no hay mensaje de error

    if 'mensaje' in session:
        mensaje = session['mensaje']
        session.pop('mensaje', None)  # Borrar el mensaje de la sesión

    if request.method == 'POST':
        # Si el usuario envía un formulario de inicio de sesión por POST
        email = request.form['email']
        password = request.form['password']

        # Conectarse a la base de datos y verificar las credenciales del usuario
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user is not None:
            if password == user["password"]:
                 # Si las credenciales son válidas, inicia sesión y redirige al panel de control
                session['email'] = user['email']
                return redirect(url_for("dashboard"))
            else:
                session['mensaje'] = "Correo o contraseña no válida"
                return redirect(url_for('login'))
        else:
            session['mensaje'] = "No existe el usuario"
            return redirect(url_for('login'))
    else:
        # Si la solicitud es GET, muestra la página de inicio de sesión
        return render_template("login.html", mensaje=mensaje)

# Ruta para la página de registro
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        # Si el usuario envía un formulario de registro por POST
        usuario = request.form['usuario']
        email = request.form['email']

        # Verificar si el nombre de usuario ya existe
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE nombreUsuario = %s", (usuario,))
        user_by_username = cur.fetchone()
        cur.close()

        # Verificar si el correo ya está registrado
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        user_by_email = cur.fetchone()
        cur.close()

        if user_by_username:
            session['mensaje'] = "Nombre de usuario ya registrado"
            return redirect(url_for('registro'))
        elif user_by_email:
            session['mensaje'] = "Correo electrónico ya registrado"
            return redirect(url_for('registro'))
        else:
            # El nombre de usuario y el correo no existen, puedes realizar el registro
            password = request.form['password']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            fecha_nacimiento = request.form['fecha_nacimiento']
            genero = request.form['genero']
            pais = request.form['pais']

            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO usuario (nombreUsuario, password, nombre, apellido, fechaNacimiento, genero, email, pais) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (usuario, password, nombre, apellido, fecha_nacimiento, genero, email, pais)
            )

            mysql.connection.commit()

            return redirect(url_for("login"))
    else:
        # Si la solicitud es GET, muestra la página de registro
        return render_template("registro.html")
    
if __name__ == "__main__":
    app.secret_key="santiago" # Clave secreta para manejar sesiones
    app.run(debug=True)
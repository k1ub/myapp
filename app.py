from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re
import hashlib

app = Flask(__name__)
app.secret_key = 'mysecretkey'  # Asegúrate de cambiar esta clave en producción

# Conexión a la base de datos SQLite
def get_db_connection():
    conn = sqlite3.connect('database/users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Función para convertir números a romanos
def to_roman(num):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
        ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
        ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

# Ruta para la página principal
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('convert'))
    return render_template('index.html')

# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password(password, user['password']):
            session['username'] = username
            return redirect(url_for('convert'))
        else:
            error_message = "Credenciales inválidas"
    return render_template('login.html', error_message=error_message)

# Ruta para registrarse
@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(password) < 8 or not re.search(r"\d", password) or not re.search(r"[A-Za-z]", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            error_message = "La contraseña debe contener mínimo 8 caracteres, al menos un número, una mayúscula y un carácter especial."
        else:
            conn = get_db_connection()
            existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if existing_user:
                error_message = "El usuario ya existe."
            else:
                hashed_password = hash_password(password)
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
    return render_template('register.html', error_message=error_message)

# Ruta para la conversión de números romanos
@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        number = int(request.form['number'])
        roman = to_roman(number)
        return render_template('convert.html', roman=roman)
    return render_template('convert.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Funciones para cifrado de contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed_password):
    return hash_password(password) == hashed_password

if __name__ == '__main__':
    app.run(debug=True)

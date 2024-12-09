import re  # Para validação com expressões regulares
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from urllib.parse import urlparse, urljoin
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


app = Flask(__name__)
app.secret_key = 'seu_segredo_seguro_aqui'  # Necessário para usar flash messages


# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"  # Redireciona para a página de login se não autenticado
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "error"


# Configurar Flask-WTF
csrf = CSRFProtect(app)


# Configurar Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]  # Limites globais
)


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


# Carregar usuário a partir do ID
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], password=user[2])
    return None


# Limitar tentativas de login
@app.route("/", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # Limitar a 10 tentativas por minuto
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]


        app.logger.debug(f"Attempting login for username: {username}")


        # Verificar se o usuário existe no banco de dados
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()


        if user and check_password_hash(user[2], password):
            app.logger.debug(f"Login successful for username: {username}")
            user_obj = User(id=user[0], username=user[1], password=user[2])
            login_user(user_obj)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("homepage"))
        else:
            app.logger.debug(f"Login failed for username: {username}")
            flash("Usuário ou senha inválidos. Tente novamente.", "error")


    app.logger.debug("Rendering login.html")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta com sucesso.", "success")
    return redirect(url_for("login"))


# Página pós-login
@app.route("/homepage")
@login_required
def homepage():
    return render_template("homepage.html", username=current_user.username)


# Rota para registrar novos usuários
# Rota para registro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()


        # Regras de validação
        if not username:
            flash("O nome de usuário não pode estar vazio.", "error")
            return redirect(url_for("register"))
       
        if len(username) < 3:
            flash("O nome de usuário deve ter pelo menos 3 caracteres.", "error")
            return redirect(url_for("register"))


        if len(password) < 8:
            flash("A senha deve ter pelo menos 8 caracteres.", "error")
            return redirect(url_for("register"))
       
        # Verificar se o nome de usuário já existe
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("O nome de usuário já está em uso. Escolha outro.", "error")
            conn.close()
            return redirect(url_for("register"))


        # Gerar hash da senha antes de salvar
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')


        # Inserir novo usuário com a senha hashed
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()


        # Redireciona para a mesma página com um indicador de sucesso
        return redirect(url_for("register", success="true"))


    # Verifica se o registro foi bem-sucedido
    success = request.args.get("success")
    return render_template("register.html", success=success)


if __name__ == "__main__":
    app.run(debug=True)


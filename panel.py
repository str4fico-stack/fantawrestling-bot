from flask_login import current_user
from telegram_utils import send_telegram_message

import secrets

from flask_mail import (
    Mail,
    Message
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from datetime import datetime

from flask import (
    Flask,
    flash,
    render_template,
    request,
    redirect,
    url_for
    
)

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user
)

import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config[
    "MAIL_SERVER"
] = "smtp.gmail.com"

app.config[
    "MAIL_PORT"
] = 587

app.config[
    "MAIL_USE_TLS"
] = True

app.config[
    "MAIL_USERNAME"
] = "str4fico@gmail.com"

app.config[
    "MAIL_PASSWORD"
] = "rvgi pcdr lawb ojqt"

mail = Mail(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.secret_key = "FANTAWRESTLING_SUPER_SECRET_2026"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user_login"
login_manager.login_message = "🔒 Effettua il login"



class Card(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    apertura = db.Column(
        db.String(100)
    )

    chiusura = db.Column(
        db.String(100)
    )

    match = db.relationship(
        "Match",
        backref="card",
        lazy=True,
        cascade="all, delete"
    )

class User(UserMixin, db.Model):

    is_admin = db.Column(
    db.Boolean,
    default=False
    )

    email = db.Column(
        db.String(200),
        unique=True,
        nullable=False
    )

    reset_token = db.Column(
        db.String(200),
        nullable=True
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    punti = db.Column(
        db.Integer,
        default=0
    )
    pronostici = db.relationship(
    "Pronostico",
    backref="user",
    lazy=True
)
class Match(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    card_id = db.Column(
        db.Integer,
        db.ForeignKey("card.id"),
        nullable=False
    )

    risultato1 = db.Column(
        db.String(200)
    )
 
    risultato2 = db.Column(
            db.String(200)
    )

    nome = db.Column(
        db.String(100)
    )

    domanda1 = db.Column(
        db.String(200)
    )

    risposte1 = db.Column(
        db.Text
    )

    domanda2 = db.Column(
        db.String(200)
    )

    risposte2 = db.Column(
        db.Text
    )    
    pronostici = db.relationship(
    "Pronostico",
    backref="match",
    lazy=True
)
    
class Pronostico(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    match_id = db.Column(
        db.Integer,
        db.ForeignKey("match.id")
    )

    risposta1 = db.Column(
        db.String(200)
    )

    risposta2 = db.Column(
        db.String(200)
    )

    punti = db.Column(
        db.Integer,
        default=0
    )


@login_manager.user_loader
def load_user(user_id):

    try:

        return User.query.get(int(user_id))

    except:

        return None
from functools import wraps

def admin_required(f):

    @wraps(f)

    def decorated_function(
         *args,
        **kwargs
   ):

        if not current_user.is_admin:

            return "Accesso negato"

        return f(*args, **kwargs)

    return decorated_function    

#def load_cards():

#    with open("cards.json", "r", encoding="utf-8") as file:

#        return json.load(file)

@app.route(
    "/reset_password/<token>",
    methods=["GET", "POST"]
)
def reset_password(token):

    user = User.query.filter_by(
        reset_token=token
    ).first()

    if not user:

        return "Token non valido"

    if request.method == "POST":

        nuova_password = request.form[
            "password"
        ]

        user.password = generate_password_hash(
            nuova_password
        )

        user.reset_token = None

        db.session.commit()
        send_telegram_message(
             f"🔥 Nuova card disponibile!\n\n🏆 {nuova_card.nome}\n\n⏰ Chiusura: {nuova_card.chiusura}"
        )

        flash(
            "✅ Password aggiornata"
        )

        return redirect(
            url_for("user_login")
        )

    return render_template(
        "reset_password.html"
    )
    

@app.route("/admin/users")
@login_required
@admin_required
def admin_users():

    users = User.query.all()

    return render_template(
        "admin_users.html",
        users=users
    )

@app.route("/make_admin/<user_id>")
@login_required
@admin_required
def make_admin(user_id):

    user = User.query.get(user_id)

    user.is_admin = True

    db.session.commit()

    flash(
        "👑 Utente promosso admin"
    )

    return redirect(
        url_for("admin_users")
    )

@app.route(
    "/modifica_punti/<user_id>",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def modifica_punti(user_id):

    user = User.query.get(user_id)

    if request.method == "POST":

        user.punti = int(
            request.form["punti"]
        )

        db.session.commit()

        flash(
            "🏆 Punti aggiornati"
        )

        return redirect(
            url_for("admin_users")
        )

    return render_template(
        "modifica_punti.html",
        user=user
    )

@app.route("/profilo")
@login_required
def profilo():

    pronostici = Pronostico.query.filter_by(
        user_id=current_user.id
    ).all()

    totale_pronostici = len(pronostici)

    punti_totali = current_user.punti

    punti_massimi = totale_pronostici * 2

    accuratezza = 0

    if punti_massimi > 0:

        accuratezza = round(
            (punti_totali / punti_massimi) * 100,
            1
        )

    return render_template(

        "profilo.html",

        pronostici=pronostici,

        totale_pronostici=totale_pronostici,

        punti_totali=punti_totali,

        accuratezza=accuratezza
    )

@app.route(
    "/forgot_password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user:

            token = secrets.token_hex(32)

            user.reset_token = token

            db.session.commit()

            link = url_for(
                "reset_password",
                token=token,
                _external=True
            )

            msg = Message(
                "Reset Password Fantawrestling",
                sender=app.config[
                    "MAIL_USERNAME"
                ],
                recipients=[email]
            )

            msg.body = f"""
Recupero Password Fantawrestling

Apri questo link:

{link}
"""

            mail.send(msg)

            flash(
                "📧 Email inviata"
            )

            return redirect(
                url_for("user_login")
            )

        flash("❌ Email non trovata")

    return render_template(
        "forgot_password.html"
    )

@app.route("/user_logout")
@login_required
def user_logout():

    logout_user()

    return redirect(
        url_for("user_login")
    )

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
    url_for("user_login")
)

@app.route("/dashboard")
@login_required
@admin_required
def home():
    print(current_user.username)
    print(current_user.is_admin)

    cards_db = Card.query.all()

    cards = {}

    for card in cards_db:

        cards[str(card.id)] = {

            "nome": card.nome,
            "apertura": card.apertura,
            "chiusura": card.chiusura,

            "match": [

                {
                    "id": m.id,
                    "nome": m.nome
                }

                for m in card.match
        ]
    }

    classifica_ordinata = User.query.order_by(
    User.punti.desc()
    ).all()

    totale_cards = len(cards)

    totale_match = sum(
        len(card["match"])
        for card in cards.values()
    )

    totale_utenti = len(classifica_ordinata)

    if len(classifica_ordinata) > 0:

        leader = classifica_ordinata[0].username
        punti_leader = classifica_ordinata[0].punti

    else:

        leader = "Nessuno"
        punti_leader = 0

    labels = []
    punti = []

    for user in classifica_ordinata:

        labels.append(user.username)
        punti.append(user.punti)

    return render_template(
        "dashboard.html",
        cards=cards,
        classifica=classifica_ordinata,
        totale_cards=totale_cards,
        totale_match=totale_match,
        totale_utenti=totale_utenti,
        leader=leader,
        punti_leader=punti_leader,
        labels=labels,
        punti=punti
    )

@app.route("/elimina_card/<card_id>")
@login_required
@admin_required
def elimina_card(card_id):

    card = Card.query.get(card_id)

    if card:

        db.session.delete(card)

        db.session.commit()

    return redirect(url_for("home"))

@app.route("/modifica_card/<card_id>", methods=["GET", "POST"])
@login_required
@admin_required
def modifica_card(card_id):

    card = Card.query.get(card_id)

    if request.method == "POST":

        card.nome = request.form["nome"]

        card.apertura = request.form["apertura"]

        card.chiusura = request.form["chiusura"]

        db.session.commit()

        return redirect(url_for("home"))

    return render_template(
        "modifica_card.html",
        card=card
    )

@app.route("/crea_card", methods=["GET", "POST"])
@login_required
@admin_required
def crea_card():

    if request.method == "POST":

        nome = request.form["nome"]
        apertura = request.form["apertura"]
        chiusura = request.form["chiusura"]

        nuova_card = Card(

            nome=request.form["nome"],
            apertura=request.form["apertura"],
            chiusura=request.form["chiusura"]
        )

        db.session.add(nuova_card)

        db.session.commit()
        send_telegram_message(
            f"🔥 Nuova card disponibile!\n\n🏆 {nuova_card.nome}\n\n⏰ Chiusura: {nuova_card.chiusura}"
        )

        return redirect(url_for("home"))

    return render_template("crea_card.html")


@app.route("/aggiungi_match/<card_id>", methods=["GET", "POST"])
@login_required
@admin_required
def aggiungi_match(card_id):

    card = Card.query.get(card_id)

    if request.method == "POST":

        nuovo_match = Match(

            nome=request.form["nome"],
            card_id=card_id
        )

        db.session.add(nuovo_match)

        db.session.commit()
        send_telegram_message(
        f"🎮 Nuovo match aggiunto!\n\n📌 {nuovo_match.nome}"
        )

        return redirect(url_for("home"))

    return render_template(
        "aggiungi_match.html",
        card=card
    )

@app.route("/elimina_match/<card_id>/<match_id>")
@login_required
@admin_required
def elimina_match(card_id, match_id):

    match = Match.query.get(match_id)

    if match:

        db.session.delete(match)

        db.session.commit()

    return redirect(url_for("home"))

@app.route("/modifica_match/<card_id>/<match_id>", methods=["GET", "POST"])
@login_required
@admin_required
def modifica_match(card_id, match_id):

    match = Match.query.get(match_id)

    if request.method == "POST":

        match.nome = request.form["nome"]

        db.session.commit()

        return redirect(url_for("home"))

    return render_template(
        "modifica_match.html",
        match=match
    )

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]

        password = request.form["password"]
        password_hash = generate_password_hash(password)

        existing_user = User.query.filter_by(
            username=username
        ).first()

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            return "Email già registrata"

        if existing_user:

            return "Utente già esistente"

        nuovo_utente = User(

            username=username,
            email=email,
            password=password_hash

        )

        db.session.add(nuovo_utente)

        db.session.commit()

        return redirect(
            url_for("user_login")
)

    return render_template("register.html")

@app.route("/user_login", methods=["GET", "POST"])
def user_login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

             login_user(user)

             if user.is_admin:
                return redirect(
                    url_for("home"),
                )
             return redirect(
                url_for("dashboard_user"),
            )

        return "Credenziali non valide"

    return render_template("user_login.html")

@app.route("/dashboard_user")
@login_required
def dashboard_user():

    user = current_user

    cards = Card.query.all()
    
    classifica = User.query.order_by(
    User.punti.desc()
    ).all()
    
    return render_template(
        "dashboard_user.html",
        user=user,
        cards=cards,
        classifica=classifica
    )

@app.route("/")
def index():

    cards = Card.query.all()

    classifica = User.query.order_by(
        User.punti.desc()
    ).limit(10).all()

    return render_template(

        "index.html",

        cards=cards,

        classifica=classifica
    )

@app.route("/pronostici/<card_id>", methods=["GET", "POST"])
@login_required
def pronostici(card_id):

    user = current_user

    card = Card.query.get(card_id)
    
    chiusura = datetime.strptime(
       card.chiusura,
       "%d/%m/%Y %H:%M"
   )

    if datetime.now() > chiusura:

       return "Pronostici chiusi"

    if request.method == "POST":

        for match in card.match:

            risposta1 = request.form.get(
                f"risposta1_{match.id}"
            )

            risposta2 = request.form.get(
                f"risposta2_{match.id}"
            )
            
            pronostico_esistente = Pronostico.query.filter_by(

                user_id=user.id,

                match_id=match.id

            ).first()

            if pronostico_esistente:
                flash("⚠️ Pronostico già presente per questo match.")

                continue
            nuovo_pronostico = Pronostico(

                user_id=user.id,

                match_id=match.id,

                risposta1=risposta1,

                risposta2=risposta2
            )

            db.session.add(nuovo_pronostico)

        db.session.commit()

        flash("✅ Pronostici salvati!")
        
        return redirect(
            url_for("dashboard_user")
        )
    
    return render_template(
        "pronostici.html",
        user=user,
        card=card
    )

@app.route("/risultati_match/<match_id>", methods=["GET", "POST"])
@login_required
@admin_required
def risultati_match(match_id):

    match = Match.query.get(match_id)

    if request.method == "POST":

        match.risultato1 = request.form["risultato1"]

        match.risultato2 = request.form["risultato2"]
        
        pronostici = Pronostico.query.filter_by(
    
        match_id=match.id
    
        ).all()

        for pronostico in pronostici:

            punti = 0

            if pronostico.risposta1 == match.risultato1:

                punti += 1

            if pronostico.risposta2 == match.risultato2:

                punti += 1

            pronostico.punti = punti

            user = User.query.get(
                pronostico.user_id
            )

            user.punti -= pronostico.punti
            user.punti += punti
        db.session.commit()
        send_telegram_message(
             f"✅ Risultati aggiornati per il match:\n\n🎯 {match.nome}"
        )

        return redirect(url_for("home"))

    return render_template(
        "risultati_match.html",
        match=match
    )

with app.app_context():

    db.create_all()

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
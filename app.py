from flask import Flask, render_template, url_for, request, session, redirect, flash, current_app
from dataclasses import asdict
from forms import BillForm, RegisterForm, LoginForm
from models import Bill, User
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256
from datetime import datetime
import uuid
import functools
import os

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFz"
    )
    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
    app.db = MongoClient(app.config["MONGODB_URI"]).get_default_database()

    def login_required(route):
        @functools.wraps(route)
        def route_wrapper(*args, **kwargs):
            if session.get("email") is None:
                return redirect(url_for(".login"))
            
            return route(*args, **kwargs)
        
        return route_wrapper

    @app.route("/")
    @login_required
    def index():
        user_data = current_app.db.users.find_one({"email": session["email"]})
        user = User(**user_data)
        bills_data = current_app.db.bills.find({"_id": {"$in": user.bills}}).sort([("insertDate", -1)]).limit(3)
        bill = [Bill(**bill) for bill in bills_data]
        return render_template('index.html', title="Coincare - Início", bill_data=bill)
    
    @app.route("/contas", methods=["GET", "POST"])
    @login_required
    def bills_to_pay(confirm_delete=None, confirm_edit=None, bill=None):
        user_data = current_app.db.users.find_one({"email": session["email"]})
        user = User(**user_data)
        if not bill:
            bills_data = current_app.db.bills.find({"_id": {"$in": user.bills}})
            bill = [Bill(**bill) for bill in bills_data]
        
        return render_template('bills_to_pay.html', title="Coincare - Contas a Pagar", bill_data=bill, confirm_delete=confirm_delete, confirm_edit=confirm_edit)
    
    @app.route("/conta/<string:_id>", methods=["GET", "POST"])
    def delete_bill(_id: str):
        if request.method == "POST":
            operacao = request.form.get('operacao')
            if operacao == "excluir":
                current_app.db.bills.delete_one({'_id': _id})

            return redirect(url_for(".bills_to_pay"))

        return bills_to_pay(confirm_delete=True)
    
    @app.route("/edit/<string:_id>", methods=["GET", "POST"])
    def edit_bill(_id: str):
        operacao = request.form.get('operacao')
        bills_data = current_app.db.bills.find({"_id": _id})
        bill = [Bill(**bill) for bill in bills_data]
        if request.method == "POST":
            if operacao == "Confirmar":
                if request.form.get("billName"):
                    current_app.db.bills.update_one({"_id": _id},
                    {"$set": {"billName": request.form.get("billName")}})
                if request.form.get("billValue"):
                    current_app.db.bills.update_one({"_id": _id},
                    {"$set": {"billValue": request.form.get("billValue")}})
                if request.form.get("expireDate"):
                    expire_date = str(request.form.get("expireDate"))
                    expire_formatted = datetime.strptime(expire_date, '%Y-%m-%d').strftime("%d-%m-%Y")
                    current_app.db.bills.update_one({"_id": _id},
                    {"$set": {"expireDate": expire_formatted}})
                
                current_app.db.bills.update_one({"_id": _id},
                {"$set": {"description": request.form.get("description")}})

            return redirect(url_for(".bills_to_pay"))
        
        return bills_to_pay(confirm_edit=True, bill=bill)

    @app.get("/toggle-theme")
    def toggle_theme():
        current_theme = session.get("theme")
        if current_theme == "dark":
            session["theme"] = "light"
        else:
            session["theme"] = "dark"

        return redirect(request.args.get("current_page"))
    
    @app.route("/registrar", methods=["GET", "POST"])
    def register():
        if session.get("email"):
            return redirect(url_for(".index"))
        form = RegisterForm()

        if form.validate_on_submit():
            if current_app.db.users.find_one({"email": form.email.data}):
                flash("Este email já está em uso", category="danger")
                return redirect(url_for(".register"))
            else:
                user = User(
                    _id=uuid.uuid4().hex,
                    email=form.email.data,
                    password=pbkdf2_sha256.hash(form.password.data),
                )

                current_app.db.users.insert_one(asdict(user))

                flash("Usuário registrado com sucesso!!")
                
                return redirect(url_for(".login"))

        return render_template("register.html", title="CoinCare - Registrar", form=form)
    
    @app.route("/logout")
    def logout():
        current_theme = session.get("theme")
        session["theme"] = current_theme
        del session["user_id"]
        del session["email"]

        return redirect(url_for(".login"))

    @app.route("/add", methods=["GET", "POST"])
    @login_required
    def add_bill():
        form = BillForm()

        if form.validate_on_submit():
            expire_date = str(form.expire_date.data)
            expire_formatted = datetime.strptime(expire_date, '%Y-%m-%d').strftime("%d-%m-%Y")
            insertion_date = datetime.today().strftime("%d-%m-%Y")
            description = "" if not form.description.data else form.description.data
            bill = Bill(
                _id=uuid.uuid4().hex,
                billName=form.bill_name.data,
                billValue=form.bill_value.data,
                expireDate=expire_formatted,
                description=description,
                insertDate=insertion_date
            )
            current_app.db.bills.insert_one(asdict(bill))
            current_app.db.users.update_one(
                {"_id": session["user_id"]}, {"$push": {"bills": bill._id}}
            )

            return redirect(url_for(".index"))

        return render_template("new_bill.html", title="CoinCare - Adicionar Conta", form=form)
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if session.get("email"):
            return redirect(url_for(".index"))
        
        form = LoginForm()

        if form.validate_on_submit():
            user_data = current_app.db.users.find_one({"email": form.email.data})
            if not user_data:
                flash("Dados de login incorretos", category="danger")
                return redirect(url_for(".login"))
            user = User(**user_data)

            if user and pbkdf2_sha256.verify(form.password.data, user.password):
                session["user_id"] = user._id
                session["email"] = user.email

                return redirect(url_for(".index"))
            print("chegou aqui")
            flash("Dados de login incorretos", category="danger")
        return render_template("login.html", title="CoinCare - Login", form=form)
    
    return app

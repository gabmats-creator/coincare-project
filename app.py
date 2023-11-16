from flask import (
    Flask,
    render_template,
    url_for,
    request,
    session,
    redirect,
    flash,
    current_app,
)
from dataclasses import asdict
from forms import BillForm, RegisterForm, LoginForm
from models import Bill, User
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256
from datetime import datetime
import uuid
import functools
import os
import locale


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

    def get_month_name(date):
        fields = date.split("/")
        month = fields[1]

        months = {
            "01": "Janeiro",
            "02": "Fevereiro",
            "03": "Março",
            "04": "Abril",
            "05": "Maio",
            "06": "Junho",
            "07": "Julho",
            "08": "Agosto",
            "09": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro",
        }

        return months[month]

    def formata_reais(valor):
        valor_formatado = f"R$ {valor:.2f}"

        return valor_formatado

    def calc_free_value(user):
        cond1 = {"mensal": True}
        cond2 = {
            "insertMonth": get_month_name(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        }
        mensal_bills_data_value = current_app.db.bills.find(
            {"_id": {"$in": user.bills}, "$or": [cond1, cond2]}
        )

        custo_contas = 0
        for conta in mensal_bills_data_value:
            custo_contas += float(conta["billValue"])
        income = user.income
        free_value = income - custo_contas
        negative = True if free_value < 0 else None
        if free_value < 0:
            free_value *= -1
        return formata_reais(free_value), negative

    @app.route("/")
    def homepage():
        current_theme = session.get("theme")
        session["theme"] = current_theme
        if session.get("user_id"):
            del session["user_id"]
        if session.get("email"):
            del session["email"]

        return render_template("home.html")

    @app.route("/home")
    @login_required
    def index():
        user_data = current_app.db.users.find_one({"email": session["email"]})
        user = User(**user_data)
        cond1 = {"mensal": True}
        cond2 = {
            "insertMonth": get_month_name(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        }
        bills_data = (
            current_app.db.bills.find({"_id": {"$in": user.bills}, "$or": [cond1, cond2]})
            .sort("insertDate", -1)
            .limit(3)
        )
        income_value = formata_reais(user.income)
        free_value, negative = calc_free_value(user)
        bill = [Bill(**bill) for bill in bills_data]
        for conta in bill:
            conta.billValue = formata_reais(conta.billValue)
        atual_month = get_month_name(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        return render_template(
            "index.html",
            title="Coincare - Início",
            bill_data=bill,
            user_name=user.name,
            user_income=income_value,
            free_value=free_value,
            negative=negative,
            mes=atual_month,
        )

    @app.route("/contas", methods=["GET", "POST"])
    @login_required
    def bills_to_pay(confirm_delete=None, confirm_edit=None, bill=None):
        user_data = current_app.db.users.find_one({"email": session["email"]})
        user = User(**user_data)
        atual_month = get_month_name(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        if not bill:
            cond1 = {"mensal": True}
            cond2 = {
                "insertMonth": get_month_name(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            }
            bills_data = current_app.db.bills.find({"_id": {"$in": user.bills},  "$or": [cond1, cond2]})
            bill = [Bill(**bill) for bill in bills_data]
            for conta in bill:
                conta.billValue = formata_reais(conta.billValue)

        return render_template(
            "bills_to_pay.html",
            title="Coincare - Contas a Pagar",
            bill_data=bill,
            confirm_delete=confirm_delete,
            confirm_edit=confirm_edit,
            mes=atual_month,
        )

    @app.route("/add", methods=["GET", "POST"])
    @login_required
    def add_bill():
        form = BillForm()

        if form.validate_on_submit():
            expire_date = str(form.expire_date.data)
            expire_formatted = datetime.strptime(expire_date, "%Y-%m-%d").strftime(
                "%d-%m-%Y"
            )
            insertion_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            insertion_month = get_month_name(insertion_date)
            description = "" if not form.description.data else form.description.data
            bill = Bill(
                _id=uuid.uuid4().hex,
                billName=form.bill_name.data,
                billValue=form.bill_value.data,
                expireDate=expire_formatted,
                description=description,
                insertDate=insertion_date,
                insertMonth=insertion_month,
                mensal=True if form.frequence.data == "mensal" else False,
            )
            current_app.db.bills.insert_one(asdict(bill))
            current_app.db.users.update_one(
                {"_id": session["user_id"]}, {"$push": {"bills": bill._id}}
            )

            return redirect(url_for(".index"))

        return render_template(
            "new_bill.html", title="CoinCare - Adicionar Conta", form=form
        )

    @app.route("/conta/<string:_id>", methods=["GET", "POST"])
    @login_required
    def delete_bill(_id: str):
        if request.method == "POST":
            operacao = request.form.get("operacao")
            if operacao == "excluir":
                current_app.db.bills.delete_one({"_id": _id})

            return redirect(url_for(".bills_to_pay"))

        return bills_to_pay(confirm_delete=True)

    @app.route("/edit/<string:_id>", methods=["GET", "POST"])
    @login_required
    def edit_bill(_id: str):
        operacao = request.form.get("operacao")
        bills_data = current_app.db.bills.find({"_id": _id})
        bill = [Bill(**bill) for bill in bills_data]
        if request.method == "POST":
            if operacao == "Confirmar":
                if request.form.get("billName"):
                    current_app.db.bills.update_one(
                        {"_id": _id},
                        {"$set": {"billName": request.form.get("billName")}},
                    )
                if request.form.get("billValue"):
                    current_app.db.bills.update_one(
                        {"_id": _id},
                        {"$set": {"billValue": request.form.get("billValue")}},
                    )
                if request.form.get("expireDate"):
                    expire_date = str(request.form.get("expireDate"))
                    expire_formatted = datetime.strptime(
                        expire_date, "%Y-%m-%d"
                    ).strftime("%d-%m-%Y")
                    current_app.db.bills.update_one(
                        {"_id": _id}, {"$set": {"expireDate": expire_formatted}}
                    )

                current_app.db.bills.update_one(
                    {"_id": _id},
                    {"$set": {"description": request.form.get("description")}},
                )

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
                    name=form.nome.data,
                    email=form.email.data,
                    income=form.income.data,
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
            flash("Dados de login incorretos", category="danger")
        return render_template("login.html", title="CoinCare - Login", form=form)

    return app
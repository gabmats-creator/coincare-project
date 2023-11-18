from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    FloatField,
    SubmitField,
    IntegerField,
    DateField,
    PasswordField,
    SelectField,
    TextAreaField,
)
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo


class BillForm(FlaskForm):
    bill_name = StringField(
        "Nome da conta a pagar",
        validators=[InputRequired(message="Esse campo é obrigatório")],
    )
    bill_value = FloatField(
        "Valor da conta", validators=[InputRequired(message="Esse campo é obrigatório")]
    )
    description = StringField("Descrição")

    opcoes = [("", "Selecione uma opção"), ("mensal", "Mensal"), ("uma vez", "Uma vez")]
    frequence = SelectField("Recorrência", choices=opcoes)
    submit = SubmitField(
        "Confirmar", render_kw={"value": "Confirmar"}
    )
    cancel = SubmitField(
        "Cancelar", render_kw={"value": "Cancelar"}
    )


class RegisterForm(FlaskForm):
    nome = StringField(
        "Nome completo do usuário",
        validators=[InputRequired(message="Esse campo é obrigatório")],
    )
    email = StringField(
        "E-mail",
        validators=[InputRequired(message="Esse campo é obrigatório"), Email()],
    )
    income = FloatField(
        "Renda mensal fixa",
        validators=[InputRequired(message="Esse campo é obrigatório")],
    )
    password = PasswordField(
        "Senha",
        validators=[
            InputRequired(message="Esse campo é obrigatório"),
            Length(min=4, max=20, message="Sua senha deve ter entre 4 e 20 caracteres"),
        ],
    )
    confirm_password = PasswordField(
        "Confirme sua senha",
        validators=[
            InputRequired(message="Esse campo é obrigatório"),
            EqualTo("password", message="Suas senhas devem ser iguais"),
        ],
    )
    submit = SubmitField("Registrar")


class LoginForm(FlaskForm):
    email = StringField(
        "E-mail",
        validators=[InputRequired(message="Esse campo é obrigatório"), Email()],
    )
    password = PasswordField(
        "Senha",
        validators=[
            InputRequired(message="Esse campo é obrigatório"),
            Length(min=4, max=20, message="Sua senha deve ter entre 4 e 20 caracteres"),
        ],
    )
    submit = SubmitField("Fazer login")


class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []


class ExtendedBillForm(BillForm):
    submit = SubmitField("Enviar")


class ReceiptForm(FlaskForm):
    receipt_name = StringField(
        "Nome da renda", validators=[InputRequired(message="Esse campo é obrigatório")]
    )
    receipt_value = FloatField(
        "Valor da renda", validators=[InputRequired(message="Esse campo é obrigatório")]
    )
    description = StringField("Descrição")

    submit = SubmitField(
        "Confirmar", render_kw={"value": "Confirmar"}
    )
    cancel = SubmitField(
        "Cancelar", render_kw={"value": "Cancelar"}
    )

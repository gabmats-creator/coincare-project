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
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo, ValidationError


class BillForm(FlaskForm):
    bill_name = StringField(
        "Nome da conta a pagar",
        validators=[InputRequired(message="Esse campo é obrigatório")],
    )
    bill_value = StringField(
        "Valor da conta", validators=[InputRequired(message="Esse campo é obrigatório")]
    )
    description = StringField("Descrição")

    opcoes = [("", "Selecione uma opção"), ("mensal", "Mensal"), ("uma vez", "Uma vez")]
    frequence = SelectField("Recorrência", choices=opcoes)
    submit = SubmitField("Confirmar", render_kw={"value": "Confirmar"})
    cancel = SubmitField("Cancelar", render_kw={"value": "Cancelar"})

    def validate_bill_value(form, field):
        try:
            cleaned_value = field.data.replace('.', '').replace(',', '.')
            field.data = float(cleaned_value)
        except ValueError:
            raise ValidationError('Valor da conta deve ser um número válido.')


class RegisterForm(FlaskForm):
    nome = StringField(
        "Nome completo do usuário",
        validators=[InputRequired(message="Esse campo é obrigatório")],
    )
    email = StringField(
        "E-mail",
        validators=[InputRequired(message="Esse campo é obrigatório"), Email()],
    )
    income = StringField(
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

    def validate_income(form, field):
        try:
            cleaned_value = field.data.replace('.', '').replace(',', '.')
            field.data = float(cleaned_value)
        except ValueError:
            raise ValidationError('Renda mensal deve ser um número válido.')


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

class ResetEmailForm(FlaskForm):
    email = StringField(
        "E-mail",
        validators=[InputRequired(message="Esse campo é obrigatório"), Email()],
    )
    submit = SubmitField("Verificar e-mail")


class ReceiptForm(FlaskForm):
    receipt_name = StringField(
        "Nome da renda", validators=[InputRequired(message="Esse campo é obrigatório")]
    )
    receipt_value = StringField(
        "Valor da renda", validators=[InputRequired(message="Esse campo é obrigatório")]
    )
    description = StringField("Descrição")

    submit = SubmitField("Confirmar", render_kw={"value": "Confirmar"})
    cancel = SubmitField("Cancelar", render_kw={"value": "Cancelar"})

    def validate_receipt_value(form, field):
        try:
            cleaned_value = field.data.replace('.', '').replace(',', '.')
            field.data = float(cleaned_value)
        except ValueError:
            raise ValidationError('Valor da renda deve ser um número válido.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Senha",
        validators=[
            InputRequired(message="Esse campo é obrigatório"),
            Length(min=4, max=20, message="Sua senha deve ter entre 4 e 20 caracteres"),
        ],
    )
    submit = SubmitField("Confirmar")

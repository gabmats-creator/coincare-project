from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, IntegerField, DateField, PasswordField, SelectField
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo

class BillForm(FlaskForm):
    bill_name = StringField("Nome da conta a pagar", validators=[InputRequired(message="Esse campo é obrigatório")])
    bill_value = FloatField("Valor da conta", validators=[InputRequired(message="Esse campo é obrigatório")])
    expire_date = DateField("Data de vencimento", validators=[InputRequired(message="Esse campo é obrigatório")])
    description = StringField("Descrição")

    opcoes = [('', 'Selecione uma opção'), ('mensal', 'Mensal'), ('anual', 'Anual'), ('uma vez', 'Uma vez')]
    frequence = SelectField('Recorrência', choices=opcoes)
    submit = SubmitField("Registrar")

class RegisterForm(FlaskForm):
    email = StringField("E-mail", validators=[InputRequired(message="Esse campo é obrigatório"), Email()])
    password = PasswordField("Senha", validators=[InputRequired(message="Esse campo é obrigatório"), Length(min=4, max=20, message="Sua senha deve ter entre 4 e 20 caracteres")])
    confirm_password = PasswordField("Confirme sua senha", validators=[InputRequired(message="Esse campo é obrigatório"), EqualTo("password", message="Suas senhas devem ser iguais")])
    submit = SubmitField("Registrar")

class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[InputRequired(message="Esse campo é obrigatório"), Email()])
    password = PasswordField("Senha", validators=[InputRequired(message="Esse campo é obrigatório"), Length(min=4, max=20, message="Sua senha deve ter entre 4 e 20 caracteres")])
    submit = SubmitField("Fazer login")
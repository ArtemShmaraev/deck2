from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


# Форма регистрации пользователя
class RegisterForm(FlaskForm):
    email = EmailField('Логин / почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    address = StringField('Адрес проживания', validators=[DataRequired()])
    tel = StringField('Номер телефона', validators=[DataRequired()])
    submit = SubmitField('Готово!')


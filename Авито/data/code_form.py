from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# форма отправки кода
class CodeForm(FlaskForm):
    code = StringField('Код подтверждения c email', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField, FileField, TextAreaField
from wtforms.validators import DataRequired


# форма добавления товара
class AddProductForm(FlaskForm):
    product = StringField('Название товара', validators=[DataRequired()])
    leader = IntegerField('Продавец')
    price = StringField('Цена', validators=[DataRequired()])
    opisanie = TextAreaField('Описание', validators=[DataRequired()])
    img = FileField('Фото товара', validators=[DataRequired()])
    is_finished = BooleanField('Товар продан?')
    submit = SubmitField('Готово!')

from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField


# форма удалени я товара и не только
class DelProductForm(FlaskForm):
    is_finished = BooleanField('Да')
    submit = SubmitField('Готово!')

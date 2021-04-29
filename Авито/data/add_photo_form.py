from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField
from wtforms.validators import DataRequired

# форма добавления картинки
class AddPhotoForm(FlaskForm):
    img = FileField('Ваше фото', validators=[DataRequired()])
    submit = SubmitField('Готово!')
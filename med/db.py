from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, validators, SubmitField, PasswordField, BooleanField, FileField, IntegerField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Log In')


msg = "Заполните поле"


class CreatePatientForm(FlaskForm):
    name = StringField('ФИО*', validators=[DataRequired(message=msg+" ФИО")])
    age = IntegerField('Возраст*', validators=[DataRequired(message=msg+" Возраст")])
    address = StringField('Адрес*', validators=[DataRequired(message=msg+" Адрес")])
    diagnosis = TextAreaField('Диагноз*', validators=[DataRequired(message=msg+" Диагноз")])
    reception = TextAreaField('Рецепты*', validators=[DataRequired(message=msg+" Рецепты")])
    image_allowed = FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения разрешены.')

    analysis = MultipleFileField('Анализы', validators=[image_allowed])
    image_before = MultipleFileField('Фотки До', validators=[image_allowed])
    image_after = MultipleFileField('Фотки После', validators=[image_allowed])

    submit = SubmitField('Создать Запись')

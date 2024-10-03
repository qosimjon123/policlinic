from flask import Flask, send_from_directory, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from config import Config
from db import LoginForm, CreatePatientForm
import markdown
from datetime import datetime
import logging



password_hashed_in_project = "secret123!"

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = '/login'
login_manager.login_message = "Пожалуйста пройдите авторизацию чтобы получить доступ к данному ресурсу"
login_manager.login_message_category = "warning"

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, login, password):
        self.login = login
        self.password = generate_password_hash(password)  # Hash the password

    def __repr__(self):
        return '<User %r>' % self.login

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(login=username).first()
        print(user.password)

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash("Вы успешно вошли в систему", 'success')
            return redirect(next_page or url_for('index'))

        flash("Ошибка входа. Неверный логин или пароль", "danger")

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("Выход Успешно выполнен", "success")
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    data = Patient.query.with_entities(Patient.id, Patient.name, Patient.diagnosis, Patient.age, Patient.upload_date, Patient.edited_date).all()
    # Отформатируем даты без секунд
    formatted_data = [
        {
            'id': d.id,
            'name': d.name,
            'diagnosis': d.diagnosis,
            'age': d.age,
            'upload_date': d.upload_date.strftime('%Y-%m-%d %H:%M') if d.upload_date else None,
            'edited_date': d.edited_date.strftime('%Y-%m-%d %H:%M') if d.edited_date else None
        }
        for d in data
    ]
    return render_template('index.html', data=formatted_data)




@app.route('/create_patient', methods=['GET', 'POST'])
@login_required
def create_patient():
    form = CreatePatientForm()

    if form.validate_on_submit():
        analysis_files = form.analysis.data
        image_before_files = form.image_before.data
        image_after_files = form.image_after.data

        analysis_paths = []
        image_before_paths = []
        image_after_paths = []

        # Save analysis files
        for file in analysis_files:
            if file and allowed_file(file.filename):
                filename = 'analysis/' + form.name.data + '/' + form.diagnosis.data + '/' + file.filename
                filename = secure_filename(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Ensure the directory exists
                file.save(filepath)
                analysis_paths.append(filename)

        # Save image before files
        for file in image_before_files:
            if file and allowed_file(file.filename):
                filename = 'image_before/' + form.name.data + '/' + form.diagnosis.data + '/' + file.filename
                filename = secure_filename(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Ensure the directory exists
                file.save(filepath)
                image_before_paths.append(filename)

        # Save image after files
        for file in image_after_files:
            if file and allowed_file(file.filename):
                filename = 'image_after/' + form.name.data + '/' + form.diagnosis.data + '/' + file.filename
                filename = secure_filename(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Ensure the directory exists
                file.save(filepath)
                image_after_paths.append(filename)

        new_patient = Patient(
            name=form.name.data,
            age=form.age.data,
            address=form.address.data,
            diagnosis=form.diagnosis.data,
            reception=form.reception.data,
            analysis=",".join(analysis_paths),
            image_before_url=",".join(image_before_paths),
            image_after_url=",".join(image_after_paths)
        )

        db.session.add(new_patient)
        db.session.commit()
        flash('Пациент успешно добавлен!', 'success')
        return redirect(url_for('index'))

    return render_template('create.html', form=form)

logging.basicConfig(level=logging.INFO)

@app.route('/delete_patient/<int:id>', methods=['POST'])
@login_required
def delete_patient(id):
    patient = Patient.query.get_or_404(id)

    def delete_files(file_paths):
        for file_path in file_paths:
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    logging.info(f"Файл {full_path} успешно удален.")
                except Exception as e:
                    logging.error(f"Ошибка при удалении файла {full_path}: {e}")
            else:
                logging.warning(f"Файл {full_path} не найден.")

    # Разделение путей файлов на список
    image_after_paths = patient.image_after_url.split(",") if patient.image_after_url else []
    image_before_paths = patient.image_before_url.split(",") if patient.image_before_url else []
    analysis_paths = patient.analysis.split(",") if patient.analysis else []

    # Удаление файлов с диска
    delete_files(image_after_paths)
    delete_files(image_before_paths)
    delete_files(analysis_paths)

    # Удаление записи из базы данных
    db.session.delete(patient)
    db.session.commit()

    flash('Запись пациента и связанные файлы успешно удалены!', 'success')
    return redirect(url_for('index'))



# from flask_wtf import FlaskForm
# from wtforms import StringField, validators, SubmitField, PasswordField, BooleanField, FileField, IntegerField, TextAreaField, MultipleFileField
# from wtforms.validators import DataRequired, ValidationError

# class LoginForm(FlaskForm):
#     username = StringField('Логин', validators=[DataRequired()])
#     password = PasswordField('Пароль', validators=[DataRequired()])
#     remember = BooleanField('Запомнить меня')
#     submit = SubmitField('Log In')

# msg = "Заполните поле"

# class CreatePatientForm(FlaskForm):
#     name = StringField('ФИО', validators=[DataRequired(message=msg)])
#     age = IntegerField('Возраст', validators=[DataRequired(message=msg)])
#     address = StringField('Адрес', validators=[DataRequired(message=msg)])
#     diagnosis = TextAreaField('Диагноз', validators=[DataRequired(message=msg)])
#     reception = TextAreaField('Рецепты', validators=[DataRequired(message=msg)])
#     submit = SubmitField('Создать Запись')


@app.route('/view/<int:id>', methods=['GET'])
@login_required
def view(id):
    patient = Patient.query.get_or_404(id)
    image_before_paths = patient.image_before_url.split(",")
    image_after_paths = patient.image_after_url.split(",")
    analysis_paths = patient.analysis.split(",")
    reception = markdown.markdown(patient.reception)
    diagnosis = markdown.markdown(patient.diagnosis)


    return render_template('show.html', patient=patient,
                           image_before_paths=image_before_paths,
                           image_after_paths=image_after_paths,
                           analysis_paths=analysis_paths, reception=reception, diagnosis=diagnosis)

@app.route('/download/<filename>', methods=['GET', 'POST'])
@login_required
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    age = db.Column(db.Integer)
    address = db.Column(db.String(200))
    diagnosis = db.Column(db.String(200))
    reception = db.Column(db.String(200))
    analysis = db.Column(db.String(200))
    image_before_url = db.Column(db.String(200))
    image_after_url = db.Column(db.String(200))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    edited_date = db.Column(db.DateTime, onupdate=datetime.utcnow)



@app.route('/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit(id):
    data = Patient.query.get_or_404(id)
    form = CreatePatientForm(obj=data)
    image_before_paths = data.image_before_url.split(",")
    image_after_paths = data.image_after_url.split(",")
    analysis_paths = data.analysis.split(",")
    if form.validate_on_submit():
        data.name = form.name.data
        data.age = form.age.data
        data.address = form.address.data
        data.diagnosis = form.diagnosis.data
        data.reception = form.reception.data



        db.session.commit()
        flash('Информация о пациенте была обновлена.', 'success')
        return redirect(url_for('index'))
    return render_template("edit.html", form=form, image_after_paths=image_after_paths,image_before_paths=image_before_paths,analysis_paths=analysis_paths, pid=id)

@app.route('/delete/<filename>', methods=['POST','GET'])
@login_required
def delete_img(filename):
    patient = Patient.query.get_or_404(filename)
    filename = filename.split('-*-')
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename[1])
    if filename[0] == "before":
        image_before_paths = data.image_before_url.split(",")
        os.remove(filename[1])
        image_before_paths.remove(full_path)
    elif filename[0] == "after":
        image_after_paths = data.image_after_url.split(",")
        os.remove(filename[1])
        image_after_paths.remove(full_path)
    elif filename[0] == "analysis":
        analysis_paths = data.analysis.split(",")
        os.remove(filename[1])
        analysis_paths.remove(full_path)
        analysis_paths.remove(full_path)
    else:
        return "Без категории, ошибка"
    return redirect(url_for('edit'))



if __name__ == '__main__':

    app.run(debug=True)

from flask import Flask, render_template, redirect, make_response, jsonify, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from tools.code_email import send_msg
from random import randint
from data.add_photo_form import AddPhotoForm
from data import db_session
from data.code_form import CodeForm
from data.add_product import AddProductForm
from data.login_form import LoginForm
from data.users import User
from data.api import UsersResource, UsersListResource
from data.api_prod import ProdResource, ProdListResource
from data.product import Products
from data.register import RegisterForm
from data.del_product import DelProductForm
from data.chat import Chat
from data.chats_form import ChatForm
import datetime
from PIL import Image
from flask_restful import Api
#from flask_ngrok import run_with_ngrok

# запуск приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
api.add_resource(UsersListResource, '/api/users')
api.add_resource(UsersResource, '/api/users/<int:id>')

api.add_resource(ProdListResource, '/api/prod')
api.add_resource(ProdResource, '/api/prod/<int:id>')
#run_with_ngrok(app)

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    app.run()


# обработка ошибка 404
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# обработка входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == str(form.email.data).lower()).first()
        if user and user.check_password(form.password.data):
            if user.is_good == "1":
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return redirect(f'/code/{int(user.id)}')
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    products = db_sess.query(Products).all()
    pr = []
    for i in range(len(products) // 4):
        s = []
        for j in range(4):
            s.append(products[i * 4 + j])
        pr.append(s)
    if len(products) % 4 == 3:
        pr.append([products[-1], products[-2], products[-3], 0])
    if len(products) % 4 == 2:
        pr.append([products[-1], products[-2], 0, 0])
    if len(products) % 4 == 1:
        pr.append([products[-1], 0, 0, 0])
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("index.html", products=pr, names=names, title='Список объявлений')


# обработка выхода
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# обработка регистрации
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Это пользователь уже существует")
        try:
            id = db_sess.query(User).order_by(User.id.desc()).first().id + 1
        except AttributeError:
            id = 1
        print(id)
        code = str(randint(1000, 9999))
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=str(form.email.data).lower(),
            address=form.address.data,
            tel=form.tel.data,
            img='img/site/avatar.jpg',
            code=code,
            is_good="0"
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect(f'/code/{int(id)}')
    return render_template('register.html', title='Регистрация', form=form)


# добавление фото профиля
@app.route('/add_photo', methods=['GET', 'POST'])
def add_photo():
    form = AddPhotoForm()
    if form.validate_on_submit():
        f = form.img.data
        file = open(f"static/img/users/user{current_user.id}.jpg", 'wb')
        file.write(f.read())
        file.close()
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.img = f"img/users/user{user.id}.jpg"

        im = Image.open(f"static/img/users/user{current_user.id}.jpg")
        x, y = im.size
        if x > y:
            d = (x - y) // 2
            im2 = im.crop((d, 0, x - d, y))
            im2.save(f'static/img/users/user{current_user.id}.jpg')
        if y > x:
            d = (y - x) // 2
            im2 = im.crop((0, d, x, y - d))
            im2.save(f'static/img/users/user{current_user.id}.jpg')
        db_sess.commit()
        return redirect(f'/user/{int(user.id)}')
    return render_template('add_photo.html', title='Добавьте фото', form=form)


@app.route('/add_photo/<int:id>', methods=['GET', 'POST'])
def add_photo_(id):
    form = AddPhotoForm()
    if form.validate_on_submit():
        f = form.img.data
        file = open(f"static/img/products/prod{id}.jpg", 'wb')
        file.write(f.read())
        file.close()
        db_sess = db_session.create_session()
        prod = db_sess.query(Products).filter(Products.id == id).first()
        prod.img = f"img/products/prod{id}.jpg"
        db_sess.commit()
        return redirect(f'/product/{int(id)}')
    return render_template('add_photo.html', title='Добавьте фото', form=form)


# отправка защитного кода
@app.route('/code/<int:id>', methods=['GET', 'POST'])
def code(id):
    form = CodeForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    print(user.code)
    if request.method == 'GET':
        send_msg(user.email, user.code)
    if form.validate_on_submit():
        code1 = form.code.data
        if str(code1) == str(user.code):
            user.is_good = "1"
            db_sess.commit()
            return redirect("/login")
        else:
            return render_template('code.html', title='Подтверждение почты', form=form, message="Неверный код!")
    return render_template('code.html', title='Подтверждение почты', form=form)


# добавление товара
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if current_user.is_authenticated:
        add_form = AddProductForm()
        if add_form.validate_on_submit():
            db_sess = db_session.create_session()
            try:
                id = db_sess.query(Products).order_by(Products.id.desc()).first().id + 1
            except AttributeError:
                id = 1
            product = Products(
                product=add_form.product.data,
                leader=current_user.id,
                is_finished=False,
                price=add_form.price.data,
                img=f"img/products/prod{id}.jpg",
                opisanie=add_form.opisanie.data
            )
            f = add_form.img.data
            file = open(f"static/img/products/prod{id}.jpg", 'wb')
            file.write(f.read())
            file.close()
            db_sess.add(product)
            db_sess.commit()
            return redirect('/')
        return render_template('add_product.html', title='Добавить объявление', form=add_form)
    return redirect('/')


# редактирование товара
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        product = db_sess.query(Products).filter(Products.id == id).first()
        if current_user.id == product.leader or current_user.id == 1:
            add_form = AddProductForm()
            if add_form.validate_on_submit():
                product.product = add_form.product.data
                product.leader = current_user.id
                product.price = add_form.price.data
                product.opisanie = add_form.opisanie.data

                f = add_form.img.data
                file = open(f"static/img/products/prod{id}.jpg", 'wb')
                file.write(f.read())
                file.close()
                db_sess.commit()
                return redirect('/')
            return render_template('add_product.html', title='Редактировать объявление', form=add_form)
        return redirect('/')
    return redirect('/')


# отображение списка чатов
@app.route("/chats", methods=['GET', 'POST'])
def chats():
    if current_user.is_authenticated:
        users = []
        db_sess = db_session.create_session()
        for s in current_user.chats:
            users.append([db_sess.query(User).filter(User.id == s.second_id).first(), s.id])
        return render_template('chats.html', users=users, title="Сообщения")


# удаление конкретного чата
@app.route("/del_chat/<int:id>", methods=['GET', 'POST'])
def del_chat(id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        chat = db_sess.query(Chat).filter(Chat.id == id).first()
        if current_user.id == chat.first_id or current_user.id == 1:
            add_form = DelProductForm()
            if add_form.validate_on_submit():
                f = add_form.is_finished.data
                if f:
                    db_sess.delete(chat)
                    db_sess.commit()
                    return redirect('/')
                else:
                    return redirect('/')
            return render_template('del_product.html', title='Удалить чат?', form=add_form)
        return redirect('/')
    return redirect('/')


# отображение чата
@app.route("/chat/<int:id>", methods=['GET', 'POST'])
def chat(id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        chat = db_sess.query(Chat).filter(Chat.first_id == current_user.id, Chat.second_id == id).first()
        if current_user.id != id:
            if chat is None:
                ch = Chat(
                    first_id=current_user.id,
                    second_id=id,
                    sms=""
                )
                db_sess.add(ch)
                db_sess.commit()
            chat = db_sess.query(Chat).filter(Chat.first_id == id, Chat.second_id == current_user.id).first()
            if chat is None:
                ch = Chat(
                    first_id=id,
                    second_id=current_user.id,
                    sms=""
                )
                db_sess.add(ch)
                db_sess.commit()
            chat = db_sess.query(Chat).filter(Chat.first_id == current_user.id, Chat.second_id == id).first()
            sms = chat.sms.split("!@#")
            sms_chat = []
            for i in range(len(sms)):
                sms[i] = sms[i].split("#@!")
                if sms[i] != [""]:
                    sms_chat.append(sms[i])
            user = db_sess.query(User).filter(User.id == id).first()
            form = ChatForm()
            if form.validate_on_submit():
                if request.method == "POST":
                    text = form.text.data
                    time = datetime.datetime.now().strftime("%d %b %H:%M")
                    chat_my = db_sess.query(Chat).filter(Chat.first_id == current_user.id, Chat.second_id == id).first()
                    chat_you = db_sess.query(Chat).filter(Chat.first_id == user.id,
                                                          Chat.second_id == current_user.id).first()
                    chat_my.sms += f"!@#1#@!{text}#@!{time}"
                    chat_you.sms += f"!@#2#@!{text}#@!{time}"
                    db_sess.commit()
                    return redirect(f"/chat/{id}")
            return render_template('chat.html', sms=sms_chat, chat=chat, user=user, form=form, title="Чат")
        return redirect("/")
    return redirect("/")


# отображение аккаунта пользователя
@app.route("/user/<int:id>", methods=['GET', 'POST'])
def user_pos(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if user is None:
        return redirect("/")
    return render_template('user.html', user=user, title='User')


# редактирование аккаунта
@app.route("/edit_user/<int:id>", methods=['GET', 'POST'])
def edit_user(id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if current_user.id == user.id or current_user.id == 1:
            form = RegisterForm()
            if form.validate_on_submit():
                if form.password.data != form.password_again.data:
                    return render_template('register.html', title='Редактирование', form=form,
                                           message="Пароли не совпадают")
                if user.email == form.email.data:
                    user.name = form.name.data
                    user.surname = form.surname.data
                    user.email = form.email.data
                    user.address = form.address.data
                    user.tel = form.tel.data
                    user.set_password(form.password.data)
                    db_sess.commit()
                    return redirect('/')
                return render_template('register.html', title='Редактирование', form=form,
                                       message="Старый и новый email не совподают")
            return render_template('register.html', title='Редактирование', form=form, user=user)
        return redirect("/")
    return redirect("/")


# удаление товара
@app.route('/del_product/<int:id>', methods=['GET', 'POST'])
def del_product(id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        prod = db_sess.query(Products).filter(Products.id == id).first()
        print(prod.user)
        if current_user.id == prod.leader or current_user.id == 1:
            add_form = DelProductForm()
            if add_form.validate_on_submit():
                f = add_form.is_finished.data
                if f:
                    db_sess.delete(prod)
                    db_sess.commit()
                    return redirect('/')
                else:
                    return redirect('/')
            return render_template('del_product.html', title='Удалить товар?', form=add_form)
        return redirect('/')
    return redirect('/')


# продажа товара
@app.route('/ok_product/<id>', methods=['GET', 'POST'])
def ok_product(id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        prod = db_sess.query(Products).filter(Products.id == id).first()
        if current_user.id == prod.leader or current_user.id == 1:
            add_form = DelProductForm()
            if add_form.validate_on_submit():
                f = add_form.is_finished.data
                if f:
                    prod.is_finished = True
                    db_sess.commit()
                    return redirect('/')
                else:
                    return redirect('/')
            return render_template('del_product.html', title='Товар продан?', color="success", form=add_form)
        return redirect('/')
    return redirect('/')


# отображение сранички с товаром
@app.route("/product/<int:id>", methods=['GET', 'POST'])
def prod(id):
    db_sess = db_session.create_session()
    prod = db_sess.query(Products).filter(Products.id == id).first()
    if prod is None:
        return redirect("/")
    return render_template('prod.html', product=prod, title="Товар")


if __name__ == '__main__':
    db_session.global_init("db/mars.db")
    # app.register_blueprint(api.blueprint)
    main()

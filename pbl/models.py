from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from pbl import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    products = db.relationship('Product', backref='author', lazy=True)
    cart = db.relationship('Cart', backref='author', lazy=True)
    bills = db.relationship('Bill', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    info = db.Column(db.Text, nullable=False , default="No Information Available")
    image_url = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cart = db.relationship('Cart', backref='product', lazy=True)
    bill_products = db.relationship('Bill_Products', backref='product', lazy=True)

    def __repr__(self):
        return f"Product('{self.name}', '{self.date_created}' , '{self.price}')"


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f"Cart('{self.user_id}', '{self.product_id}')"


class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_products = db.relationship('Bill_Products', backref='bill', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phonenumber = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Bill('{self.user_id}', '{self.total}')"


class Bill_Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f"Bill_Product('{self.bill_id}','{self.product_id}')"

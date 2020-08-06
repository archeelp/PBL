import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from pbl import app, db, bcrypt, mail
from pbl.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             ProductForm, RequestResetForm, ResetPasswordForm ,BillingForm)
from pbl.models import User, Product ,Cart ,Bill,Bill_Products
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime


def produce_graph():
    if not current_user.is_authenticated:
        bills=Bill.query.filter().all()
        bills=list(filter(lambda x: float((x.date_created - datetime.now()).total_seconds())<604800,bills))
        newbill={"Mon":0,"Tue":0,"Wed":0,"Thu":0,"Fri":0,"Sat":0,"Sun":0}
        for x in bills:
            newbill[x.date_created.strftime("%a")]+=1
        return newbill
    else:
        bills=Bill.query.filter_by(author=current_user)
        bills=list(filter(lambda x: float((x.date_created - datetime.now()).total_seconds())<604800,bills))
        newbill={"Mon":0,"Tue":0,"Wed":0,"Thu":0,"Fri":0,"Sat":0,"Sun":0}
        for x in bills:
            newbill[x.date_created.strftime("%a")]+=1
        return newbill


@app.route("/")
@app.route("/home")
def home():
    newbill=produce_graph()
    return render_template('home.html',newbill=newbill)


@app.route("/about")
def about():
    newbill=produce_graph()
    return render_template('about.html', title='About',newbill=newbill)


@app.route("/register", methods=['GET', 'POST'])
def register():
    newbill=produce_graph()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form,newbill=newbill)


@app.route("/login", methods=['GET', 'POST'])
def login():
    newbill=produce_graph()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form,newbill=newbill)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    newbill=produce_graph()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form,newbill=newbill)


@app.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    newbill=produce_graph()
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data,discount=form.discount.data if form.discount.data else 0.0, price = form.price.data, info = form.info.data, image_url= form.image_url.data, author=current_user)
        db.session.add(product)
        db.session.commit()
        flash('Your product has been added', 'success')
        return redirect(url_for('home'))
    form.discount.data=0.0
    return render_template('new_product.html', title='New Product',
                           form=form, legend='New Product',newbill=newbill)


@app.route("/addtocart/<int:product_id>", methods=['GET','POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    cart=Cart(author=current_user,product=product)
    db.session.add(cart)
    db.session.commit()
    flash('Product added to cart', 'success')
    next_page = request.args.get('next')
    return redirect(next_page) if next_page else redirect(url_for('cart'))


@app.route("/removefromcart/<int:cart_id>", methods=['GET','POST'])
@login_required
def remove_from_cart(cart_id):
    cart = Cart.query.filter_by(product_id=cart_id)[0]
    if cart.author != current_user:
        abort(403)
    db.session.delete(cart)
    db.session.commit()
    flash('Product deleted from cart', 'success')
    return redirect(url_for('cart'))

def search_product(product,q):
    if q in product.name or q in product.info :
        return True
    elif q.isnumeric() :
        if float(q)==product.id or float(q)==product.price :
            return True
    else:
        flash('Product not found. Please add the product first to search!','info')
        return False

@app.route("/allproducts")
@login_required
def all_products():
    page = request.args.get('page', 1, type=int)
    if request.args.get('search'):
        products = list(filter(lambda product : search_product(product,request.args.get('search')),Product.query.filter_by(author=current_user)))
        #if len(products)==0:
            #return redirect(url_for(new_product))
        print(products)
        return render_template('all_products.html', products=products,title="Searched Product",disabled=True)
    else :
        p = list(Product.query.filter_by(author=current_user))
        products = Product.query.filter_by(author=current_user)\
            .order_by(Product.date_created.desc())\
            .paginate(page=page, per_page=16)
    if len(p)==0:
        flash('No product present currently . Please add products','info')
    return render_template('all_products.html', products=products,title="All Products",disabled = False) if len(p)>0 else redirect(url_for('new_product'))


@app.route("/cart")
@login_required
def cart():
    products_id = Cart.query.filter_by(author=current_user)
    pids =[pid.product_id for pid in products_id]
    products = [ (Product.query.get(pid),pids.count(pid)) for pid in set(pids)]
    mrp,n,t=0,0,0
    for product in products:
        mrp+=product[0].price*product[1]
        n+=product[1]
        t+=product[0].price*product[1]*(1-product[0].discount*0.01)
    d = round((1-t/mrp)*100,2) if len(products)>0 else -100
    if d==-100:
        flash('You have nothing in cart. Please add some products and then proceed','danger')
    return render_template('cart.html',title="Cart", products=products,mrp=mrp,n=n,t=t,d=d) if d!=-100 else redirect(url_for('all_products'))


@app.route("/cart/proceed",methods=["POST"])
@login_required
def proceed():
    discount=0.0
    if request.method == "POST":
        discount=float(request.form.get('discount'))
    form = BillingForm()
    products_id = Cart.query.filter_by(author=current_user)
    pids =[pid.product_id for pid in products_id]
    products = [ (Product.query.get(pid),pids.count(pid)) for pid in set(pids)]
    mrp,n,t=0,0,0
    for product in products:
        mrp+=product[0].price*product[1]
        n+=product[1]
        t+=product[0].price*product[1]*(1-product[0].discount*0.01)
    d=round((1-t/mrp)*100,2)
    return render_template('proceed.html',form=form,products=products,mrp=mrp,n=n,t=t,d=d,discount=discount,title="Summary",legend="Summary")


def send_bill_email(emailfrom,emailto,name,url):
    try:
        msg = Message('Bill Copy',
                    sender=emailfrom,
                    recipients=[emailto])
        msg.body = f'''Thanks for shopping at {name}
        You can view your bill by following the link given below:
        {url}
        If you did not make this request then simply ignore this email and no changes will be made.
    '''
        mail.send(msg)
    except :
        flash('unable to send mail','danger')


@app.route("/cart/confirmed",methods=["POST"])
@login_required
def confirmed():
    form=BillingForm()
    cart_items = Cart.query.filter_by(author=current_user)
    pids =[pid.product_id for pid in cart_items]
    products = [ (Product.query.get(pid),pids.count(pid)) for pid in set(pids)]
    mrp,n,t=0,0,0
    for product in products:
        mrp+=product[0].price*product[1]
        n+=product[1]
        t+=product[0].price*product[1]*(1-product[0].discount*0.01)
    if form.validate_on_submit():
        total_bill = Bill(name = form.name.data, email = form.email.data, phonenumber = form.phone.data,total=mrp,final_price=t*(1-0.01*float(request.form.get('discount'))),discount=request.form.get('discount'), author = current_user)
        db.session.add(total_bill)
        db.session.commit()

        for item in cart_items:
            bp = Bill_Products(bill=Bill.query.get(item.id) , product=Product.query.get(item.product_id))
            db.session.add(bp)
            db.session.delete(item)
            db.session.commit()
        #http://localhost:5000/bill/
        url="https://deploy-pbl.herokuapp.com/bill/"+str(total_bill.id)
        send_bill_email(current_user.email,form.email.data,current_user.username,url)

        flash('Bill created successfully', 'success')
        return redirect(url_for('home'))



def search_bill(bill,q):
    if q in bill.name :
        return True
    elif q.isnumeric() :
        if float(q)==bill.id or float(q)==bill.final_price :
            return True
    else:
        flash('Bill not found.','info')
        return False



    
@app.route("/bill",methods=["GET","POST"])
@login_required
def all_bill():
    newbill=produce_graph()
    page = request.args.get('page', 1, type=int)
    if request.args.get('search'):
        bills = list(filter(lambda product : search_bill(bill,request.args.get('search')),Bill.query.filter_by(author=current_user)))
        #if len(products)==0:
            #return redirect(url_for(new_product))
        print(bills)
        return render_template('view_all_bills.html', bills=bills,title="Searched Bill",disabled=True,newbill=newbill)
    else:    
        p = list(Bill.query.filter_by(author=current_user))
        bills = Bill.query.filter_by(author=current_user)\
            .order_by(Bill.date_created.desc())\
            .paginate(page=page, per_page=10)
    if len(p)==0:
        flash('No bill present','info')
    return render_template('view_all_bills.html',title="Bill", bills = bills,newbill=newbill) if len(p)>0 else redirect(url_for('home'))

@app.route("/bill/<int:bill_id>",methods=["GET","POST"])
@login_required
def particular_bill(bill_id):
    newbill=produce_graph()
    details = Bill.query.get_or_404(bill_id)
    #print("details",details.id)
    products = Bill_Products.query.filter_by(id=details.id)
    #print("products", products)
    products = [ Product.query.get(x.product_id) for x in products ]
    products = [ (x,products.count(x)) for x in set(products) ]
    
    quantity=0
    total=0
    discount=0
    mrp=0
    for product in products:
        quantity+=product[1]
        total+=product[1]*product[0].price*(1-product[0].discount*0.01)
        mrp+=product[0].price
    #discount=(mrp*quantity-total)/(mrp*quantity)*100    

    return render_template('view_particular_bill.html',title="Bill" , quantity=quantity, total=total,mrp=mrp, details=details, products=products, newbill=newbill)


@app.route("/product/<int:product_id>")
@login_required
def product(product_id):
    newbill=produce_graph()
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', title=product.name, product=product,newbill=newbill)


@app.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    newbill=produce_graph()
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.info = form.info.data
        product.image_url = form.image_url.data
        db.session.commit()
        flash('Your product has been updated!', 'success')
        return redirect(url_for('product', product_id=product.id))
    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.discount.data = product.discount 
        form.info.data = product.info
        form.image_url.data = product.image_url
    return render_template('new_product.html', title='Update product',
                           form=form, legend='Update product',newbill=newbill)


@app.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Your product has been deleted!', 'success')
    return redirect(url_for('home'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    newbill=produce_graph()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form,newbill=newbill)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    newbill=produce_graph()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form,newbill=newbill)

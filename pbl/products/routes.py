from flask import Blueprint

products=Blueprint('products',__name__)



@products.route("/product/new", methods=['GET', 'POST'])
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


@products.route("/allproducts")
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



@products.route("/product/<int:product_id>")
@login_required
def product(product_id):
    newbill=produce_graph()
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', title=product.name, product=product,newbill=newbill)


@products.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
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
        product.info = form.info.data
        product.image_url = form.image_url.data
        db.session.commit()
        flash('Your product has been updated!', 'success')
        return redirect(url_for('product', product_id=product.id))
    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.info.data = product.info
        form.image_url.data = product.image_url
    return render_template('new_product.html', title='Update product',
                           form=form, legend='Update product',newbill=newbill)


@products.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Your product has been deleted!', 'success')
    return redirect(url_for('home'))

                          

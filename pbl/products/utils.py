



def search_product(product,q):
    if q in product.name or q in product.info :
        return True
    elif q.isnumeric() :
        if float(q)==product.id or float(q)==product.price :
            return True
    else:
        flash('Product not found. Please add the product first to search!','info')
        return False

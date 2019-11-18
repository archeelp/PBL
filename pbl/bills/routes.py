from flask import Blueprint

bills=Blueprint('bills',__name__)




@bills.route("/bill",methods=["GET","POST"])
@login_required
def all_bill():
    newbill=produce_graph()
    page = request.args.get('page', 1, type=int)
    p = list(Bill.query.filter_by(author=current_user))
    bills = Bill.query.filter_by(author=current_user)\
        .order_by(Bill.date_created.desc())\
        .paginate(page=page, per_page=10)
    if len(p)==0:
        flash('No bill present','info')
    return render_template('view_all_bills.html',title="Bill", bills = bills,newbill=newbill) if len(p)>0 else redirect(url_for('home'))

@bills.route("/bill/<int:bill_id>",methods=["GET","POST"])
@login_required
def particular_bill(bill_id):
   newbill=produce_graph()
   details = Bill.query.get_or_404(bill_id)
   bill = Bill_Products.query.get_or_404(bill_id)
   products = Bill_Products.query.filter_by(bill=bill)
   products = [ Product.query.get(x.product_id) for x in products ]
   return render_template('view_particular_bill.html',title="Bill", bill = bill , details=details, products=products, newbill=newbill)

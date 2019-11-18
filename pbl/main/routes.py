from flask import Blueprint

main=Blueprint('main',__name__)




@main.route("/")
@app.route("/home")
def home():
    newbill=produce_graph()
    return render_template('home.html',newbill=newbill)


@main.route("/about")
def about():
    newbill=produce_graph()
    return render_template('about.html', title='About',newbill=newbill)

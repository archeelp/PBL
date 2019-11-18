



class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    image_url = StringField('Image Url' , validators=[DataRequired()] )
    price = FloatField('Price' , validators=[DataRequired()] )
    discount = FloatField('Discount' )
    info = TextAreaField('Information', validators=[DataRequired()])
    submit = SubmitField('Add Product')

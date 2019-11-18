



class BillingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(10)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Proceed')

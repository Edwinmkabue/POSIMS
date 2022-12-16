from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, url

class ItemForm(Form):
    id = StringField(
        'id', validators=[DataRequired()]
    )
    name = StringField(
        'name', validators=[DataRequired()]
    )
    quantity = StringField(
        'quantity', validators=[DataRequired()]
    )
    price = StringField(
        'price', validators=[DataRequired()]
    )

class SaleForm(Form):
    id = StringField(
        'id', validators=[DataRequired()]
    )
    name = StringField(
        'name', validators=[DataRequired()]
    )
    quantity = StringField(
        'quantity', validators=[DataRequired()]
    )
    price = StringField(
        'price', validators=[DataRequired()]
    )
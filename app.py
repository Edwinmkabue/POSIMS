from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, flash
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from forms import *
from wtforms import Form,validators
import babel
import dateutil.parser

# ------------------------------------------------------------------------------------------------------
# App Config
# ------------------------------------------------------------------------------------------------------

app = Flask(__name__)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres@localhost:5432/hardware_store"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/hardware_store'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# ------------------------------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------------------------------

# Create the items model
class Item(db.Model):
    __tablename__ = 'Item'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    quantity = db.Column(db.Integer, nullable = True)
    price = db.Column(db.Integer, nullable = False)


# Create the sales model
class Sale(db.Model):
    __tablename__ = 'Sale'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable = True)
    price = db.Column(db.Integer, primary_key = True)


with app.app_context():
    db.create_all()

# --------------------------------------------------------------------------------------------------
# Filters
# --------------------------------------------------------------------------------------------------

def format_datetime(value, format = 'medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

# --------------------------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('pages/home.html')

# Items
# ---------------------------------------------------------------------------------------------------
@ app.route('/items')
def items():
    item_inventorys = db.session.query(Item.id, Item.name, Item.quantity).distinct()
    data = []
    for item_inventory in item_inventorys:
        items_data= []
        for item in Item.query.filter_by(id=item_inventory.id).filter_by(name=item_inventory.name).filter_by(quantity=item_inventory.quantity).all():
            items_data.append({
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity
            })
            data.append({
                'id': item_inventory.id,
                'name': item_inventory.name,
                'quantity': item.quantity,
                'items': items_data 
            })

    return render_template('pages/items.html', stocks=data)

@app.route('/items/search', methods=['POST'])
def search_items():
    search_term = request.form.get('search_term', '')
    items = db.session.query.filter(Item.name.ilike('%' + search_term + "%")).all()
    data = []
    for item in items:
        data.append({
            "id":item.id,
            "name":item.name,
            "quantity": item.quantity
        })
    response={
        "count":len(items),
        "data":data
    }
    return render_template('pages/search_items.html', results=response, search_item=request.form.get('search_term', ''))


# ---------------------------------------------------------------------------------------------------
# Add new item 
# ---------------------------------------------------------------------------------------------------
@app.route("/items/create", methods=["GET"])
def create_item_form():           
    form = ItemForm()
    return render_template('forms/new_item.html', form=form)

@app.route('/items/create', methods=['POST'])
def create_item_submission():
    form = ItemForm(request.form, meta={'csrf': False}) 

    if form.validate():
        try:
            item = Item(id = form.id.data,
                        name = form.name.data, 
                        quantity = form.quantity.data,
                        price = form.price.data 
                        )
            db.session.add(item)
            db.session.commit()
            flash(request.form['name']+ 'successfuly added!')
            return render_template('pages/items.html')
        except:
            db.session.rollback()
            flash(request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
    else:
        flash('Error from validate!!')
    return render_template('forms/new_item.html', form=form)

# --------------------------------------------------------------------------------
# Sales
# --------------------------------------------------------------------------------
@app.route('/sales')
def sales():
    sales = Sale.query.all()
    data = []
    for sale in sales:
        data.append({
            'id':sale.id,
            'name':sale.name
        })
    return render_template('pages/sales.html', sales=data)

@app.route('/sales/search', methods=['POST'])
def search_sales():
    search_term = request.form.get('search_term')
    result = Sale.query.filter(Sale.name.ilike('%' + search_term + '%')).all()
    data = ()
    for sale in result:
        data.append([{
            "id": sale.id,
            "name": sale.name,
            "price": sale.price,
            "quantity": sale.quantity
        }])
    response={
        "count": len(result),
        "data": data
    }
    return render_template('pages/search_sales', results=response, search_term=request.form.get('search_term', ''))

# ----------------------------------------------------------------------------------------------------------------------------
# Sell an item
# ----------------------------------------------------------------------------------------------------------------------------
@app.route('/sales/create', methods=['GET'])
def create_sale_form():
    form = SaleForm()
    return render_template('forms/new_sale.html', form=form)

@app.route('/sale/create', methods=['POST'])
def create_sale_submission():
    form = SaleForm(request.form, meta={'crsf':False})

    if form.validate():
        try:
            sale = Sale(id = form.id.data,
                        name = form.name.data,
                        price = form.price.data,
                        quantity = form.quantity.data
                        )
            db.session.add(sale)
            db.session.commit()
            flash(request.form['name'] + 'successfully added!')
            return render_template('pages/sales.html')
        except:
            db.session.rollback()
            flash(request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
    else:
        flash('Error from validate!!')
    return render_template('forms/new_sale.html', form=form)


# ----------------------------------------------------------------------------------------------------------------------------
#  Update
# ----------------------------------------------------------------------------------------------------------------------------
@app.route('/items/<int:item_id>/edit', methods = ['GET'])
def edit_item(item_id):
    item_id = request.args.get('item_id')
    form = ItemForm()
    item = item.query.get(item_id)
    item_info={
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "quantity": item.quantity
    }
    return render_template('forms/edit_item.html', form= form, item=item_info)
    
@app.route('/items/<int:item_id>/edit', methods=['POST'])
def edit_item_submission(item_id):
    item = Item.query.get(item_id)
    item.id = request.form['id']
    item.name = request.form['name']
    item.price = request.form['price']
    item.quantity = request.form['quantity']
    try:
        db.session.commit()
        flash('Item  ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Item ' + item.name + ' could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_item', item_id=item_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
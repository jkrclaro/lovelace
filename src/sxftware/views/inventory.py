from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    current_app
)
from flask_login import login_required, current_user

from src.sxftware.models import db
from src.sxftware.models.merchant import Product, Inventory, Listing
from src.sxftware.forms import InventoryBaseForm, InventoryCreateForm
from src.sxftware.helpers.model import get_or_404
from src.sxftware.helpers.flash import flash_form_errors
from src.sxftware.helpers.inventory import Actioner

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')


@inventory_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    products = Product.query.filter_by(merchant_id=current_user.merchant.id).all()
    return render_template('inventory/index.html', products=products)


@inventory_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = InventoryCreateForm()
    if form.validate_on_submit():
        data = {
            'product_id': form.product.data.id,
            'quantity': form.quantity.data,
            'price': form.price.data,
            'sku': form.sku.data,
        }
        inventory = Inventory(**data)
        db.session.add(inventory)
        db.session.commit()
        flash('Successfully added SKU', 'success')
        return redirect(url_for('inventory.index'))
    else:
        flash_form_errors(form.errors)

    return render_template('inventory/create.html', form=form)


@inventory_bp.route('/<uid>/create', methods=['GET', 'POST'])
@login_required
def create_with_product_uid(uid):
    options = {'uid': uid}
    product = get_or_404(Product, options)

    form = InventoryBaseForm()
    if form.validate_on_submit():
        data = {
            'product_id': product.id,
            'quantity': form.quantity.data,
            'price': form.price.data,
            'sku': form.sku.data,
        }
        inventory = Inventory(**data)
        db.session.add(inventory)
        db.session.commit()
        flash('Successfully added SKU', 'success')
    else:
        flash_form_errors(form.errors)

    return redirect(url_for('product.retrieve', uid=uid))


@inventory_bp.route('/<uid>/<sku>', methods=['GET', 'POST'])
@login_required
def retrieve(uid, sku):
    options = {'uid': uid, 'merchant_id': current_user.merchant.id}
    product = get_or_404(Product, options)

    options = {'product_id': product.id, 'sku': sku}
    inventory = get_or_404(Inventory, options)

    form = InventoryBaseForm(obj=inventory)
    if form.validate_on_submit():
        if form.menus.data:
            for menu in form.menus.data:
                data_listing = {
                    'inventory_id': inventory.id,
                    'menu_id': menu.id
                }
                listing = Listing(**data_listing)
                db.session.add(listing)
            db.session.commit()
            flash('Successfully linked menu to SKU', 'success')
        else:
            inventory.price = form.price.data
            inventory.quantity = form.quantity.data
            inventory.sku = form.sku.data
            inventory.is_active = form.is_active.data
            db.session.add(inventory)
            db.session.commit()
            flash('Successfully updated SKU', 'success')

        url = url_for('inventory.retrieve', uid=uid, sku=inventory.sku)
        return redirect(url)
    else:
        flash_form_errors(form.errors)

    context = {'inventory': inventory, 'form': form, 'product': product}
    return render_template('inventory/retrieve.html', **context)


@inventory_bp.route('/perform', methods=['GET', 'POST'])
@login_required
def perform():
    action = request.form.get('action')
    inventories = request.form.getlist('inventories_selected')
    Actioner(action, inventories)
    return redirect(url_for('inventory.index'))

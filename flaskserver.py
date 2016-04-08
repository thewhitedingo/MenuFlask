from flask import Flask, render_template, url_for, jsonify, request, redirect, flash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db import engine, Base, Restaurant, MenuItem
Base.metadata.bind  = engine
DBSession = sessionmaker(bind = engine)
s = DBSession()
# create instance of the Class with name of app
app = Flask(__name__)

def	restaurant(restaurant_id):
	restaurant = s.query(Restaurant).filter_by(id = restaurant_id).one()
	return restaurant

def restaurants():
	restaurants = s.query(Restaurant).all()
	return restaurants

def menu_items(restaurant_id):
	items = s.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return items

def menu_item(menu_id):
	item = s.query(MenuItem).filter_by(id = menu_id).one()
	return item

@app.route('/restaurant/<restaurant_id>/JSON/')
def menu_JSON(restaurant_id):
	rstr = restaurant(restaurant_id)
	return jsonify(Restaurant=[rstr.serialize])

@app.route('/restaurant/JSON/')
def rstr_list_JSON():
	rstr_list = restaurants()
	return jsonify(Restaurant=[r.serialize for r in rstr_list])

@app.route('/restaurant/<menu_id>/item/JSON/')
def item_JSON(menu_id):
	item = menu_item(menu_id)
	return jsonify(MenuItem=[item.serialize])

@app.route('/restaurant/<restaurant_id>/menu/JSON/')
def menu_list_JSON(restaurant_id):
	item_list = menu_items(restaurant_id)
	return jsonify(MenuItem=[r.serialize for i in item_list])

# decorator wraps the function inside the app.route function
# the function following will run if either route is given to the server
@app.route('/')
@app.route('/restaurant/')
def list():
	restaurant_list = restaurants()
	return render_template('restaurant_list.html', restaurant_list = restaurant_list)

# route to the restaurants menu if the link is clicked
@app.route('/restaurant/<restaurant_id>/')
def menus(restaurant_id):
	rstr = restaurant(restaurant_id)
	item_list = menu_items(restaurant_id)
	return render_template('restaurant_menu.html', restaurant = rstr, menu = item_list)

# form to add a restaurant item to the menu
@app.route('/restaurant/<int:restaurant_id>/new_item/', methods=['GET', 'POST'])
def add_item(restaurant_id):
	if request.method == 'POST':
		new_item = MenuItem(name = request.form['name'], description = request.form['description'], 
			price = request.form['price'], restaurant_id = restaurant_id)
		s.add(new_item)
		s.commit()
		flash("New item has been added")
		return redirect(url_for('menus', restaurant_id = restaurant_id))
	else:
		return render_template('add_item.html', restaurant_id = restaurant_id)

# form to edit an item
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit_item/', methods=['GET', 'POST'])
def edit_item(restaurant_id, menu_id):
	item = menu_item(menu_id)
	if request.method == 'POST':
		if request.form['name']:
			item.name = request.form['name']
		if request.form['description']:
			item.description = request.form['description']
		if request.form['price']:
			item.price = request.form['price']
		s.add(item)
		s.commit()
		return redirect(url_for('menus', restaurant_id = restaurant_id))
	else:
		return render_template('edit_item.html', restaurant_id = restaurant_id, menu_id = menu_id, item = item)

# route to delete an item from the menu
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete_item/', methods=['GET', 'POST'])
def delete_item(restaurant_id, menu_id):
	item = menu_item(menu_id)
	if request.method == 'POST':
		s.delete(item)
		s.commit()
		return redirect(url_for('menus', restaurant_id = restaurant_id))
	else:
		return render_template('delete_item.html', restaurant_id = restaurant_id, menu_id = menu_id, item = item)

# run the server only if it's not an imported module
if __name__ == '__main__':
	app.secret_key = 'key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
from flask import Flask, render_template, url_for, jsonify, request, redirect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db import engine, Base, Restaurant, MenuItem
Base.metadata.bind  = engine
DBSession = sessionmaker(bind = engine)
s = DBSession()
# create instance of the Class with name of app
app = Flask(__name__)
# decorator wraps the function inside the app.route function
# the function following will run if either route is given to the server
@app.route('/')
@app.route('/restaurant/')
def list():
	restaurant = s.query(Restaurant).all()
	return render_template('restaurant_list.html', restaurant_list = restaurant)
	# output = '<h1>Restaurants and Menus</h1>'
	# restaurant = s.query(Restaurant).all()
	# for res in restaurant:
	# 	output += '<p><b>%s</b></p>' %res.name
	# 	output += '<a href="restaurant/%s">Menu</a>' %res.id
	# return output
# route to the restaurants menu if the link is clicked
@app.route('/restaurant/<restaurant_id>/')
def menus(restaurant_id):
	restaurant = s.query(Restaurant).filter_by(id = restaurant_id).one()
	output = '<h1>%s</h1>' %restaurant.name
	item_list = s.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return render_template('restaurant_menu.html', restaurant = restaurant, menu = item_list)

# form to add a restaurant item to the menu
@app.route('/restaurant/<int:restaurant_id>/new_item/', methods=['GET', 'POST'])
def add_item(restaurant_id):
	if request.method == 'POST':
		new_item = MenuItem(name = request.form['name'], description = request.form['description'], 
			price = request.form['price'], restaurant_id = restaurant_id)
		s.add(new_item)
		s.commit()
		return redirect(url_for('menus', restaurant_id = restaurant_id))
	else:
		return render_template('add_item.html', restaurant_id = restaurant_id)

# form to edit an item
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit_item/', methods=['GET', 'POST'])
def edit_item(restaurant_id, menu_id):
	item = s.query(MenuItem).filter_by(id = menu_id).one()
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
	item = s.query(MenuItem).filter_by(id = menu_id).one()
	if request.method == 'POST':
		s.delete(item)
		s.commit()
		return redirect(url_for('menus', restaurant_id = restaurant_id))
	else:
		return render_template('delete_item.html', restaurant_id = restaurant_id, menu_id = menu_id, item = item)

# run the server only if it's not an imported module
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
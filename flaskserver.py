from flask import Flask
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
@app.route('/restaurant')
def list():
	output = '<h1>Restaurants and Menus</h1>'
	restaurant = s.query(Restaurant).all()
	for res in restaurant:
		output += '<p><b>%s</b></p>' %res.name
		output += '<a href="restaurant/%s">Menu</a>' %res.id
	return output

@app.route('/restaurant/<int:restaurant_id>/')
def menus(restaurant_id):
	restaurant = s.query(Restaurant).filter_by(id = restaurant_id).one()
	output = '<h1>%s</h1>' %restaurant.name
	list_item = s.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	for item in list_item:
		output += '<p><b>' + item.name + '</b></p>'
		output += '<p>' + item.description + '</p>'
		output += '<p>' + item.price + '</p>'
	return output

@app.route('/restaurant/<int:restaurant_id>/new_item/')
def new_item(restaurant_id):

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit_item/')

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete_item/')
# run the server only if it's not an imported module
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
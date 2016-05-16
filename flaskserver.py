from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from flask import Flask, render_template, url_for, jsonify, request, redirect, flash
from flask import session as login_session

from db import engine, Base, Restaurant, MenuItem
import random, string
# needed libraries for authentication and security
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import make_response
# declare client id by referencing json file
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

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
@app.route('/login/')
def show_login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
	# validate it's the user connecting
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	code = request.data
	try:
		# exchange auth code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade auth code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# check if the token is valid
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response
	# verify the access is given
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps('Token user ID doesn\'t match given ID.'))
		response.headers['Content-Type'] = 'application/json'
		return response
	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps('Token client ID doesn\'t match given ID.'))
		print 'Token ID does not match app ID.'
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = login_session.get('access_token')
	stored_gp_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gp_id:
		response = make_response(json.dumps('Current user already logged in.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	return output

@app.route('/gdisconnect')
def gdisconnect():
	if 'username' not in login_session:
		flash('Please login to continue.')
		return redirect('/login/')
	access_token = login_session['access_token']
	if access_token is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	if result['status'] == '200':
		del login_session['access_token']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		flash("You have successfully logged out!")
		return redirect(url_for('show_login'))
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		flash('There was a problem logging out, try again later.')
		return redirect(url_for('list'))

@app.route('/restaurant/')
def list():
	if 'username' not in login_session:
		flash('Please login to continue.')
		return redirect('/login/')
	restaurant_list = restaurants()
	return render_template('restaurant_list.html', restaurant_list = restaurant_list)

# route to the restaurants menu if the link is clicked
@app.route('/restaurant/<restaurant_id>/')
def menus(restaurant_id):
	if 'username' not in login_session:
		flash('Please login to continue.')
		return redirect('/login/')
	rstr = restaurant(restaurant_id)
	item_list = menu_items(restaurant_id)
	return render_template('restaurant_menu.html', restaurant = rstr, menu = item_list)

@app.route('/restaurant/add_restaurant/', methods=['GET', 'POST'])
def add_restaurant():
	if 'username' not in login_session:
		flash('Please login to continue.')
		return redirect('/login/')
	if request.method == 'POST':
		new_rstr = Restaurant(name = request.form['name'])
		s.add(new_rstr)
		s.commit()
		return redirect(url_for('list'))
	else:
		return render_template('add_restaurant.html')

# form to edit a rstr
@app.route('/restaurant/<int:restaurant_id>/edit_restaurant/', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
	if 'username' not in login_session:
		flash('Please login to continue.')
		return redirect('/login/')
	rstr = restaurant(restaurant_id)
	if request.method == 'POST':
		if request.form['name']:
			rstr.name = request.form['name']
		s.add(rstr)
		s.commit()
		return redirect(url_for('list'))
	else:
		return render_template('edit_restaurant.html', restaurant_id = restaurant_id, rstr = rstr)

# route to delete a rstr
@app.route('/restaurant/<int:restaurant_id>/delete_restaurant/', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
	if 'username' not in login_session:
		flash('Please login to continue.')
		return redirect('/login/')
	rstr = restaurant(restaurant_id)
	item_list = menu_items(restaurant_id)
	if request.method == 'POST':
		for item in item_list:
			s.delete(item)
		s.delete(rstr)
		s.commit()
		return redirect(url_for('list'))
	else:
		return render_template('delete_restaurant.html', restaurant_id = restaurant_id, rstr = rstr)

# form to add a restaurant item to the menu
@app.route('/restaurant/<int:restaurant_id>/new_item/', methods=['GET', 'POST'])
def add_item(restaurant_id):
	if 'username' not in login_session:
		flash('Please login to continue.')
		return redirect('/login/')
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
	if 'username' not in login_session:
		flash('Please login to continue.')
		return redirect('/login/')
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
	if 'username' not in login_session:
		flash('Please login to continue.')
		return redirect('/login/')
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

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi, datetime
from menu_database import engine, Base, Restaurant, MenuItem

# there will be two main sections Handler Class and Main method
Base.metadata.bind  = engine
DBSession = sessionmaker(bind = engine)
s = DBSession()
# this is the handler Class
class WebServerHandler(BaseHTTPRequestHandler):
	# this method handles all get requests the server recieves
	def do_GET(self):
		# set response to handle specific url
		try:
			if self.path.endswith("/restaurant"):
				# send response
				self.send_response(200)
				# tells client that the response will be in html
				self.send_header("Content-type", "text/html")
				self.end_headers()
				restaurant_list = ''
				# code to grab restaurant data from the db and post it to a list
				restaurants = s.query(Restaurant.name, Restaurant.id).all()
				for res in restaurants:
					restaurant_list += '<p><b>%s</b></p>' %res.name
					restaurant_list += '<a href="restaurant/%s/edit">Edit</a>' %res.id
					restaurant_list += '</br><a href="restaurant/%s/delete">Delete</a></br>' %res.id
				# output to send back to client
				message = "<html><body>"
				message += "<h1>Restaurants in Database</h1>"
				message += '%s' % restaurant_list
				message += '</br><a href="restaurant/new">Add a new Restaurant</a>'
				message += "</body></html>"
				self.wfile.write(message)
				return
			if self.path.endswith('/restaurant/new'):
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				message = '<html><body>'
				message += '<h1>Add a New Restaurant</h2>'
				message += '<form method="Post" enctype="multipart/form-data" action="/restaurant/new"><p>Restaurant Name</p>'
				message += '<input name="new_restaurant" type="text"><input type="submit" value="Submit"></form>'
				message += '</body></html>'
				self.wfile.write(message)
				return
			if self.path.endswith('/edit'):
				restaurant_id = self.path.split('/')[2]
				restaurant = s.query(Restaurant).filter_by(id = restaurant_id).one()
				if restaurant != []:
					self.send_response(200)
					self.send_header("Content-type", "text/html")
					self.end_headers()
					message = '<html><body>'
					message += '<h1>Edit %s</h1>' %restaurant.name
					message += '<form method="Post" enctype="multipart/form-data" action="%s/edit"><p>Restaurant Name</p>'  %restaurant_id
					message += '<input name="new_name" type="text"><input type="submit" value="Rename"></form>'
					message += '</body></html>'
					self.wfile.write(message)
					return
			if self.path.endswith('/delete'):
				restaurant_id = self.path.split('/')[2]
				restaurant = s.query(Restaurant).filter_by(id = restaurant_id).one()
				if restaurant != []:				
					self.send_response(200)
					self.send_header("Content-type", "text/html")
					self.end_headers()
					message = "<html><body>"
					message += "<h1>Are you sure you want to delete %s?</h1>" %restaurant.name
					message += "<form method='POST' enctype='multipart/form-data' action='%s/delete'><input name='yes' type='submit' value='Yes'>" %restaurant_id
					message += '</br><a href="/restaurant">Back to List</a>'
					message += "</body></html>"
					self.wfile.write(message)
					return
	# exception if try fails
		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)

	def do_POST(self):
		try:
			# parses an html form header into a value and parameters
			if self.path.endswith("/restaurant/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				# check to see if this is form data being recieved
				if ctype == "multipart/form-data":
					# collect all the fields in a form
					fields = cgi.parse_multipart(self.rfile, pdict)
					# get the value of a field, or set of fields and store in an array
					messagecontent = fields.get("new_restaurant")
				new_name = messagecontent[0]
				new_rest = Restaurant(name = new_name)
				s.add(new_rest)
				s.commit()
				
				self.send_response(301)
				self.send_header("Content-type", "text/html")
				self.send_header('Location', '/restaurant')
				self.end_headers()
				return
			if self.path.endswith('/edit'):
				restaurant_id = self.path.split('/')[2]
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == "multipart/form-data":
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get("new_name")
				restaurant = s.query(Restaurant).filter_by(id = restaurant_id).one()
				if restaurant != []:
					restaurant.name = messagecontent[0]
					s.add(restaurant)
					s.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurant')
					self.end_headers()
			if self.path.endswith('/delete'):
				restaurant_id = self.path.split('/')[2]
				restaurant = s.query(Restaurant).filter_by(id = restaurant_id).one()
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == "multipart/form":
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('yes')
				if restaurant != []:
					s.delete(restaurant)
					s.commit()
					self.send_response(201)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					message = "<html><body>"
					message += "<h1>%s has been deleted</h1>" %restaurant.name
					message += '</br><a href="/restaurant">Back to List</a>'
					message += "</body></html>"
					self.wfile.write(message)
		except:
			print ("Failed to post for some reason or another.")

# this is the main method
def main():
	# try this method
	try:
		#define port to use for serer
		port = 8080
		# server_address is tuple that contains host and port number for the server, then specify handler name
		server = HTTPServer(("",port), WebServerHandler)
		print ("Web server running on port %s" % port)
		# keep the server running until exception is made
		server.serve_forever()

	# break the code on this event happening
	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		# close the server
		server.socket.close()

# run the main method immediatley when script is executed
if __name__ == "__main__":
	main()
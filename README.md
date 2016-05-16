# MenuFlask
Restaurant Menu created using Flask Python library, for the Udacity Fullstack Developer course

To get this to work will you have to go to console.developers.google.com to create a client id and a client_secrets.json

At the page go to credentials, create one naming it whatever you like, click on the newly created Oauth2 Client ID to see all the information.

In the Authorized redirects URI add in http://localhost:5000/login/, http://localhost:5000/gconnect/, and http://localhost:5000/restaurant/

The default port the site runs through is 5000, you can change that in flaskserver.py, just make sure to change the redirect uris and download a new client_secrets.json.

When the URI's are click the Download JSON and rename the file, client_secrets.json and put it into the root MenuFlask folder.

After that go to login.html in the template folders and copy in the client ID as the variaable for the data-clientid key in the signin div.

Once that is done run the flaskserver.py using python in a terminal and the website will be running with complete database functionality and googleplus authentication.

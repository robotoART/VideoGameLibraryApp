from flask import (
  Flask, render_template, request, redirect, jsonify,
  url_for, flash
  )

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, GameMachine, VideoGame, User

from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
  open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Video Game Library Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///videogamelibrary.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create a state token to prevent request forgery,
# and store it in the session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32)
        )
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
          json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid
    access_token = credentials.access_token
    url = (
      'https://www.googleapis.com/oauth2/v1/'
      'tokeninfo?access_token=%s' % access_token
      )
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify access token is used for intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
          json.dumps("Token's User ID doesn't match given User ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
          json.dumps("Token's client ID doesn't match app's."), 401)
        print "Token's client ID doesn't match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user is already logged in
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
          json.dumps('Current user is already connected.'), 200
          )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    # data = json.loads(answer.text) # Alternative
    data = answer.json()

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]
    login_session['provider'] = 'google'

    # Check if user exists, if user doesn't exist add it
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
        login_session['user_id'] = user_id

        output = ''
        output += '<h1>Welcome, '
        if login_session['username'] != '':
            output += login_session['username']
        else:
            output += 'Anonymous User'

        output += '!</h1>'
        output += '<img src="'
        output += login_session['picture']
        output += ' " style = "width: 300px; height: 300px;' \
            'border-radius: 150px;-webkit-border-radius: 150px;' \
            '-moz-border-radius: 150px;">'
        flash("you are now logged in as %s" % login_session['username'])
        return output


# Disconnect - Revoke a current user's token & reset their login_session.
@app.route("/gdisconnect")
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Credentials is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401
            )
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access_token is %s', access_token
    print 'User name is: '
    print login_session['username']
    # Execute HTTP GET request to revoke current token.
    # access_token = credentials.access_token
    url = 'https://accounts.google.com/' \
          'o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # In case the given token was invalid.
        response = make_response(
                    json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Game Machine Information
@app.route('/gamemachine/<int:game_machine_id>/JSON')
def videogameLibraryJSON(game_machine_id):
    game_machine = session.query(
      GameMachine).filter_by(id=game_machine_id).one()
    items = (session.query(VideoGame).filter_by(
      game_machine_id=game_machine_id).order_by("name").all()
    )
    return jsonify(ConsoleGames=[i.serialize for i in items])


@app.route(
  '/gamemachine/<int:game_machine_id>/videogame/<int:video_game_id>/JSON'
  )
def videoGameJSON(game_machine_id, video_game_id):
    Video_Game = session.query(VideoGame).filter_by(id=video_game_id).one()
    return jsonify(VideoGame=Video_Game.serialize)


@app.route('/gamemachine/JSON')
def gameMachinesJSON():
    GameMachines = session.query(GameMachine).order_by("manufacturer").all()
    return jsonify(GameMachines=[g.serialize for g in GameMachines])
    # return jsonify(vglibs = vglibs.serialize)


# Show all game machines
@app.route('/')
@app.route('/gamemachine/')
def showGameMachines():
    users = session.query(User).all()
    game_machines = session.query(GameMachine).order_by(asc(GameMachine.name))
    # creator = getUserInfo(GameMachine.user_id)
    if 'username' not in login_session:
        return render_template('publicgamemachines.html',
                               game_machines=game_machines, users=users)
    else:
        return render_template('gamemachines.html',
                               game_machines=game_machines,
                               users=users)


# Create a new game machine
@app.route('/gamemachine/new/', methods=['GET', 'POST'])
def newGameMachine():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGameMachine = GameMachine(
                                manufacturer=request.form['manufacturer'],
                                name=request.form['name'],
                                user_id=login_session['user_id'])
        session.add(newGameMachine)
        flash('New Console %s Successfully added' % newGameMachine.name)
        session.commit()
        return redirect(url_for('showGameMachines'))
    else:
        return render_template('newGameMachine.html')


# Edit a game machine
@app.route(
  '/gamemachine/<int:game_machine_id>/edit/', methods=['GET', 'POST']
  )
def editGameMachine(game_machine_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedGameMachine = session.query(
                            GameMachine).filter_by(id=game_machine_id).one()
    if editedGameMachine.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
            "{alert('You are not authorized to edit this console.');}" \
            "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedGameMachine.name = request.form['name']
            editedGameMachine.manufacturer = request.form['manufacturer']
            flash('Console Successfully Edited %s' % editedGameMachine.name)
            return redirect(url_for('showGameMachines'))
    else:
        return render_template('editGameMachine.html',
                               game_machine=editedGameMachine)


# Delete a game machine
@app.route('/gamemachine/<int:game_machine_id>/delete/',
           methods=['GET', 'POST'])
def deleteGameMachine(game_machine_id):
    if 'username' not in login_session:
        return redirect('/login')
    gamemachineToDelete = session.query(GameMachine).filter_by(
      id=game_machine_id).one()
    if gamemachineToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
          "{alert('You are not authorized to delete this console.');}" \
          "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(gamemachineToDelete)
        flash('%s Successfully Deleted' % gamemachineToDelete.name)
        session.commit()
        return redirect(
          url_for('showGameMachines', game_machine_id=game_machine_id)
          )
    else:
        return render_template('deleteGameMachine.html',
                               game_machine=gamemachineToDelete)


# Show a game machine game
@app.route('/gamemachine/<int:game_machine_id>/')
@app.route('/gamemachine/<int:game_machine_id>/games/')
def showVGLib(game_machine_id):
    game_machine = session.query(
      GameMachine).filter_by(id=game_machine_id).one()
    creator = getUserInfo(game_machine.user_id)
    items = session.query(
                          VideoGame).filter_by(
                          game_machine_id=game_machine_id).order_by(
                          "name").all()
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('publicvglib.html', items=items,
                               game_machine=game_machine,
                               creator=creator)
    else:
        return render_template('vglib.html', items=items,
                               game_machine=game_machine, creator=creator)


# Create a new video game item
@app.route(
  '/gamemachine/<int:game_machine_id>/videogame/new/', methods=['GET', 'POST']
  )
def newVideoGame(game_machine_id):
    if 'username' not in login_session:
        return redirect('/login')
    game_machine = session.query(
      GameMachine).filter_by(id=game_machine_id).one()
    if request.method == 'POST':
        newItem = VideoGame(name=request.form['name'],
                            description=request.form['description'],
                            game_machine=game_machine,
                            user_id=game_machine.user_id)
        session.add(newItem)
        session.commit()
        flash('New Video Game %s Successfully Added' % (newItem.name))
        return redirect(url_for('showVGLib', game_machine=game_machine,
                                game_machine_id=game_machine.id))
    else:
        return render_template('newvglibitem.html',
                               game_machine=game_machine)


# Edit a video game item
@app.route(
  '/gamemachine/<int:game_machine_id>/videogame/<int:video_game_id>/edit',
  methods=['GET', 'POST']
  )
def editVideoGame(game_machine_id, video_game_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(VideoGame).filter_by(id=video_game_id).one()
    game_machine = session.query(
      GameMachine).filter_by(id=game_machine_id).one()
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
          "{alert('You are not authorized to edit this video game.');}" \
          "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Video Game Successfully Edited')
        return redirect(url_for('showVGLib',
                                game_machine_id=game_machine_id)
                        )
    else:
        return render_template('editvglibitem.html',
                               game_machine_id=game_machine_id,
                               video_game_id=video_game_id,
                               item=editedItem)


# Delete a video game item
@app.route(
  '/gamemachine/<int:game_machine_id>/videogame/<int:video_game_id>/delete',
  methods=['GET', 'POST']
  )
def deleteVideoGame(game_machine_id, video_game_id):
    if 'username' not in login_session:
        return redirect('/login')
    game_machine = session.query(
      GameMachine).filter_by(id=game_machine_id).one()
    itemToDelete = session.query(VideoGame).filter_by(id=video_game_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
          "{alert('You are not authorized to delete this video game.');}" \
          "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Video Game Successfully Deleted')
        return redirect(url_for('showVGLib',
                                game_machine_id=game_machine_id))
    else:
        return render_template('deletevglibitem.html', item=itemToDelete)


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        return redirect(url_for('showGameMachines'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showGameMachines'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base, AeroplaneName, ModelName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///aeroplanes.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Aeroplanes"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
mds_cat = session.query(AeroplaneName).all()


# login
@app.route('/login')
def showLogin():
    ''' it used for to enter into the login page'''
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    mds_cat = session.query(AeroplaneName).all()
    mdes = session.query(ModelName).all()
    return render_template('login.html',
                           STATE=state, mds_cat=mds_cat, mdes=mdes)
    # return render_template('myhome.html', STATE=state
    # mds_cat=mds_cat,mdes=mdes)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    ''' it is used to connect through gmailid'''
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
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

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
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

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(User1)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


# Home


@app.route('/')
@app.route('/home')
def home():
    mds_cat = session.query(AeroplaneName).all()
    return render_template('myhome.html', mds_cat=mds_cat)

# aeroplane hub for admins


@app.route('/AeroplaneHub')
def AeroplaneHub():
    """ here it shows aeroplanes myhome file"""
    try:
        if login_session['username']:
            name = login_session['username']
            mds_cat = session.query(AeroplaneName).all()
            mds = session.query(AeroplaneName).all()
            mdes = session.query(ModelName).all()
            return render_template('myhome.html', mds_cat=mds_cat,
                                   mds=mds, mdes=mdes, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing models


@app.route('/AeroplaneHub/<int:mdid>/AllAeroplanes')
def showAeroplanes(mdid):
    ''' here it is used to show aeroplanes '''
    mds_cat = session.query(AeroplaneName).all()
    mds = session.query(AeroplaneName).filter_by(id=mdid).one()
    mdes = session.query(ModelName).filter_by(aeroplanenameid=mdid).all()
    try:
        if login_session['username']:
            ''' linking to the showAeroplanes.html to display aeroplanes '''
            return render_template('showAeroplanes.html', mds_cat=mds_cat,
                                   mds=mds, mdes=mdes,
                                   uname=login_session['username'])
    except:
        return render_template('showAeroplanes.html',
                               mds_cat=mds_cat, mds=mds, mdes=mdes)

#####
# Add New model


@app.route('/AeroplaneHub/addAeroplaneName', methods=['POST', 'GET'])
def addAeroplaneName():
    ''' if you want to add new aeroplane name '''
    if "username" not in login_session:
        flash("Please login first")
        return redirect(url_for("showLogin"))
    if request.method == 'POST':
        aeroplanename = AeroplaneName(name=request.form['name'],
                                      user_id=login_session['user_id'])
        session.add(aeroplanename)
        session.commit()
        return redirect(url_for('AeroplaneHub'))
    else:
        return render_template('addAeroplaneName.html', mds_cat=mds_cat)

# Edit Aeroplane name


@app.route('/AeroplaneHub/<int:mdid>/edit', methods=['POST', 'GET'])
def editAeroplaneName(mdid):
    ''' if you want to edit the aeroplanename'''
    editAeroplaneName = session.query(AeroplaneName).filter_by(id=mdid).one()
    creator = getUserInfo(editAeroplaneName.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this AeroplaneName."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('AeroplaneHub'))
    if request.method == "POST":
        if request.form['name']:
            editAeroplaneName.name = request.form['name']
        session.add(editAeroplaneName)
        session.commit()
        flash("editAeroplaneName Edited Successfully")
        return redirect(url_for('AeroplaneHub'))
    else:
        # mds_cat is global variable we can them in entire application
        return render_template('editAeroplaneName.html',
                               md=editAeroplaneName, mds_cat=mds_cat)


# Delete AeroplaneName


@app.route('/AeroplaneHub/<int:mdid>/delete', methods=['POST', 'GET'])
def deleteAeroplaneName(mdid):
    ''' if you want to delete aeroplane name'''
    md = session.query(AeroplaneName).filter_by(id=mdid).one()
    creator = getUserInfo(md.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Aeroplane name."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('AeroplaneHub'))
    if request.method == "POST":
        session.delete(md)
        session.commit()
        flash("AeroplaneName Deleted Successfully")
        return redirect(url_for('AeroplaneHub'))
    else:
        return render_template('deleteAeroplaneName.html',
                               md=md, mds_cat=mds_cat)

######
# Add New Aeroplane Name Details


@app.route(
          '/AeroplaneHub/addAeroplaneName/'
          'addAeroplaneModelDetails/<string:mdname>/add',
          methods=['GET', 'POST'])
def addAeroplaneDetails(mdname):
    ''' if you want to add aeroplane model details'''
    mds = session.query(AeroplaneName).filter_by(name=mdname).one()
    # See if the logged in user is not the owner of Aeroplane
    creator = getUserInfo(mds.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != Model owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new Model edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showAeroplanes', mdid=mds.id))
    if request.method == 'POST':
        name = request.form['name']
        capacity = request.form['capacity']
        topspeed = request.form['topspeed']
        rating = request.form['rating']
        service = request.form['service']
        modeldetails = ModelName(name=name, capacity=capacity,
                                 topspeed=topspeed,
                                 rating=rating,
                                 service=service,
                                 date=datetime.datetime.now(),
                                 aeroplanenameid=mds.id,
                                 user_id=login_session['user_id'])
        session.add(modeldetails)
        session.commit()
        return redirect(url_for('showAeroplanes', mdid=mds.id))
    else:
        return render_template('addAeroplaneModelDetails.html',
                               mdname=mds.name, mds_cat=mds_cat)


# Edit Aeroplane Model details


@app.route('/AeroplaneHub/<int:mdid>/<string:mdename>/edit',
           methods=['GET', 'POST'])
def editAeroplaneModel(mdid, mdename):
    ''' if you want to edit the aeroplane model details'''
    md = session.query(AeroplaneName).filter_by(id=mdid).one()
    modeldetails = session.query(ModelName).filter_by(name=mdename).one()
    # See if the logged in user is not the owner of Aeroplane
    creator = getUserInfo(md.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != model owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this Model edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showAeroplanes', mdid=md.id))
    # POST methods
    if request.method == 'POST':
        modeldetails.name = request.form['name']
        modeldetails.capacity = request.form['capacity']
        modeldetails.topspeed = request.form['topspeed']
        modeldetails.rating = request.form['rating']
        modeldetails.service = request.form['service']
        modeldetails.date = datetime.datetime.now()
        session.add(modeldetails)
        session.commit()
        flash("Model Edited Successfully")
        return redirect(url_for('showAeroplanes', mdid=mdid))
    else:
        return render_template('editAeroplaneModel.html',
                               mdid=mdid, modeldetails=modeldetails,
                               mds_cat=mds_cat)


# Delte Aeroplane model


@app.route('/AeroplaneHub/<int:mdid>/<string:mdename>/delete',
           methods=['GET', 'POST'])
def deleteAeroplaneModel(mdid, mdename):
    ''' if you want to delete an aeroplane model'''
    md = session.query(AeroplaneName).filter_by(id=mdid).one()
    modeldetails = session.query(ModelName).filter_by(name=mdename).one()
    # See if the logged in user is not the owner of Aeroplane
    creator = getUserInfo(md.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != model owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this aeroplane edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showAeroplanes', mdid=md.id))
    if request.method == "POST":
        session.delete(modeldetails)
        session.commit()
        flash("Deleted Aeroplane model Successfully")
        return redirect(url_for('showAeroplanes', mdid=mdid))
    else:
        return render_template('deleteAeroplaneModel.html',
                               mdid=mdid, modeldetails=modeldetails,
                               mds_cat=mds_cat)


# Logout from current user


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type':
                           'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
            'Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Json


@app.route('/AeroplaneHub/JSON')
def allAeroplanesJSON():
    aeroplanenames = session.query(AeroplaneName).all()
    category_dict = [c.serialize for c in aeroplanenames]
    for c in range(len(category_dict)):
        aeroplanemodelnames = [i.serialize for i in session.query(
                 ModelName).filter_by(
                     aeroplanenameid=category_dict[c]["id"]).all()]
        if aeroplanemodelnames:
            category_dict[c]["aeroplanes"] = aeroplanemodelnames
    return jsonify(AeroplaneName=category_dict)


@app.route('/AeroplaneHub/aeroplaneName/JSON')
def categoriesJSON():
    aeroplanes = session.query(AeroplaneName).all()
    return jsonify(aeroplaneName=[c.serialize for c in aeroplanes])


@app.route('/AeroplaneHub/aeroplanes/JSON')
def modelsJSON():
    models = session.query(ModelName).all()
    return jsonify(aeroplanes=[i.serialize for i in models])


@app.route('/AeroplaneHub/<path:aeroplane_name>/aeroplanes/JSON')
def categoryModelsJSON(aeroplane_name):
    aeroplaneName = session.query(
        AeroplaneName).filter_by(name=aeroplane_name).one()
    aeroplanes = session.query(
        ModelName).filter_by(aeroplanename=aeroplaneName).all()
    return jsonify(aeroplaneName=[i.serialize for i in aeroplanes])


@app.route('/AeroplaneHub/<path:aeroplane_name>'
           '/<path:aeroplanemodel_name>/JSON')
def modelJSON(aeroplane_name, aeroplanemodel_name):
    aeroplaneName = session.query(
        AeroplaneName).filter_by(name=aeroplane_name).one()
    aeroplaneModelName = session.query(
        ModelName).filter_by(
            name=aeroplanemodel_name, aeroplanename=aeroplaneName).one()
    return jsonify(aeroplaneModelName=[aeroplaneModelName.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

import colander
import deform.widget
from deform import Form

from pyramid.httpexceptions import HTTPFound

from .models import (
    DBSession,
    User,
    )


class SignupForm(colander.MappingSchema):
    firstname = colander.SchemaNode(
        colander.String(),
        title='First Name'
        )
    lastname = colander.SchemaNode(
        colander.String(),
        title='Last Name')
    emailadd = colander.SchemaNode(
        colander.String(),
        title='Email Address'
        )
    username = colander.SchemaNode(
        colander.String(),
        title='Username'
        )
    password = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.CheckedPasswordWidget(size=20),
        validator=colander.Length(min=8)
        )

class LoginForm(colander.MappingSchema):
    username = colander.SchemaNode(
        colander.String(),
        title='Username')
    password = colander.SchemaNode(
        colander.String(),
        title='Password'
        )

class UserAuthViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='templates/home.jinja2')
    def my_view(self):
        return {'title': 'Home'}

    @view_config(route_name='signup', renderer='templates/signup.jinja2')
    def signupView(self):
        schema = SignupForm()
        signupForm = deform.Form(schema, buttons=('submit',))

        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = signupForm.validate(controls)
                print appstruct
            except:
                return{'title': 'Sign Up', 'form': signupForm}

            username = appstruct['username']
            password = appstruct['password']
            firstname = appstruct['firstname']
            lastname = appstruct['lastname']
            emailadd = appstruct['emailadd']

            session = DBSession()
            newestID = session.query(User).order_by(User.id.desc()).first().id + 1
            newusr = User(id=newestID, username=username, password=password, firstname=firstname, lastname=lastname, email=emailadd)
            
            # Validate that user is uniquie as determined by criteria
            # If newusr is valid, add to db
            session.add(newusr)

            return HTTPFound(location = self.request.route_url('viewAllUsers'))
            
        return{'title': 'Sign Up', 'form': signupForm}


    @view_config(route_name='login', renderer='templates/login.jinja2')
    def loginView(self):
        schema = LoginForm()
        loginForm = deform.Form(schema, buttons=('submit',))

        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = loginForm.validate(controls)
            except:
                return {'title': 'Login', 'form': loginForm}
            
            usrname = appstruct['username']
            pswrd = appstruct['password']

            # check to see if user and password exist and match, if so, then give them some credentials

        return {'title': 'Login', 'form': loginForm}


    @view_config(route_name='viewAllUsers', renderer='templates/allusers.jinja2')
    def allUsersView(self):
        usrs = []
        session = DBSession()
        for instance in session.query(User).order_by(User.id):
            print instance.id, instance.username, instance.password
            usrs.append(str(instance.id) + ' ' + instance.username + ' ' + instance.password + ' ' + instance.firstname + ' ' + instance.lastname + ' ' + instance.email)

        return{'title': 'View All Users', 'users': usrs}

    @view_config(route_name='secret', renderer='templates/secret.jinja2', permission='god')
    def secretView(self):
        return {'title': 'Secret Page'}

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_UserAuth_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""


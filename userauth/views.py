from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

import colander
import deform.widget
from deform import Form

from pyramid.httpexceptions import HTTPFound

from pyramid.security import (
    authenticated_userid,
    remember,
    forget
    )

from .models import (
    DBSession,
    User,
    hash_password
    )


class SignupForm(colander.MappingSchema):
    choices = (
        ('viewer', 'Viewer'),
        ('fool', 'Fool'),
        ('king', 'King'),
        ('god', 'God')
        )
    firstname = colander.SchemaNode(
        colander.String(),
        title='First Name'
        )
    lastname = colander.SchemaNode(
        colander.String(),
        title='Last Name')
    emailaddress = colander.SchemaNode(
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
    credentials = colander.SchemaNode(
                colander.String(),
                validator=colander.OneOf([x[0] for x in choices]),
                widget=deform.widget.RadioChoiceWidget(values=choices),
                title='Choose your credentials',
                description='Select a credentials')

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
    def homeView(self):
        print authenticated_userid(self.request)
        return {'title': 'Home', 'userid': authenticated_userid(self.request)}

    @view_config(route_name='signup', renderer='templates/signup.jinja2')
    def signupView(self):
        schema = SignupForm()
        signupForm = deform.Form(schema, buttons=('submit',))

        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = signupForm.validate(controls)
            except:
                return{'title': 'Sign Up', 'form': signupForm}

            username = appstruct['username']
            session = DBSession()
            if session.query(User).filter(User.username == username).first():
                return{'title': 'Sign Up', 'form': signupForm, 'message': 'Username already taken'}

            newestID = session.query(User).order_by(User.id.desc()).first().id + 1
            newusr = User(
                id       =newestID,
                username = username,
                password = appstruct['password'],
                firstname= appstruct['firstname'],
                lastname = appstruct['lastname'],
                email    = appstruct['emailaddress'],
                credentials = appstruct['credentials']
            )

            headers = remember(self.request, username)
            session.add(newusr)
            return HTTPFound(location = self.request.route_url('viewAllUsers'), headers=headers)
            
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
                return {'title': 'Login', 'form': loginForm, 'message': 'Login Unsuccessful'}
            
            username = appstruct['username']
            password = appstruct['password']
            
            if User.check_password(username, password):
                headers = remember(self.request, username)
                return HTTPFound(location=self.request.route_url('home'), headers=headers)
            else:
                return {'title': 'Login', 'userid': authenticated_userid(self.request), 'form': loginForm, 'message': 'Login Unsuccessful'}                

        return {'title': 'Login', 'form': loginForm}

    @view_config(route_name='logout', renderer='templates/logout.jinja2')
    def logoutView(self):
        headers = forget(self.request)
        return HTTPFound(location=self.request.route_url('home'), headers=headers)


    @view_config(route_name='viewAllUsers', renderer='templates/allusers.jinja2')
    def allUsersView(self):
        usrs = []
        session = DBSession()
        for instance in session.query(User).order_by(User.id):
            print instance.id, instance.username, instance.password
            usrs.append(str(instance.id) + ' ' + instance.username + ' ' + instance.password + ' ' + instance.firstname + ' ' + instance.lastname + ' ' + instance.email + ' ' + instance.credentials)
        return{'title': 'View All Users', 'userid': authenticated_userid(self.request), 'users': usrs}


    @view_config(route_name='fool', renderer='templates/fool.jinja2', permission='fool')
    def foolsView(self):
        return {'title': "Fool's Page", 'userid': authenticated_userid(self.request)}


    @view_config(route_name='king', renderer='templates/king.jinja2', permission='king')
    def kingsView(self):
        return {'title': "King's Page", 'userid': authenticated_userid(self.request)}


    @view_config(route_name='god', renderer='templates/god.jinja2', permission='god')
    def godsView(self):
        return {'title': "God's Page", 'userid': authenticated_userid(self.request)}

    @view_config(route_name='settings', renderer='settings.jinja2', permission='settingsConfiguration')
    def settingsView(self):
        return {}



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


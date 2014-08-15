from .models import (
    DBSession,
    User
    )

GROUPS = { 'fool': ['group:fool'],
	'king': ['group:king', 'group:fool'],
	'god': ['group:god', 'group:king', 'group:fool']
}

def groupfinder(userid, request):
	user = DBSession().query(User).filter(User.username == userid).first()
	cred = user.credentials
	return GROUPS.get(cred, [])
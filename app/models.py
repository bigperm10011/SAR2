from app import db
from datetime import datetime
from flask_login import UserMixin
from app import login

class Leaver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    status = db.Column(db.String(50), default="Lost")
    prole = db.Column(db.String(100))
    pfirm = db.Column(db.String(100))
    lrole = db.Column(db.String(100))
    lfirm = db.Column(db.String(100))
    llink = db.Column(db.String(100))
    llocation = db.Column(db.String(100))
    team = db.Column(db.String(10))
    repcode = db.Column(db.String(10), db.ForeignKey('srep.repcode'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    suspects = db.relationship('Suspect', backref='leaver', lazy='dynamic', cascade="all, delete, delete-orphan")
    updated = db.Column(db.String(10), default='No')
    rescued = db.relationship('Rescue', backref='leaver', uselist=False)
    proscreatedt = db.Column(db.DateTime)
    track_name = db.Column(db.String(100))
    track_detail = db.Column(db.String(1000))
    track_lst_update = db.Column(db.DateTime)

    def __repr__(self):
        return '<Leaver {}>'.format(self.name)


class Srep(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    repemail = db.Column(db.String(100))
    repcode = db.Column(db.String(10), unique=True)
    teamcode = db.Column(db.String(10))
    leavers = db.relationship('Leaver', backref='rep', lazy='dynamic')
    rescues = db.relationship('Rescue', backref='rrep', lazy='dynamic')

    def __repr__(self):
        return '<Sales Rep {}>'.format(self.firstname + " " + self.lastname)

class Suspect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    leaverid = db.Column(db.Integer, db.ForeignKey('leaver.id'))
    name = db.Column(db.String(50))
    include = db.Column(db.String(50), default="Yes")
    role = db.Column(db.String(100))
    firm = db.Column(db.String(100))
    location = db.Column(db.String(75))
    link = db.Column(db.String(100), unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Suspect {}>'.format(self.name)

class Rescue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(100))
    firm = db.Column(db.String(100))
    link = db.Column(db.String(100))
    location = db.Column(db.String(100))
    team = db.Column(db.String(10))
    repcode = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    srepid = db.Column(db.Integer, db.ForeignKey('srep.id'))
    leaverid = db.Column(db.Integer(), db.ForeignKey('leaver.id'))

    def __repr__(self):
        return '<Rescue {}>'.format(self.name)

@login.user_loader
def load_user(id):
    return Srep.query.get(int(id))



###################### DB Commands ######################
# flask db init
# flask db migrate -m "sar2 table"
# flask db upgrade

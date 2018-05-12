from app import app
from flask import render_template, flash, redirect, url_for, request, json, Flask, jsonify, make_response
from app import db
from app.forms import LoginForm, RegistrationForm, BeginForm, RefreshForm, UpdateForm, TestForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Srep, Suspect, Leaver, Rescue
from werkzeug.urls import url_parse
from helpers import processfile, pd2class, scrapename, getchoices, check4chg, scrapename2, getupdates, threadscrape, turboscrape, getlinks, linkexists, processresults, fillselect, tablefill, comparefill, dblbackup, dbsbackup
from app.emails import find_notification, scraperesult
import datetime



@app.route('/')
@app.route('/index')
@login_required
def index():
    found = Leaver.query.filter_by(status='Placed', updated='No', repcode=current_user.repcode).all()
    return render_template('index.html', title='Home', found=found)

@app.route('/pros', methods=['GET', 'POST'])
@login_required
def pros():
    if request.method == 'POST':
        prosid = request.json['id']
        action = request.json['action']
        if action == 'update':
            iprosid = int(prosid)
            updated = Leaver.query.filter_by(id=iprosid).first()
            updated.updated = 'YES'
            db.session.commit()
            rep = Srep.query.filter_by(repcode=updated.repcode).first()
            l = Rescue(name=updated.name, role=updated.lrole, firm=updated.lfirm, link=updated.llink, location=updated.llocation, repcode=updated.repcode, team=updated.team, srepid=rep.id, leaverid=updated.id)
            db.session.add(l)
            db.session.delete(updated)
            db.session.commit()
            flash('Leaver Successfully Placed')
            return redirect(url_for('index'))

    return render_template('index.html', title='Home', found=found)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        f = request.files['file']
        rez = processfile(f)
        if rez == "Success":
            flash('Leavers Uploaded and Saved. Searching for Matches...')
            tlst = getlinks(current_user.repcode)
            rezzies = turboscrape(threadscrape, tlst)
            processresults(rezzies)
            flash('Potential Matches Added. Proceed to Step 2 to sort.')
        else:
            flash('ERROR: Try Again')

    return render_template('upload.html', title='Upload XLSX File')

################### TRACK Functionality ###################

@app.route('/track', methods=['GET', 'POST'])
@login_required
def track():

    return render_template('track.html', title='Update')

@app.route('/ndrop', methods=['GET', 'POST'])
@login_required
def ndrop():
    leavers = Leaver.query.filter_by(repcode=current_user.repcode, status='Lost').all()
    print(len(leavers))
    leaver_dict = fillselect(leavers)
    print(len(leaver_dict))
    return json.dumps(leaver_dict)

@app.route('/ajax', methods=['POST', 'GET'])
@login_required
def ajax():
    thing = request.args.get( 'data', '', type = int )
    parentdict = tablefill(thing)

    return json.dumps(parentdict)

@app.route('/followclick', methods=['GET', 'POST'])
@login_required
def followclick():
    ident = request.args.get( 'data', '', type = int )
    hit = Suspect.query.filter_by(id=ident).first()
    lhit = Leaver.query.filter_by(id=hit.leaverid).first()
    lhit.lrole = hit.role
    lhit.lfirm = hit.firm
    lhit.llink = hit.link
    lhit.llocation = hit.location
    lhit.status = 'Tracking'
    db.session.commit()
    flash('Tracking')

    leavers = Leaver.query.filter_by(repcode=current_user.repcode, status='Lost').all()
    leaver_dict = []
    for s in leavers:
        suspects = Suspect.query.filter_by(leaverid=s.id, include='Yes').all()
        num = len(suspects)
        dval = s.name + ' ' + '(' + str(num) + ')'
        s_dict = {'ident': s.id, 'name': dval}
        leaver_dict.append(s_dict)

    return json.dumps(leaver_dict)

@app.route('/pclick', methods=['GET', 'POST'])
@login_required
def pclick():
    ident = request.args.get( 'data', '', type = int )
    hit = Suspect.query.filter_by(id=ident).first()
    lhit = Leaver.query.filter_by(id=hit.leaverid).first()
    lhit.lrole = hit.role
    lhit.lfirm = hit.firm
    lhit.llink = hit.link
    lhit.llocation = hit.location
    lhit.status = 'Placed'
    db.session.commit()
    flash('Placed. Please Update Covering Rep.')

    leavers = Leaver.query.filter_by(repcode=current_user.repcode, status='Lost').all()
    leaver_dict = fillselect(leavers)
    return json.dumps(leaver_dict)

@app.route('/dclick', methods=['GET', 'POST'])
@login_required
def dclick():
    ident = request.args.get( 'data', '', type = int )
    suspect = Suspect.query.filter_by(id=ident).first()
    suspect.include = 'No'
    db.session.commit()
    flash('Removed. Choice will no longer appear in list.')

    lid = suspect.leaverid
    suspect_dict = []
    suspects = Suspect.query.filter_by(leaverid=lid, include='Yes').all()
    for s in suspects:
        s_dict = {'ident': s.id, 'name': s.name, 'link': s.link, 'role': s.role, 'firm':s.firm}
        suspect_dict.append(s_dict)
    return json.dumps(suspect_dict)





@app.route('/folla', methods=['GET','POST'])
@login_required
def folla():
    if request.method == 'POST':
        sid = request.json['data']
        action = request.json['action']
        no = 'No'
        if action == 'follow':
            print('section is:', action)
            hit = Suspect.query.filter_by(id=int(sid)).first()
            lhit = Leaver.query.filter_by(id=hit.leaverid).first()
            lhit.lrole = hit.role
            lhit.lfirm = hit.firm
            lhit.llink = hit.link
            lhit.llocation = hit.location
            lhit.status = 'Tracking'
            db.session.commit()
            flash('Tracking')
            return redirect(url_for('track'))
        elif action == 'place':
            print('section is:', action)
            hit = Suspect.query.filter_by(id=int(sid)).first()
            lhit = Leaver.query.filter_by(id=hit.leaverid).first()
            lhit.lrole = hit.role
            lhit.lfirm = hit.firm
            lhit.llink = hit.link
            lhit.llocation = hit.location
            lhit.status = 'Placed'
            db.session.commit()
            flash('Placed. Please Update Covering Rep.')
            return redirect(url_for('track'))
        elif action == 'remove':
            suspect = Suspect.query.filter_by(id=int(sid)).first()
            suspect.include = 'No'
            db.session.commit()
            flash('Removed. Choice will no longer appear in list.')
            return redirect(url_for('track'))

    return redirect(url_for('track'))
    #return redirect(url_for('test'))

#################### COMPARE FUNCTIONALITY #####################

@app.route('/check', methods=['GET','POST'])
@login_required
def check():

    return render_template('check.html', title='Compare')

@app.route('/comparedrop', methods=['GET', 'POST'])
@login_required
def comparedrop():
    leavers = Leaver.query.filter_by(repcode=current_user.repcode, status='Tracking').all()
    leaver_dict = []
    for l in leavers:
        ldict = {'ident': l.id, 'name': l.name}
        leaver_dict.append(ldict)
    return json.dumps(leaver_dict)

@app.route('/found', methods=['GET','POST'])
@login_required
def found():
    fid = request.args.get( 'id', '', type = int )
    firm = request.args.get('firm')
    location = firm = request.args.get('location')
    role = firm = request.args.get('role')
    find = Leaver.query.filter_by(id=fid).first()
    find.status = 'Placed'
    find.lrole = role
    find.llocation = location
    find.lfirm = firm
    db.session.commit()
    find_notification(find)

    leavers = Leaver.query.filter_by(repcode=current_user.repcode, status='Lost').all()
    leaver_dict = fillselect(leavers)

    return json.dumps(leaver_dict)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    loginform = LoginForm()
    if loginform.validate_on_submit():
        user = Srep.query.filter_by(repcode=loginform.repcode.data).first()
        if user is None:
            flash('Invalid username or teamcode')
            return redirect(url_for('login'))
        login_user(user, remember=loginform.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', loginform=loginform)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    regform = RegistrationForm()
    if regform.validate_on_submit():
        newsrep = Srep(name=regform.name.data, repemail=regform.email.data, repcode=regform.repcode.data, teamcode=regform.teamcode.data)
        db.session.add(newsrep)
        db.session.commit()
        flash('New Rep Successfully Registered')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', regform=regform)


@app.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    return render_template('test.html')

@app.route('/tstcompare', methods=['POST', 'GET'])
@login_required
def tstcompare():

    return render_template('tstcompare.html', title='Update')



@app.route('/cards', methods=['GET', 'POST'])
@login_required
def cards():
    thing = request.args.get( 'data', '', type = int )
    parentdict = comparefill(thing)
    return json.dumps(parentdict)

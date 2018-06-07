import pandas as pd
import xlrd
from app.models import Srep, Leaver, Suspect
from app import db
import os
import html5lib
import datetime
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from fuzzywuzzy import fuzz
import sys
from flask_login import current_user
import re
from multiprocessing import Pool
import datetime
import csv


######## Index/Homepage HELPERS ##############
#populates placed leavers in table on homepage
def placefill():
    placed = Leaver.query.filter_by(status='Placed', repcode=current_user.repcode).all()
    parentdict = {}
    placed_dict = {}
    placed_list = []
    for l in placed:
        placed_dict = {'leavername': l.name, 'leaverfirm': l.track_firm, 'leaverrole': l.track_role, 'leaverlocation': l.track_location, 'leaverlink': l.llink, 'leaverid': l.id}
        placed_list.append(placed_dict)
    parentdict['B'] = placed_list
    return parentdict


######## UPLOAD HELPERS ##############
#adds NEW leavers to database from pandas df
def pd2class(row):
    if Leaver.query.filter_by(name=row['name'], prole=row['role'], pfirm=row['firm']).first():
        pass
    else:
        l = Leaver(name=row['name'], repcode=row['repcode'], team=row['teamcode'], pfirm=row['firm'], prole=row['role'])
        db.session.add(l)
        db.session.commit()

#translates excel file to pandas df passing rows to pd2class
def processfile(file):
    data_xls = pd.read_excel(file)
    data_xls["name"] = data_xls["first"] + ' ' + data_xls["last"]
    data_xls = data_xls.drop('first', 1)
    data_xls= data_xls.drop('last', 1)
    data_xls.fillna(' ', inplace=True)
    data_xls.apply(pd2class, axis=1)
    return 'Success'

####### Track HELPERS ############
#populates the dropdown on track page with leavers. selection triggers tablefill
def fillselect(leavers):
    leaver_dict = []
    for l in leavers:
        suspects = Suspect.query.filter_by(leaverid=l.id, include='Yes').all()
        num = len(suspects)
        if num > 0:
            dval = l.name + ' ' + '(' + str(num) + ')'
            s_dict = {'ident': l.id, 'name': dval}
            leaver_dict.append(s_dict)
    return leaver_dict

#populates dictionary for suspect table on fillselect selection AND comparison card
def tablefill(thing):
    l = Leaver.query.filter_by(id=thing).first()
    ddate = l.timestamp.date().strftime('%m/%d/%Y')
    parentdict = {}
    suspect_list = []
    leaverdict = {'leavername': l.name, 'leaverfirm': l.pfirm, 'leaverrole': l.prole, 'leavertime': ddate}
    suspects = Suspect.query.filter_by(leaverid=thing, include='Yes').all()
    for s in suspects:
        s_dict = {'ident': s.id, 'name': s.name, 'link': s.link, 'role': s.role, 'firm':s.firm}
        suspect_list.append(s_dict)
    parentdict['A'] = leaverdict
    parentdict['B'] = suspect_list
    return parentdict

######################## Check HELPERS ############################
#generate 2 dicts to populate 2 cards for comparison
def comparefill(thing):
    parentdict = {}
    l = Leaver.query.filter_by(id=thing).first()
    ddate = l.timestamp.date().strftime('%m/%d/%Y')
    leaverdict = {'leaverid': l.id, 'leavername': l.name, 'leaverfirm': l.lfirm, 'leaverrole': l.lrole, 'leavertime': ddate, 'leaverlink': l.llink, 'leaverloc': l.llocation}
    d = {}
    d['name'] = l.name
    d['link'] = l.llink
    d['location'] = l.track_location
    d['id'] = l.id
    d['role'] = l.track_role
    d['firm'] = l.track_firm
    d['updated'] = l.track_lst_update
    parentdict['A'] = leaverdict
    parentdict['B'] = d
    return parentdict


def getchoices():
    leavers = Leaver.query.filter_by(repcode=current_user.repcode, status='Lost').all()
    choicelist = []
    for l in leavers:
        print(l.id)
        susps = Suspect.query.filter_by(leaverid=l.id, include='Yes').all()
        num = len(susps)
        print(num)
        if num > 0:
            snum = str(num)
            choice = (l.id, l.name + ' ' + '(' + snum + ')')
            choicelist.append(choice)
    return choicelist

def getupdates():
    leavers = Leaver.query.filter_by(repcode=current_user.repcode, status='Tracking').all()
    updatelist = []
    for l in leavers:
        choice = (l.id, l.name)
        updatelist.append(choice)
    return updatelist

def scrapename(sheep):
    browser = webdriver.Firefox(executable_path=r'/Users/Jeff/anaconda/bin/geckodriver')
    url_linkedin = 'https://www.google.com/search?q=' + sheep.name + ' ' + 'site:www.linkedin.com'
    browser.get(url_linkedin)
    results = browser.find_elements_by_class_name('rc')

    faillist = []
    passed = 'Accepted'
    failed = 'Rejected'
    result_list = []
    for item in results:
        result_list.append(item)

    item_list = []
    for item in result_list:
        item1 = item.text.split('\n')
        item_list.append(item1)


    ldict = []
    for item in item_list:
        if len(item) == 4:
            d = {}
            name = re.split('- |\|', item[0])[0].strip()
            d['Name'] = name
            print(d['Name'])
            d['Link'] = item[1]
            info_list = item[2].split(' - ')
            try:
                d['Location'] = info_list[0]
            except:
                d['Location'] = 'None'
            try:
                d['Role'] = info_list[1]
            except:
                d['Role'] = 'None'
            try:
                d['Firm'] = info_list[2]
            except:
                d['Firm'] = 'None'

            ratio = fuzz.token_set_ratio(name, sheep.name)
            if ratio < 80:
                d['Result'] = 'Rejected'
                faillist.append(d)
            else:
                d['Result'] = 'Accepted'
                ldict.append(d)

            link_exists = Suspect.query.filter_by(link=d['Link']).first()
            if link_exists is None and d['Result'] == 'Accepted':
                s = Suspect(name=d['Name'], location=d['Location'], role=d['Role'], link=d['Link'], leaverid=sheep.id)
                db.session.add(s)
                db.session.commit()

        elif len(item) == 3:
            d = {}
            otherlst = re.split('- |\|', item[0])
            d['Name'] = re.split('- |\|', item[0])[0].strip()
            name = re.split('- |\|', item[0])[0].strip()
            d['Link'] = item[1]
            d['Location'] = 'None'
            if 'https://www.linkedin.com/pub/dir/' in item[1]:
                d['Result'] = 'Rejected'
                faillist.append(d)
                pass
            elif len(otherlst) == 4 and otherlst[1] != 'LinkedIn':
                d['Role'] = otherlst[1]
                d['Firm'] = otherlst[2]
                d['Result'] = 'Accepted'

            else:
                d['Role'] = 'None'
                d['Firm'] = 'None'
                d['Result'] = 'Accepted'


            ratio = fuzz.token_set_ratio(name, sheep.name)
            if ratio < 80:
                d['Result'] = 'Rejected'
                faillist.append(d)
            else:
                ldict.append(d)

            link_exists = Suspect.query.filter_by(link=d['Link']).first()
            if link_exists is None and d['Result'] == 'Accepted':
                print(d['Name'], d['Result'])
                s = Suspect(name=d['Name'], location=d['Location'], role=d['Role'], link=d['Link'], leaverid=sheep.id)
                db.session.add(s)
                db.session.commit()
    browser.quit()
    return faillist

def check4chg(tracked):
    checklist = []
    browser = webdriver.Firefox(executable_path=r'/Users/Jeff/anaconda/bin/geckodriver')
    url_linkedin = 'https://www.google.com/search?q=' + tracked.llink
    browser.get(url_linkedin)
    results = browser.find_elements_by_class_name('rc')
    result = results[0].text.split('\n')
    browser.quit()
    dd = {}
    if len(result) == 4:
        d = {}
        d['Name'] = re.split('- |\|', result[0])[0].strip()
        info_list = result[2].split(' - ')
        if len(info_list) == 3:
            d['Location'] = info_list[0]
            d['Role'] = info_list[1]
            d['Firm'] = info_list[2]
        elif len(info_list) == 4:
            d['Location'] = info_list[0]
            d['Role'] = info_list[1] + ' ' + info_list[2]
            d['Firm'] = info_list[3]
        elif len(info_list) == 2:
            d['Location'] = info_list[0]
            d['Role'] = None
            d['Firm'] = None
        else:
            d['Location'] = None
            d['Role'] = None
            d['Firm'] = None
        dd['Name'] = [tracked.name, d['Name']]
        dd['Location'] = [tracked.llocation, d['Location']]
        dd['Role'] = [tracked.lrole, d['Role']]
        dd['Firm'] = [tracked.lfirm, d['Firm']]
        dd['Link'] = tracked.llink
        dd['ID'] = tracked.id

    elif len(result) == 3:
        d = {}
        d['Name'] = re.split('- |\|', result[0])[0].strip()
        d['Role'] = result[2]
        d['Location'] = None
        d['Firm'] = None

        dd['Name'] = [tracked.name, d['Name']]
        dd['Location'] = [tracked.llocation, d['Location']]
        dd['Role'] = [tracked.lrole, d['Role']]
        dd['Firm'] = [tracked.lfirm, d['Firm']]
        dd['Link'] = tracked.llink
        dd['ID'] = tracked.id

    return dd

def scrapename2(sheep):
    browser = webdriver.Firefox(executable_path=r'/Users/Jeff/anaconda/bin/geckodriver')
    url_linkedin = 'https://www.google.com/search?q=' + sheep.name + ' ' + 'site:www.linkedin.com'
    browser.get(url_linkedin)
    results = browser.find_elements_by_class_name('rc')

    item_list = []
    for item in results:
        item1 = item.text.split('\n')
        item_list.append(item1)
    browser.quit()

    fdict = []
    ldict = []
    for item in item_list:
        if len(item) == 4:
            d = {}
            info_list = []
            d['Name'] = re.split('- |\|', item[0])[0].strip()
            ratio = fuzz.token_set_ratio(d['Name'], sheep.name)
            d['Ratio'] = ratio
            d['Link'] = item[1]
            info_list = item[2].split(' - ')

            if len(info_list) == 3:
                d['Location'] = info_list[0]
                d['Role'] = info_list[1]
                d['Firm'] = info_list[2]
            elif len(info_list) == 4:
                d['Location'] = info_list[0]
                d['Role'] = info_list[1] + ' ' + info_list[2]
                d['Firm'] = info_list[3]
            elif len(info_list) == 2:
                d['Location'] = info_list[0]
                d['Role'] = None
                d['Firm'] = None
            else:
                d['Location'] = None
                d['Role'] = None
                d['Firm'] = None

            if d['Ratio'] > 77:
                ldict.append(d)
                link_exists = Suspect.query.filter_by(link=d['Link']).first()
                if link_exists is None:
                    s = Suspect(name=d['Name'], location=d['Location'], role=d['Role'], link=d['Link'], firm=d['Firm'], leaverid=sheep.id)
                    db.session.add(s)
                    db.session.commit()
            else:
                fdict.append(d)


        elif len(item) == 3 and 'https://www.linkedin.com/in/' in item[1]:
            d = {}
            d['Name'] = re.split('- |\|', item[0])[0].strip()
            ratio = fuzz.token_set_ratio(d['Name'], sheep.name)
            d['Ratio'] = ratio
            d['Link'] = item[1]
            d['Role'] = None
            d['Location'] = None
            d['Firm'] = None
            if d['Ratio'] > 77:
                ldict.append(d)
                link_exists = Suspect.query.filter_by(link=d['Link']).first()
                if link_exists is None:
                    s = Suspect(name=d['Name'], location=d['Location'], role=d['Role'], link=d['Link'], firm=d['Firm'], leaverid=sheep.id)
                    db.session.add(s)
                    db.session.commit()
            else:
                fdict.append(d)
    return fdict

def getlinks(repcode):
    leavers = Leaver.query.filter_by(repcode=repcode, status='Lost').all()
    tlst = []
    for l in leavers:
        url = 'https://www.google.com/search?q=' + l.name + ' ' + 'site:www.linkedin.com'
        lid = l.id
        tup = (lid, url)
        tlst.append(tup)
    return tlst

def threadscrape(ident, link):
    #browser = webdriver.Firefox(executable_path=r'/Users/Jeff/anaconda/bin/geckodriver')
    browser = webdriver.Firefox(executable_path=r'/.sar2/bin/geckodriver')
    browser.get(link)
    results = browser.find_elements_by_class_name('rc')
    lfuzz = Leaver.query.filter_by(id=ident).first()
    db_entries = []
    item_list = []
    for item in results:
        item1 = item.text.split('\n')
        item_list.append(item1)
    browser.quit()
    for item in item_list:
        if len(item) == 4:
            d = {}
            name = re.split('- |\|', item[0])[0].strip()
            d['Name'] = name
            d['Link'] = item[1]
            d['ID'] = lfuzz.id
            info_list = item[2].split(' - ')
            try:
                d['Location'] = info_list[0]
            except:
                d['Location'] = 'None'
            try:
                d['Role'] = info_list[1]
            except:
                d['Role'] = 'None'
            try:
                d['Firm'] = info_list[2]
            except:
                d['Firm'] = 'None'

            ratio = fuzz.token_set_ratio(name, lfuzz.name)
            if ratio < 80:
                d['Result'] = 'Rejected'
                db_entries.append(d)
            else:
                d['Result'] = 'Accepted'
                db_entries.append(d)

        elif len(item) == 3:
            d = {}
            otherlst = re.split('- |\|', item[0])
            d['Name'] = re.split('- |\|', item[0])[0].strip()
            name = re.split('- |\|', item[0])[0].strip()
            d['Link'] = item[1]
            d['Location'] = 'None'
            d['ID'] = lfuzz.id
            if 'https://www.linkedin.com/pub/dir/' in item[1]:
                d['Result'] = 'Rejected'
                db_entries.append(d)
                pass
            elif len(otherlst) == 4 and otherlst[1] != 'LinkedIn':
                d['Role'] = otherlst[1]
                d['Firm'] = otherlst[2]
                d['Result'] = 'Accepted'

            else:
                d['Role'] = 'None'
                d['Firm'] = 'None'
                d['Result'] = 'Accepted'


            ratio = fuzz.token_set_ratio(name, lfuzz.name)
            if ratio < 80:
                d['Result'] = 'Rejected'
                db_entries.append(d)
            else:
                db_entries.append(d)

    return db_entries

def turboscrape(fnc, tups):
    pool = Pool(3)
    results = pool.starmap(fnc, tups)
    return results

def linkexists(dic):
    link_exists = Suspect.query.filter_by(link=dic['Link']).first()
    if link_exists:
        return True
    else:
        return False

def processresults(results):
    for lst in results:
        for d in lst:
            if d['Result'] == 'Accepted' and linkexists(d) == False:
                s = Suspect(name=d['Name'], location=d['Location'], role=d['Role'], link=d['Link'], firm=d['Firm'], leaverid=d['ID'])
                db.session.add(s)
                db.session.commit()

#################### AJAX HELPERS ############################







def dblbackup():
    with open('/Users/Jeff/sar2/db_backup/leaver.csv', 'r', encoding='cp1252') as csvfile:
        # print(datetime.datetime.utcnow())
        tbl_reader = csv.reader(csvfile, delimiter=',')
        for row in tbl_reader:
            # dt = datetime.datetime.strptime(row[11], "%m/%d/%Y %H:%M:%S")
            l = Leaver(id=row[0], name=row[1], status=row[2], prole=row[3], pfirm=row[4],
            lrole=row[5], lfirm=row[6], llink=row[7], llocation=row[8], team=row[9],
            repcode=row[10], updated=row[12])
            db.session.add(l)
            db.session.commit()

def dbsbackup():
    # id	leaverid	name	include	role	firm	location	link	timestamp
    with open('/Users/Jeff/sar2/db_backup/suspect.csv', 'r', encoding = "ISO-8859-1") as csvfile:
        tbl_reader = csv.reader(csvfile, delimiter=',')
        for row in tbl_reader:
            s = Suspect(id=row[0], leaverid=row[1], name=row[2], include=row[3], role=row[4],
            firm=row[5], location=row[6], link=row[7])
            db.session.add(s)
            db.session.commit()
#Simply have another python script file (for example helpers.py) in the same
#directory as your main flask .py file. Then at the top of your main flask file,
# you can do import helpers which will let you access any function in helpers
#by adding helpers. before it (for example helpers.exampleFunction()). Or you
#can do from helpers import exampleFunction and use exampleFunction() directly
#in your code. Or from helpers import * to import and use all the functions
#directly in your code.

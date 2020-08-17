import datetime
import tornado.escape
import tornado.ioloop
import tornado.web
import os
import io
import string
import random
import requests
import pymysql
import json
import urllib
import time
import math

root = os.path.dirname(__file__)

dbhost = os.environ['DBHOST']
dbuser = os.environ['DBUSER']
dbpasswd = os.environ['DBPASSWD']
dbname = os.environ['DBNAME']

endpoint = os.environ['ENDPOINT']
jobpasswd = os.environ['JOBPASSWD']

def getconnection():
    db = MySQLdb.connect(host=dbhost,  # your host, usually localhost
                     user=dbuser,      # your username
                     passwd=dbpasswd,  # your password
                     db=dbname)        # name of the data base
    return(db)

def addurl():
    db = getconnection()
    cur = db.cursor()
    query = "INSERT INTO registry (url, short_url) VALUES ('%s', '%s')" % (url, shorturl)
    cur.execute(query)
    db.commit()
    cur.close()
    db.close()

def lookupurl():
    db = getconnection()
    cur = db.cursor()
    query = "SELECT * FROM jobqueue WHERE url='%s' LIMIT 1" % (url,)
    cur.execute(query)
    for res in cur:

    
    cur.close()
    db.close()

class RegisterURL():
    def get(self):
        return("")
    def post(self):
        return("")

class CreateJobHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        username = self.get_argument('username', True)
        password = self.get_argument('password', True)
        file1 = self.get_argument('file1', True)
        file2 = self.get_argument('file2', True)
        organism = self.get_argument('organism', True)
        outname = self.get_argument('outname', True)
        
        url = charon_url+"/login?username="+username+"&password="+password
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        uuid = data["message"]
        
        if data["status"] == "success":
            url = charon_url+"/files?username="+username+"&password="+password
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            
            files = data["filenames"]
            print(file1)
            print(file2)
            
            if file2 == True:
                if (file1 in files):
                    datalink = "https://s3.amazonaws.com/"+bucketname+"/"+uuid+"/"+file1
                    
                    h2 = hashlib.md5()
                    h2.update((datalink).encode('utf-8'))
                    uid = h2.hexdigest()
                    
                    db = getConnection()
                    cur = db.cursor()
                    query = "INSERT INTO jobqueue (uid, userid, datalink, outname, organism) VALUES ('%s', '%s', '%s', '%s', '%s')" % (uid, uuid, datalink, outname, organism)
                    
                    cur.execute(query)
                    db.commit()
                    cur.close()
                    db.close()
                    response = { 'action': 'create job',
                         'task': username,
                         'status': 'success',
                         'message': uid}
                    self.write(response)
                else:
                    response = { 'action': 'create job',
                         'task': username,
                         'status': 'error',
                         'message': 'file not found'}
                    self.write(response)
            else:
                if (file1 in files) & (file2 in files):
                    datalink = "https://s3.amazonaws.com/"+bucketname+"/"+uuid+"/"+file1+";"+"https://s3.amazonaws.com/"+bucketname+"/"+uuid+"/"+file2
                    
                    h2 = hashlib.md5()
                    h2.update((datalink).encode('utf-8'))
                    uid = h2.hexdigest()
                    
                    db = getConnection()
                    cur = db.cursor()
                    query = "INSERT INTO jobqueue (uid, userid, datalink, outname, organism) VALUES ('%s', '%s', '%s', '%s', '%s')" % (uid, uuid, datalink, outname, organism)
                    
                    cur.execute(query)
                    db.commit()
                    cur.close()
                    db.close()
                    response = { 'action': 'create job',
                         'task': username,
                         'status': 'success',
                         'message': uid}
                    self.write(response)
                else:
                    response = { 'action': 'create job',
                         'task': username,
                         'status': 'error',
                         'message': 'files not found'}
                    self.write(response)

class GiveJobHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        jpass = self.get_argument('pass', True)
        response = {}
        response["id"] = "empty"
        
        if jpass == jobpasswd:
            db = getConnection()
            cur = db.cursor()
            query = "SELECT * FROM jobqueue WHERE status='waiting' LIMIT 1"
            cur.execute(query)
            
            for res in cur:
                response["id"] = res[0]
                response["uid"] = res[1]
                response["userid"] = res[2]
                response["type"] = "sequencing"
                response["resultbucket"] = bucketname
                response["datalinks"] = res[3]
                response["outname"] = res[4]
                response["organism"] = res[5]
                query = "UPDATE jobqueue SET status='submitted', submissiondate=now() WHERE id='%s'" % (res[0])
                cur.execute(query)
                db.commit()
        
        self.write(response)

class FinishJobHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        jpass = self.get_argument('pass', True)
        uid = self.get_argument('uid', True)
        
        response = {}
        if jpass == jobpasswd:
            db = getConnection()
            cur = db.cursor()
            query = "UPDATE jobqueue SET status='completed', finishdate=now() WHERE uid='%s'" % (uid)
            cur.execute(query)
            db.commit()
            
            response["id"] = uid
            response["status"] = "completed"
        else:
            response["id"] = uid
            response["status"] = "failed"
        
        self.write(response)

application = tornado.web.Application([
    (r"/cloudalignment/givejob", GiveJobHandler),
    (r"/cloudalignment/finishjob", FinishJobHandler),
    (r"/cloudalignment/createjob", CreateJobHandler)
    (r"/cloudalignment/(.*)", tornado.web.StaticFileHandler, dict(path=root))
])

if __name__ == "__main__":
    application.listen(5000)
    tornado.ioloop.IOLoop.instance().start()
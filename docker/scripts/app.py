import tornado.escape
import tornado.ioloop
import tornado.web
import requests
import json
import os
import urllib
import boto3
import hashlib
from boto3.dynamodb.conditions import Key

DOMAIN = os.environ['DOMAIN']
ENDPOINT = os.environ['ENDPOINT']
API_KEY = os.environ['API_KEY']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

AWS_ID = os.environ['AWS_ID']
AWS_KEY = os.environ['AWS_KEY']
AWS_REGION = os.environ['AWS_REGION']

SESSION = boto3.Session(
    aws_access_key_id = AWS_ID,
    aws_secret_access_key = AWS_KEY,
    region_name=AWS_REGION
)
DYNAMODB = SESSION.resource('dynamodb')

def hashString(url):
    return(hashlib.sha1(url.encode("UTF-8")).hexdigest()[:8])

def put_url(url, dynamodb):
    urlhash = hashString(url)
    table = dynamodb.Table('shorturl')
    response = table.put_item(
       Item={
            'urlhash': urlhash,
            'url': url
        }
    )
    response['shorturl'] = DOMAIN+"/"+ENDPOINT+"/"+urlhash
    return response

def get_url(urlhash, dynamodb):
    table = dynamodb.Table(DYNAMODB_TABLE)
    response = table.query(
        KeyConditionExpression=Key('urlhash').eq(urlhash)
    )
    return response["Items"][0]

class RegisterURL(tornado.web.RequestHandler):
    def post(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        payload = tornado.escape.json_decode(self.request.body)
        apikey = payload["apikey"]
        response = {"error": "apikey not valid"}
        if apikey == API_KEY:
            url = payload["url"]
            response = put_url(url, DYNAMODB)
        self.write(response)

class RedirectURL(tornado.web.RequestHandler):
    def get(self, slug):
        self.set_header("Access-Control-Allow-Origin", "*")
        urlhash = self.request.path.split("/")[-1]
        url = get_url(urlhash, DYNAMODB)["url"]
        self.redirect(url)

application = tornado.web.Application([
    (r"/"+ENDPOINT+"/api/register", RegisterURL),
    (r"/"+ENDPOINT+"/(.*)", RedirectURL)
])

if __name__ == "__main__":
    application.listen(5000)
    tornado.ioloop.IOLoop.instance().start()
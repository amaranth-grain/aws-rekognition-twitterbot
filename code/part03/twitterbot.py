from __future__ import print_function
import boto3
import json
from twython import Twython

session = boto3.session.Session(region_name='us-west-2')
rek = session.client('rekognition')
table = 'celebrity-handler'
ddb = session.resource('dynamodb').Table(table)

with open('creds.json') as f:
    c = json.loads(f.read())

twitter = Twython(c['consumer_key'], c['consumer_secret'],
                  c['access_token_key'], c['access_token_secret'])


def post_msglist(content_list):
    """ Posts a tweet on Twitter account """
    for contents in content_list:
        twitter.update_status(status=contents)

def parse_queries(query_list):
    """ Takes a list of query objects and turns them into tweets. """
    output = []
    for query in query_list:
        tweet = f"{query.name} was detected in image upload. Their Twitter handle is {query.handle}."
        output.append(tweet)
    return output

def query_db(id):
    """ Queries DynamoDB and returns object with id, handle, name """
    data = ddb.get_item(TableName=table, Key={
        'id': id
    })
    return data['Item']

def use_rekognition(bucket, filename):
    """ Analyse picture in S3 by providing unique S3 bucket name (not ARN)
    and name of file to be analysed """
    response = rek.recognize_celebrities(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': filename
            }
        }
    )
    output = []
    for person in response['CelebrityFaces']:
        output.append(person["Id"])
    return output
    


def main():
    ids = use_rekognition("a01041926-rekognition", "c04.jpg")
    queries = []
    for id in ids:
        queries.append(query_db(id))
        
    tweets = parse_queries(queries)
    post_msglist(tweets)
        
    

if __name__ == '__main__':
    main()
import boto3
import os
from botocore.vendored import requests
from requests_aws4auth import AWS4Auth

region = os.environ["REGION"]
service = "es"
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = "https://" + os.environ["ESENDPOINT"] # the Amazon ElaticSearch domain, with https://
index = "lambda-index"
type = "lambda-type"

url = host + "/" + index + "/" + type + "/"

headers = { "Content-Type": "application/json" }

# UpdateSearchCluster - Updates Elasticsearch when new books are added to the store
def handler(event, context):
    count = 0
    for record in event["Records"]:
        # Get the primary key for use as the Elasticsearch ID
        id = record["dynamodb"]["Keys"]["id"]["S"]
        print "bookId " + id

        try:
            document = record["dynamodb"]["NewImage"]
            r = requests.put(url + id, auth=awsauth, json=document, headers=headers)
            count += 1
        except KeyError:
            # this execution path is to cater for deleted records
            document = record["dynamodb"]["OldImage"]
            r = requests.delete(url + id, auth=awsauth, json=document, headers=headers)
            count += 1
        
    return str(count) + " records processed."

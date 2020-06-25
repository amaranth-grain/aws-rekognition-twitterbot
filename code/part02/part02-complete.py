from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib

print('Loading function')
rekognition = boto3.client('rekognition')
sns = boto3.client('sns')


def detect_faces(bucket, key):
    response = rekognition.detect_faces(
        Image={"S3Object": {"Bucket": bucket, "Name": key}})
    numFaces = len(response["FaceDetails"])
    output = ""
    if numFaces == 1:
        output = "There was {0} face detected in this photo.".format(numFaces)
    else:
        output = "There were {0} faces detected in this photo.".format(
            numFaces)
    return output


def detect_text(bucket, key):
    output = ""
    response = rekognition.detect_text(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}})

    textDetections = response['TextDetections']
    print(textDetections)
    for text in textDetections:
            output += text['DetectedText'] + " "
    return output[:(len(output)/2) - 1]


def lambda_handler(event, context):
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(
        event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        # Calls rekognition DetectFaces API to detect faces in S3 object
        # response = detect_faces(bucket, key)

        # Calls rekognition text detection API to detect text
        response = detect_text(bucket, key)

        message = sns.publish(
            TargetArn="arn:aws:sns:us-west-2:168052438790:image-rekognition-sns",
            Message=response,
            Subject="Text Detected in S3 Image Upload"
        )

        # Print response to console.
        print(response)
        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e

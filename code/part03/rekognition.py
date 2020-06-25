from __future__ import print_function
import boto3

session = boto3.session.Session(region_name="us-west-2")
rek = session.client('rekognition')

response = rek.recognize_celebrities(
    Image={
        'S3Object': {
            'Bucket': 'a01041926-rekognition',
            'Name': 'c04.jpg',
        }
    }
)

print("Response:\n", response, "\n\n")
for celeb in response['CelebrityFaces']:
    print("{0} -- ID {1}".format(celeb["Name"], celeb["Id"]))

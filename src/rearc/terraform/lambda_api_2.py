import boto3
import os

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = os.environ['BUCKET_NAME']
    key = "sample-data.txt"
    s3.put_object(Bucket=bucket, Key=key, Body="Hello from Lambda A!")
    return {"statusCode": 200, "body": "File uploaded to S3"}

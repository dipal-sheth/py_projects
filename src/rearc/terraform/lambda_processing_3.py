import json

def lambda_handler(event, context):
    for record in event['Records']:
        message = record['body']
        print("Received SQS message:", message)
    return {"statusCode": 200}

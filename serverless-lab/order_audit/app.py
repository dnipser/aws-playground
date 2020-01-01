import boto3
import json
import logging
import os
from datetime import datetime
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(['boto3'])

dynamo_db = boto3.resource('dynamodb')
orders_table = dynamo_db.Table(os.getenv('ORDERS_AUDIT_TABLE'))


@xray_recorder.capture('persist_audit')
def handle_order_audit_event(event, context):
    order_event = json.loads(event['Records'][0]['body'])

    customer_id = order_event['customerId']
    order_id = order_event['orderId']

    timestamp = str(datetime.utcnow().timestamp())

    item = {
        'CustomerId': customer_id,
        'OrderId': order_id,
        'CreatedAt': order_event['createdAt'],
        'ProcessedAt': timestamp
    }
    result = orders_table.put_item(Item=item)
    logging.info("Persisted order audit event", item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }
    logging.info("Processed order audit event ", result)
    return response

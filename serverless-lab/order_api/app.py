
import boto3
import decimal
import json
import logging
import os
from datetime import datetime
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(['boto3'])

dynamo_db = boto3.resource('dynamodb')
orders_table = dynamo_db.Table(os.getenv('ORDERS_TABLE'))

sqs = boto3.resource('sqs')
audit_queue = sqs.get_queue_by_name(QueueName=os.getenv('ORDERS_AUDIT_QUEUE'))


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


@xray_recorder.capture('retrieve_order')
def get_order(event, context):
    if 'queryStringParameters' not in event:
        raise Exception('Required query parameters are missing!')

    query_params = event['queryStringParameters']
    if 'customerId' not in query_params or 'orderId' not in query_params:
        raise Exception('Required query parameters are missing!')

    customer_id = event['queryStringParameters']['customerId']
    order_id = event['queryStringParameters']['orderId']

    result = orders_table.get_item(
        Key={
            'CustomerId': customer_id
        },
        ConsistentRead=True
    )

    response = {
        "statusCode": 200,
        "body": json.dumps(result['Item'], cls=DecimalEncoder)
    }
    logging.info("Get order result ", result)
    return response


@xray_recorder.capture('persist_order')
def create_order(event, context):
    order = json.loads(event['body'], parse_float=decimal.Decimal)

    customer_id = order['customerId']
    order_id = order['orderId']

    timestamp = str(datetime.utcnow().timestamp())

    item = {
        'CustomerId': customer_id,
        'OrderId': order_id,
        'Name': order['name'],
        'Quantity': order['quantity'],
        'Price': order['price'],
        'Currency': order['currency'],
        'OrderDate': order['orderDate'],
        'DeliveryDate': order['deliveryDate'],
        'DeliveryAddress': order['deliveryAddress'],
        'CreatedAt': timestamp,
        'UpdatedAt': timestamp,
    }
    orders_table.put_item(Item=item)
    logging.info("Persisted order ", item)

    send_audit_event(order)

    response = {
        "statusCode": 200,
        "body": json.dumps(item, cls=DecimalEncoder)
    }
    logging.info("Create order result ", response)
    return response


@xray_recorder.capture('audit_event')
def send_audit_event(order):
    customer_id = order['customerId']
    order_id = order['orderId']

    timestamp = str(datetime.utcnow().timestamp())

    audit_item = {
        'customerId': customer_id,
        'orderId': order_id,
        'createdAt': timestamp
    }
    audit_response = audit_queue.send_message(
        MessageBody=json.dumps(audit_item),
        MessageGroupId=customer_id
    )
    logging.info("Sent audit event ", audit_response)

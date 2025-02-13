import json
import os

import pika
from dotenv import load_dotenv

from xPortfolio.algo import optimize_portfolio
from xPortfolio.utils import logger


def on_request(ch, method, props, body):
    message = json.loads(body)
    logger.info('Received message')

    response = optimize_portfolio(message)

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def serve():
    host = os.getenv('RABBITMQ_HOST', 'localhost')
    port = int(os.getenv('RABBITMQ_PORT', 5672))

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
    channel = connection.channel()

    exchange_name = "direct_rpc"
    routing_key = "optimize_portfolio"

    queue = channel.queue_declare('', auto_delete=True, exclusive=True)
    queue_name = queue.method.queue

    channel.exchange_declare(exchange=exchange_name, durable=True, exchange_type='direct')
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_request)

    channel.start_consuming()


if __name__ == "__main__":
    load_dotenv()
    serve()

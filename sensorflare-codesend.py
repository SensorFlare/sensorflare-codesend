#!/usr/bin/env python
__author__ = 'amaxilatis'

# required for logging
# required for rabbitmq connections
import pika
# required for rabbitmq credentials
from properties import *

import socket

import logging
import logger

logger.log_config()


# create the rabbitmq exchange and queue names to communicate with sensorflare
send_exchange = "raspberry-" + username + "-send"
commands_exchange = "raspberry-" + username + "-commands"
commands_queue = "raspberry-" + username + "-commands"

logging.info(" [x] send_queue: " + send_exchange)
logging.info(" [x] commands_queue: " + commands_queue)
logging.info(" [x] commands_exchange: " + commands_exchange)

# sensorflare rabbitmq server
sensorflareHost = 'mochad.sensorflare.com'
# create the credentials to communicate with rabbitmq
sensorflareCredentials = pika.credentials.PlainCredentials(username, password)

# function that connects to rabbitmq and listens for commands
def create_connection(host, credentials):
    # create a blocking connection with pika
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials))
    # open a channel for rabbitmq
    channel = connection.channel()
    logging.info(" [x] connected to '"+sensorflareHost+"'")
    # declare the commands exchange if missing
    channel.exchange_declare(exchange=commands_exchange, type='topic', durable=True, internal=False, auto_delete=False,passive=True)
    # bind our queue to the exchange
    channel.queue_bind(exchange=commands_exchange, queue=commands_queue)

    def rabbitSend(message):
        try:
            channel.basic_publish(exchange=send_exchange, routing_key=send_exchange, body=message)
        except:
            logging.error(' [x] error sending back message')

    def callback(ch, method, properties, body):
	import subprocess
	subprocess.call(["codesend", body])
        logging.info(' [c] codesend:' + body)
        rabbitSend(body)
    # set the consume callback
    channel.basic_consume(callback, queue=commands_queue, no_ack=True)

    # start waiting for the commands
    logging.info(' [*] Waiting for commands. To exit press CTRL+C')

    # send a connect message to sensorflare
    rabbitSend('connected\n')

    # start the blocking consume
    try:
        channel.start_consuming()
    except:
        logging.error(' [*] connection was closed!')
        logging.info(' [x] reconnecting in 5 seconds...')
        import time

        time.sleep(5)
        logging.info(' [x] reconnecting...')
        create_connection(host, credentials)

# start the first connection
create_connection(sensorflareHost, sensorflareCredentials)

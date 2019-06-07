'''
Created on 29 may 2019

master function for a list creator Serverless
distributed system.

@author: German Telmo Eizaguirre Suarez
@contact: germantelmoeizaguirre@estudiants.urv.cat
@organization: Universitat Rovira i Virgili

'''

import pika
import json
import random

my_dict = dict()
my_dict['requests']= list()
my_dict['sent_list']=list()
my_dict['value_published']=True
        
def endRequests ():
    return len(my_dict['requests']) == my_dict['current_maps']

def addRequest (ident):
    my_dict['requests'].append(ident)
        
def publishPermission ():

    sent_number = random.choice(my_dict['requests'])
    msg = dict()
    msg['type']="WRITE_PERMISSION"
    msg['value']=sent_number;
    msg['ident']=my_dict['ident']
    my_dict['channel'].basic_publish( exchange= my_dict['config']['exchange_name'],
                                           routing_key='',
                                           body=json.dumps(msg))
    ''' my_dict['sent_list'].append(sent_number) '''
    my_dict['requests'].clear()
    my_dict['current_maps'] = my_dict['current_maps'] - 1
    my_dict['value_published'] = False
    print ("Write access to " + str(msg['value']) + " allowed.")

def master (elem):
    
    print ("Hello, I'm the master.")
    my_dict['number_maps'] = elem ['num_nodes']
    my_dict['current_maps'] = my_dict['number_maps']
    my_dict['config'] = elem['res']
    params = pika.URLParameters(my_dict['config']['rabbit_mq']['url'])
    params.socket_timeout = 10
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    my_dict['channel'] = channel
    my_dict['ident'] = my_dict['number_maps'] + 1
    result = channel.queue_declare(queue=my_dict['config']['leader_queue'],  exclusive=True)
    channel.exchange_declare(exchange = my_dict['config']['exchange_name'],
                         exchange_type='fanout')
    channel.queue_bind( exchange=my_dict['config']['exchange_name'],
                   queue=result.method.queue )

    channel.basic_consume( queue=result.method.queue, consumer_callback=managePermissions, no_ack=True)
    channel.start_consuming()
    connection.close()

def managePermissions (ch, method, properties, body):
    '''
    Check for request messages.
    '''
    msg = json.loads(body)
    if msg['type']=="WRITE_REQUEST":
        addRequest(ident=str(msg['ident']))
        print ("Slave " + str(msg['ident']) + " to permission list.")
        
    if msg['type']=="VALUE":
        my_dict['value_published'] = True
        if my_dict['current_maps'] == 0:
            ch.stop_consuming()
        
    if endRequests() & my_dict['value_published']:
        publishPermission()


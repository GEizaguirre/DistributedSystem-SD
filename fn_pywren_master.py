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
my_dict['received_maps']=0
my_dict['requests']= list()
my_dict['done_list']=list()
my_dict['sent_list']=list()
        
def endRequests ():
    return len(my_dict['requests']) == my_dict['number_maps']

def addRequest (ident):
    my_dict['requests'].append(ident)
        
def endWrites ():
    return len(my_dict['done_list']) == my_dict['number_maps']
        
def addDone (ident):
    my_dict['done_list'].append(ident)
        
def publishPermission ():
    ''' sent_number = random.randint(1, my_dict['number_maps']) '''
    sent_number = random.choice(my_dict['requests'])
    msg = dict()
    msg['type']="WRITE_PERMISSION"
    msg['value']=sent_number;
    msg['ident']=my_dict['ident']
    my_dict['channel'].basic_publish( exchange= my_dict['config']['exchange_name'],
                                           routing_key='',
                                           body=json.dumps(msg))
    my_dict['sent_list'].append(sent_number)
    my_dict['requests'].remove(sent_number)

def master (elem):
    
    num_nodes = elem ['num_nodes']
    res = elem['res']
    params = pika.URLParameters(res['rabbit_mq']['url'])
    params.socket_timeout = 10
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    result = channel.queue_declare(queue=res['leader_queue'])

    my_dict['channel']= channel
    my_dict['config']=res
    my_dict['number_maps']=num_nodes
    my_dict['ident']=num_nodes+1
    channel.basic_consume( queue=result.method.queue, consumer_callback=manageRequests, no_ack=True );
    channel.start_consuming()
    
    result = channel.queue_declare(queue=res['default_prefix']+"master")
    channel.exchange_declare(exchange = res['exchange_name'],
                         exchange_type='fanout')
    channel.queue_bind( exchange=res['exchange_name'],
                   queue=result.method.queue )
    publishPermission()
    channel.basic_consume( queue=result.method.queue, consumer_callback=managePermissions, no_ack=True)
    channel.start_consuming()
    connection.close()

def config_channel(res):
    '''
    Configurate message channel RabbitAMQ.
    '''
    params = pika.URLParameters(res['rabbit_mq']['url'])
    connection = pika.BlockingConnection(params)
    return(connection.channel())

def manageRequests (ch, method, properties, body):
    '''
    Check for request messages.
    '''
    msg = json.loads(body)
    addRequest(ident=str(msg['ident']));
    if endRequests(): ch.stop_consuming()
    ''' ch.stop_consuming() '''
    
def managePermissions (ch, method, properties, body):
    '''
    Check exchange messages.
    '''
    msg = json.loads(body)
    
    if msg['type'] == "VALUE":
        addDone(msg['ident']);
        if endWrites(): ch.stop_consuming()
        else: publishPermission()

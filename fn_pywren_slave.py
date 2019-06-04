'''
Created on 29 may 2019

slave function for a list creator Serverless
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
my_dict['my_list']= list()
my_dict['done_list']=list()
my_dict['sent']=False
        
def increaseReceived ( msg):
    my_dict['my_list'].append(msg['value'])
    my_dict['done_list'].append(msg['ident'])
    print("Slave "+str(my_dict['my_ident'])+" received number "+ str(msg['value']) + " from " + str(msg['ident']))
    my_dict['received_maps']+=1
        
def end ():
    return my_dict['received_maps'] == my_dict['number_maps']
    
def publishValue ():
    msg = dict()
    msg['type']="VALUE"
    msg['value']=my_dict['my_number']
    msg['ident']=my_dict['my_ident']
    my_dict['channel'].basic_publish( exchange=my_dict['config']['exchange_name'],
                                           routing_key='',
                                           body=json.dumps(msg))
    my_dict['sent']=True
    print("Slave " + str(my_dict['my_ident']) +" published the value " + str(my_dict['my_number']))


def slave (num_nodes, ident, res):
    
    params=pika.URLParameters(res['rabbit_mq']['url'])
    params.socket_timeout = 10
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    msg = dict()
    msg['ident']=ident
    channel.basic_publish (exchange='', routing_key=res['leader_queue'], body=json.dumps(msg))
    result = channel.queue_declare(queue=res['default_prefix']+str(ident), exclusive=True)
    channel.exchange_declare(exchange = res['exchange_name'],
                         exchange_type='fanout')
    channel.queue_bind(exchange=res['exchange_name'],
                   queue=result.method.queue)
    my_dict['number_maps']=num_nodes
    my_dict['config']=res
    my_dict['my_number']=random.randint(my_dict['config']['min_number'],my_dict['config']['max_number'])
    my_dict['my_ident']=ident
    my_dict['channel']= channel
    channel.basic_consume(queue=result.method.queue, consumer_callback=manageResults, no_ack=True)
    channel.start_consuming()
    connection.close()
    print("Slave " + str(my_dict['my_ident']) +' finished.')
    return (my_dict['my_list'])



def manageResults (ch, method, properties, body):
    '''
    Check for chunk completion messages.
    '''
    msg = json.loads(body)
    if msg['type'] == "VALUE":
        increaseReceived(msg)
        if end(): 
            ch.stop_consuming() 
    else:
        if msg['type'] == "WRITE_PERMISSION":
            if  ( not my_dict['sent']  ) and (int(msg['value']) == my_dict['my_ident']) :
                publishValue()
        

    


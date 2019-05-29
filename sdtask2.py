'''
Created on 29 may 2019

Serverless Distributed System, main program.
Creates n equal lists of random numbers remotely.

@author: German Telmo Eizaguirre Suarez
@contact: germantelmoeizaguirre@estudiants.urv.cat
@organization: Universitat Rovira i Virgili

'''

import pywren_ibm_cloud as pywren
import yaml
import sys
import pika
from fn_pywren_slave import  slave
from fn_pywren_master import  master

'''
Read of the configuration file.
'''
try:
    with open('cloud_config', 'r') as config_file:
        res = yaml.safe_load(config_file)
except FileNotFoundError:
    print (" We could not find your configuration yaml file cloud_config.")
    sys.exit(1)

default_node_number = 5

'''
Main program.
'''
def main ():
    
    '''
    Control of arguments.
    '''
    if (len(sys.argv) == 1):
        print ("No parameters were detected.\nThe number of nodes must be specified. \n")
        show_help()
        sys.exit(1)
    else:    
        if ( int(sys.argv[1]) > 0 ) and ( int(sys.argv[1]) < 18 ):
            node_number = int(sys.argv[1])
            print ("Number of nodes set to:  "  + str(node_number))
        else:
            node_number=default_node_number
            print ("Number of nodes set to the default: " + str(default_node_number))
            
    
    pw1 = pywren.ibm_cf_executor(runtime_memory=128, rabbitmq_monitor=True)

    ''' 
    Call leader
    '''
    params = dict()
    params['elem'] = dict()
    params['elem'] ['num_nodes'] = node_number
    params['elem']['res']=res
    pw1.call_async(master, params)
    
    '''
    Call mappers.
    '''
    params = list()
    for count in range( 0, node_number ):
        params.append(dict())
        params[count] ['num_nodes'] = node_number
        params[count] ['ident'] = count + 1
        params[count] ['res'] = res
    print("Calling...")
    pw2 = pywren.ibm_cf_executor(runtime_memory=128, rabbitmq_monitor=True)
    pw2.map(slave, params)
    result2 = pw2.get_result()
    print (result2)
    if result2.count(result2[0]) == len(result2):
        print ("The algorithm worked.")
    else:
        print ("The algorithm failed.")
        
   
def config_channel(res):
    params = pika.URLParameters(res['rabbit_mq']['url'])
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    return channel

def show_help ():
    f = open('Description', 'r')
    txt= f.read()
    print (txt)
    f.close()
    
if __name__ == '__main__':
    main()

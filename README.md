# sdtask2

## Description

Author: German Telmo Eizaguirre Suarez (URV, Tarragona)
Version: 1.0
Date: 29-05-2019

Distributed System based on Serverless Computing in the IBM Cloud.
This program uses the IBM Cloud Functions service through the IBM-PyWren middleware 
(http://cloudlab.urv.cat/josep/distributed_systems/p1-Sampe.pdf) and the Rabbit MQ 
service.

A finite number of functions are generated according to the number entered as argument.
Each functions generates a random number that is transmitted to the other functions
using a fanout Exchange. A coordinator ("master") guarantees mutual exclusion among
processes and ensures all functions receive values in the same order. Finally, every
serverless function returns the same list of values.

This project is implemented in Python 3.6

## Use

The main script is sdtask2.py.

For a correct execution of the system, a file cloud_config file with the RabbitMQ URL and some 
different setting must be set up. Follow the model at cloud_config_model.

For executing the program it is only necessary to call sdtask2.py as a python script. It receives the
first argument as the number of nodes it has to create. The number of nodes must be wrapped
between 1 and 18, if not it will be set to the default 5.

Example: >> python3 sdtask2.py 7

## General diagram
![Alt text](diagrams/distributedsystemSD1.jpeg?raw=true "General diagram of our distributed system 1")
![Alt text](diagrams/distributedsystemSD2.jpeg?raw=true "General diagram of our distributed system 2")
![Alt text](diagrams/distributedsystemSD3.jpeg?raw=true "General diagram of our distributed system 3")



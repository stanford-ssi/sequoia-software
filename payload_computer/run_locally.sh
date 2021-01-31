#!/bin/bash

redis-server --daemonize yes

for service in serialOutNode.py cameraNode.py imageProcessorNode.py serialCommandNode.py
do 
    python $service &
done 

python SerialInNode.py

pkill redis-server 
pkill python

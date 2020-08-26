### Decentralized Payload Module ###

Prerequisites:
- Python 3.8.2 (easiest just using homebrew)
- Redis (easiest just using homebrew)
- Install modules in requirements.txt (Important: If you are just testing on local machine, you don't need to install 
picamera and pyserial)
- Run redis server on default port (or change it in config.ini)
- If testing without a raspberrypi, make sure "TEST" in config.ini is set to True.

Running:
- Run all the files ending on "...Node.py" separately in Pycharm or using separate terminal windows
- Stop at any time with Control-C (cleanup is handled automatically)
- Everything is working properly if the output of "serialOutNode.py" is part of an numpy array every five seconds if in
test mode


#### Background Info: ####
The idea is that there is a central Redis messaging service to pass data between the different
nodes in the system. The goal is to enable asynchronous processing with maximum data throughput,
which is given here since the use of asyncio makes sure that nothing can block execution. At the 
moment, all the Nodes are run in distinct processes to demonstrate that they can be placed anywhere
within the local network, but you could also just put them in one event loop if the number of processes
produces too much overhead. The crucial part here is that pretty much every node only does one single thing,
e.g. interacting with peripherals, processing data, issuing commands, etc. and only does this when it 
receives data from somewhere else. That means this works very similar to Node.js with callback-based execution.
The different nodes all connections to the Redis service, where they can subscribe to channels or publish messages
on channels. The asynchronous nature is created exactly because nothing executes in a node until it receives a message
from the channel it is subscribed to and it does not block anything else in the meanwhile. To make sure that the right
channels are connected, all the channel names are centrally located in config.ini, so when adding new Nodes, please add
your channel names there. Redis also has lots of other features, like storing values at a specified key, but for now,
the publish/subscribe mechanism should be enough. 

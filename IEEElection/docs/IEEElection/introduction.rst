.. include:: substitutions.rst

Introduction
============

IEEE 1394 is a framework for high-speed serial bus communication in various electronic devices,
facilitating the seamless exchange of digitized video and audio signals.
It is also hot-pluggable which means that the devices can be added or removed at any time without disrupting the system's operation(which actually is the starting point of our algorithm)
This triggers a bus reset upon such changes.
When that happens our Leader Election Protocol would be used.

The Leader Election Protocol assigns leadership dynamically these networks(afterbus reset),
After reset, all nodes within the network are restored to an equal status.
Which means they need a new leader.
However, nodes don't have the total topological knowledge and  only knows immediate neighnoors.

Our task revolves around a irreflexive(since a self edge is not present in such networks and even if it was would not have been in any use for such a problem) connected and acyclic network of nodes, interconnected by bidirectional edges.
The objective is once again: To elect a leader, in this distributed environment. 


To summarize the problem consists of below following key points:

- It is “hot-pluggable”
- Devices and peripherals can be added and removed at any time
- Such changes are followed by a bus reset
- The leader election takes place after a bus reset in the network
- A leader needs to be chosen to act as the manager of the bus
- After a bus reset: all nodes in the network have equal status
- A node only knows to which nodes it is directly connected
- The network is connected
- The network is acyclic

Our primary contributions consist of the following:
    
- Implementation of Election in IEEE 1394 Algorithm on the AHCv2 platform. The implementation specifics are detailed in Section XX.
- Examination of the performance of the algorithm across diverse topologies and usage scenarios. Results from these investigations are outlined in Section XXX.

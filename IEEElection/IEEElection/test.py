import logging
from time import time,sleep
import random
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import networkx as nx
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes, setAHCLogLevel
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.NetworkLayer.GenericNetworkLayer import GenericNetworkLayer
from adhoccomputing.Networking.ApplicationLayer.GenericApplicationLayer import GenericApplicationLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

from AlgorithmComponent import AlgorithmComponent as NodeModel, ChannelComponentModel
# from NodeComponent import NodeComponentModel as NodeModel




def main():
    res_dict = {}
    for N in range(10,101,10):
        for trial in range(3):
            G = nx.Graph()
            topo = Topology()
            for node_num in range(N):
                G.add_node(node_num)
                if node_num:
                    other_node = random.randint(0,node_num-1)
                    G.add_edge(other_node, node_num)

            topo.construct_from_graph(G, NodeModel, ChannelComponentModel)
            start_time = time()
            topo.start()
            sleep(0.3)
            
            message_count = 0
            for node in topo.nodes.values():
                message_count += node.msg_count
            time_taken = NodeModel.end_time - start_time
            NodeModel.end_time = -1
            res_dict.setdefault(N, []).append((time_taken, message_count))
        res_dict[N] = tuple(sum(tple) / len(tple) for tple in zip(*res_dict[N]))

    x_values = list(res_dict.keys())
    y_message_count = [value[1] for value in res_dict.values()]
    y_time = [value[0] for value in res_dict.values()]

    for i in range(10,101,10):
        print(i, res_dict[i])

    plt.figure(figsize=(10, 5))
    plt.plot(x_values, y_message_count, marker='o', linestyle='-', color='blue')
    plt.xlabel('Node Count')
    plt.ylabel('Message Count')
    plt.title('Message Count over Node Count')
    plt.grid(True)
    plt.show()

    # Creating the plot for time
    plt.figure(figsize=(10, 5))
    plt.plot(x_values, y_time, marker='o', linestyle='-', color='red')
    plt.xlabel('Node Count')
    plt.ylabel('Time')
    plt.title('Time over Node Count')
    plt.grid(True)
    plt.show()



if __name__ == "__main__":
    main()
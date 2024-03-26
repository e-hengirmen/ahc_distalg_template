.. include:: substitutions.rst

|IEEElection|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The [IEEE]_ standard mentions about the problem under the concept of isochronous resource manager (IRM) selection.
It also provides examples of processes for selecting the IRM within a backplane environment.
However, it doesn't go into the algorithmic details of how the selection process should be implemented.

Additionally, [Devillers]_ formalizes a simple algorithm for this IEEE standard protocol.
This paper addresses ambiguities and challenges encountered during the process.
The authors of the paperesspecially focuses on the tree identify phase.
This paper serves as formal verification of this distributed algorithm. We will also use their method in our implementation.

.. [IEEE] IEEE Standard for a High Performance Serial Bus," in IEEE Std 1394-1995 , vol., no., pp.326-327, 30 Aug. 1996, doi: 10.1109/IEEESTD.1996.81049.
.. [Devillers] Devillers, M., Griffioen, D., Romijn, J. et al. Verification of a Leader Election Protocol: Formal Methods Applied to IEEE 1394. Formal Methods in System Design 16, 307–320 (2000).

Distributed Algorithm: |IEEElection| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An example distributed algorithm for finding a leader/isochronous resource manager(IRM) on an undirected graph is presented in  :ref:`Algorithm <IEEEalgorithmLabel>`.

.. _IEEEalgorithmLabel:

.. code-block:: RST
    :linenos:
    :caption: Leader Election algorithm in IEEE 1394.
    

    Implements: 
    Uses: 
        send_message,  # sends message to given neighboor for asking parentage
        send_ack_message,  # sends message to given neighboor for accepting parentage
        set_timer,  # set timer after the timer ends that uses the given function with given arguments.
        remove_timer,  # remove timer for that neighboor
    Events:
        Init,
        MessageNeighboor,
        OnMessageFromNeighboor,
        OnReceivingAcknowledgementMessageFromNeighboor,
        OnReceivingParentageRequstFromNeighboor,
    Needs: 
        adjacent_nodes_set: ans,
        my_node_id: my_node_id

    OnInit: () do
        parent = None
        message_queue_set = set()
        remaining_ans = ans.deep_copy()
        remaining_neighboor_count = remaining_ans.length()
        If remaining_neighboor_count == 1:  # becomes a leaf
            last_neighboor = remaining_ans.first()
            MessageNeighboor(last_neighboor)
    
    MessageNeighboor: ( x ) do
        If my_node_id < x:
            parent = x
        send_message(x)  # will u be my father
        set_timer(x, MessageNeighboor, x)
        message_queue_set.add(x)

    OnMessageFromNeighboor: ( message, x ) do
        If message is 'acknowledgement':
            OnReceivingAcknowledgementMessageFromNeighboor(x)
        Else If message is 'parentage request':
            OnReceivingParentageRequstFromNeighboor(x)
    
    OnReceivingAcknowledgementMessageFromNeighboor: (x) do
        remove_timer(x)
        message_queue_set.remove(x)
        parent = x # lifecycle of this node ends

    OnReceivingParentageRequstFromNeighboor: (x) do
        neighboor_is_the_father = False
        If parent == x:  # parent chosen as x before thus contention
            neighboor_is_the_father = True
            send_message(x)
        Elif x in message_queue_set:  # other party whose id is lower chosen me as parent thus contention
            remove_timer(x)
            message_queue_set.remove(x)
            root = my_node_id  # root is chosen  if it is needed for everyone to know broadcase message can be added
        
        If not neighboor_is_the_father:
            remaining_ans.remove(x)
            remaining_neighboor_count -= 1
            send_ack_message(x)
            If remaining_neighboor_count == 1:  # becomes a leaf
                last_neighboor = remaining_ans.first()
                MessageNeighboor(last_neighboor)


Informally, the basic idea of the protocol is as follows: leaf nodes send a “parent request”
message to their neighbor. When a node has received a parent request from all but one of
its neighbors it sends a parent request to its remaining neighbor. In this way the tree grows
from the leafs to a root. If a node has received parent requests from all its neighbors, it
knows that it is has been elected as the root of the tree. The root node is also referred to as
the leader or the bus master.
Let us consider the operation of the protocol in some more detail. During the tree identify
phase every node goes through three stages. In the first stage, a node waits until it has
received a parent request on all edges except one. Since leaf nodes have at
most one connection, they can skip the first stage, and are thus responsible for starting up
the algorithm.

In the second stage, a node acknowledges all the parent requests that it has received and
sends a parent request on the remaining edge on which it has not received a parent
request. In Example, two links have been assigned as “child links” and one parent request
from a leaf node is still pending. In the third stage, if a node has received parent requests
on all edges but has not sent a parent request itself, then it decides that it is the root of the
tree and terminates. If a node that has sent a parent request receives an acknowledgement
then it also terminates but decides that it has not been elected as the root. It is possible
that two nodes send parent requests to each other; this situation is called root contention
and is illustrated in figure 3. Whenever root contention occurs, the nodes that are involved
retransmit their parent request after random timeouts and return to the beginning of the third stage.

Example
~~~~~~~~
- For example  lets assume this is our topology

.. image:: figures/topology.png
  :align: center
  :width: 200
  :alt: Example topology

- At one point we come to this intermediate step

.. image:: figures/some_intermediate_step.png
  :align: center
  :width: 200
  :alt: Example topology

- At last 2 nodes send each other parent requests(this might be possibly avoided with randomized waits but not guaranteed) thus contending for root position(or trying to reclus theirselves from)

.. image:: figures/contending_nodes.png
  :align: center
  :width: 200
  :alt: Example topology

- Root Chosen

.. image:: figures/root_found.png
  :align: center
  :width: 200
  :alt: Example topology

Correctness
~~~~~~~~~~~


- Requirements:
    - We know that for a graph to be fully connected there must be at least N-1 edges. Since an edgeless graph can have 1 connected component. And every edge can add 1 component to that graph.
    - Assume that there are N-1 edges and N nodes in a fully connected graph. Since we know that every edge added one node we know that it is acyclic.
    - In a connected graph if u add 1 edge from 1 node to another that will create a cycle thus it should have exactly N-1 edges to be acyclic
- Knowing above requirements if a graph has no non leaf nodes it means that it has at least 2N edges which will surely make it cyclic thus contradiction
- Since it is not cyclic some of the nodes has to be leafs.
- Only leafs sends request to possible parents.
- When a node chooses its parent(it has to be acknowledged) it is eliminated from this process.
- After every elimination there are 3 cases:
    - Either there are at least one previous leaf remaining(in this case at least one of these chooses its parents)
    - There is no previous leaf remaining but since these leaf nodes are removed from our calculation new leafs are created
    - Parent chosen process ends

because of above reasons this algorithm is correct.

- In addition to above, for contention instead of using randomized waits I chose to appoint node with higher number as root. To do this:
    - In case the current node having lower id. It first appoints the neighboor as its root then sends parentage request. In the case of receiveng a root request from said node, it resends root request to that neighboor forcing parentship until acknowledgement received. 
    - In case the current node having higher id. It sends parentage request. In the case of receiveng a root request from said node instead of acknowledgement, immediately accepts.
    - Thus:
        - In case of contention(last 2 nodes) since lower id forces parentage, higher id will receive parentage request at some point and acknowledge it ending the cycle.
        - In case of no contention even if it is lower or higher id since the other node doesn't send a request back it will acknowledge the parentage request.

Complexity
~~~~~~~~~~

1. **Time Complexity**  The IEEElection :ref:`Algorithm <IEEEalgorithmLabel>` takes at most O(N*RTT) time units to complete where N is the number of nodes
2. **Message Complexity:** The IEEElection :ref:`Algorithm <IEEEalgorithmLabel>` requires O(N) messages and their acknowledgements.


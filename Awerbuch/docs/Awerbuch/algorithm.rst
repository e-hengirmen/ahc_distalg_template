.. include:: substitutions.rst

|Awerbuch|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The 1985 paper [Awerbuch1985]_ proposes the method for alpha beta gamma synchronizers(without naming them as alpha beta gamma) and analyzes the trade-offs between them in this paper.
So in essence its a paper that introduces simple methodologies for designing efficient distributed algorithms in asynchronous networks.

Distributed Algorithm: |Awerbuch| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Alpha
---------------------------------


An example distributed algorithm for local synchronization is presented in  :ref:`Algorithm <AlphaAlgorithmLabel>`.


.. _AlphaAlgorithmLabel:

.. code-block:: RST
    :linenos:
    :caption: Awerbuch's alpha algorithm.
    

    Implements:
    Uses:
        set_neighboors_not_received,  # sets every value in adjnd as not received or False
        create_current_round_messages,  # creates messages for current round
        do_round_process,
        set_received_rmd_messages_to_none,
        send_messages_to_neighboors,
        set_timer,  # set timer that after given time calls the given function with given parameters. repeats itself until reset_timer call
        reset_timer,
    Events:
        Init,
        NewRoundEvent,
        OnMessageReceive,
    Needs:
        adjacent_nodes_dict: adjnd
        received_messages_dict: rmd  # for storing this round's messages

    OnInit: () do
        round = 0
        NewRoundEvent()

    NewRoundEvent () do
        round += 1
        unreceived_count = len(adjnd)
        set_neighboors_not_received()
        do_round_process()  # doing the algorithm event since it received every needed mesage
        set_received_rmd_messages_to_none()
        current_round_messages = create_current_round_messages()
        send_messages_to_neighboors(round, current_round_messages)
        set_timer(send_messages_to_neighboors, round, current_round_messages)

    OnMessageReceive: ( neighboor_round, neighboor_node, message ) do
        If neighboor_round == round and adjnd[neighboor_node] == False:
            adjnd[neighboor_node] = true
            unreceived_count -= 1
            rmd[neighboor_node] = message
            If unreceived_count == 0:
                reset_timer()
                NewRoundEvent()


- In the alpha synchronizer, every node sends a message to every neighbor in every round(so that neighboor can synchronize with it)
  - If no message needs to be sent to that neighboor, node sends a dummy message to that neighboor.
- The receiver waits until it receives a message from every neighbor for a particular round before proceeding to the next round.

Beta
---------------------------------

An example distributed algorithm for global synchronization is presented in  :ref:`Algorithm <BetaAlgorithmLabel>`.

.. _BetaAlgorithmLabel:

.. code-block:: RST
    :linenos:
    :caption: Awerbuch's Beta algorithm.
    

    Implements:
    Uses:
        create_current_round_messages,  # creates messages for current round
        do_round_process,
        set_received_rmd_messages_to_none,
        send_messages_to_neighboors,
        is_root,
        broadcast_go,
    Events:
        Init,
        NewRoundEvent,
        OnMessageReceive,
        OnOKReceive,
        NodeRoundEndCheck,
    Needs:
        parent_node,        # if parent node is none it is root
        adjacent_node_count: adj_count,
        children_node_count: child_count,
        received_messages_dict: rmd  # for storing this round's messages

    OnInit: () do
        NewRoundEvent()

    NewRoundEvent () do
        unreceived_count = adj_count
        unreceived_OK_count = child_count
        do_round_process()  # doing the algorithm event since it received every needed mesage
        set_received_rmd_messages_to_none()
        current_round_messages = create_current_round_messages()
        send_messages_to_neighboors(round, current_round_messages)

    OnMessageReceive: ( neighboor_node, message ) do
        unreceived_count -= 1
        rmd[neighboor_node] = message
        NodeRoundEndCheck()

    OnOKReceive: ( child_node ) do
        unreceived_OK_count -= 1
        NodeRoundEndCheck()

    NodeRoundEndCheck: () do
        If unreceived_count == 0 and unreceived_OK_count == 0:
            If is_root():
                broadcast_go()  # every node will activate newroundevent when they receive it
                NewRoundEvent()
            Else:
                SendOK(parent_node)


- In the beta synchronizer, messages sent by processes are acknowledged by their receivers.
- Senders wait until they receive acknowledgments (ACKs) from all receivers for the messages they sent in a particular round.
  - That is why since its a reliable connection we act like receive happens only ones(think of TCP)
- Once all ACKs are received and all OKs from child nodes are received, the node sends ok to parent node.
- Once root receives OK from its parent nodes it broadcasts GO signifying the start of new round

Note: I didn't control round counts and other things because the syncronized messaging will ensure those by itself.



Gamma
---------------------------------

- The gamma synchronizer is the merge of both alpha and beta synchronizers. It does this by having multiple roots which all have their own spanning trees where:
    - The beta algorithm runs within each tree 
    - The alpha algorithm runs between trees
- In here in addition to beta when the root of a tree gets all acks and OKs, it sends ready to the roots of all adjacent trees (and itself).
    - Two trees are considered to be adjacent when any of their members are adjacent.
- When the root is READY(which means every one of its descendants are OK). And all their adjacent nodes are READY(which it knows by receiving their message). It broadcasts go down its tree

Example
~~~~~~~~

Provide an example for the distributed algorithm.

Correctness
~~~~~~~~~~~

- Alpha: guarantees local synchronization, ensuring that no process proceeds to the next round since it waits for all its neighboors which means it knows every neighboor finished its previous message neighbors have completed the current round.
- Beta: guarantees global synchronization, ensuring that no process proceeds to the next round since everyone waits for root and root waits for OKs from its children And since its children being OK would recursively prove that every other node is OK this algorithm is correct.
- Gamma:
    - As in the alpha synchronizer, we can show that no root process to the next round unless it and all its neighbors are in ready state, which happens only after both all nodes in the root's tree and all their neighbors have received acks for all messages. This proves that within nodes there is local syncronization.
    - And since every tree uses beta syncronizer in itself we can see that within that tree networkwise syncronization has been achieved.
    - Since every connection of a node inside 1 tree to another implies connection between roots the syncronization of roots will be achieved. While this sentence does not prove its correctnes, the idea of thinking every tree as a giant node will since it will make the situation same as a normal alpha synchronizer.

Complexity 
~~~~~~~~~~

Edge Count is E, Node count is N, Round Count is R,

- Alpha:
    - Message Complexity: O(R*E). Because every round we send messages to every neighboor so 2E messages are sent(at least). There will be multiple sends but this should be under a constant count 
    - Time Complexity: O(R)
- Beta:
    - Message Complexity: O(R*(E+N)) but since N is always less than E it is actually O(R*E)
    - Time Complexity: O(R*(highest distance from root to a leaf)). So it depends on the network in a linked list like tree it will be O(R*N) but in a root centered and divided network(in best case) O(R*log(N))
- Gamma:
    - Message Complexity: O(R*E) there are more calculations but the complexity doesn't change.
    - Time Complexity: O(R* highest of the highest distance from root to leaf between trees).

But if we really want to analyze gamma:
- O(R*E_roots) messages for messages between roots. O(R) time spend between roots
- O(R*E_tree) messages for messages within trees. O(R*(highest distance from root to a leaf)) time is spend within the tree
    - (dont add + N it doesn't change anything comlexitywise)

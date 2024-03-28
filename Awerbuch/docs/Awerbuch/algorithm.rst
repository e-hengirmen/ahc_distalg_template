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

- Alpha:
- Beta:
- Gamma:



.. admonition:: EXAMPLE 

    Snapshot algorithms are fundamental tools in distributed systems, enabling the capture of consistent global states during system execution. These snapshots provide insights into the system's behavior, facilitating various tasks such as debugging, recovery from failures, and monitoring for properties like deadlock or termination. In this section, we delve into snapshot algorithms, focusing on two prominent ones: the Chandy-Lamport algorithm and the Lai-Yang algorithm. We will present the principles behind these algorithms, their implementation details, and compare their strengths and weaknesses.

    **Chandy-Lamport Snapshot Algorithm:**

    The Chandy-Lamport :ref:`Algorithm <ChandyLamportSnapshotAlgorithm>` [Lamport1985]_ , proposed by Leslie Lamport and K. Mani Chandy, aims to capture a consistent global state of a distributed system without halting its execution. It operates by injecting markers into the communication channels between processes, which propagate throughout the system, collecting local states as they traverse. Upon reaching all processes, these markers signify the completion of a global snapshot. This algorithm requires FIFO channels. There are no failures and all messages arrive intact and only once. Any process may initiate the snapshot algorithm. The snapshot algorithm does not interfere with the normal execution of the processes. Each process in the system records its local state and the state of its incoming channels.

    1. **Marker Propagation:** When a process initiates a snapshot, it sends markers along its outgoing communication channels.
    2. **Recording Local States:** Each process records its local state upon receiving a marker and continues forwarding it.
    3. **Snapshot Construction:** When a process receives markers from all incoming channels, it captures its local state along with the incoming messages as a part of the global snapshot.
    4. **Termination Detection:** The algorithm ensures that all markers have traversed the system, indicating the completion of the snapshot.


    .. _ChandyLamportSnapshotAlgorithm:

    .. code-block:: RST
        :linenos:
        :caption: Chandy-Lamport Snapshot Algorithm [Fokking2013]_.
                
        bool recordedp, markerp[c] for all incoming channels c of p; 
        mess-queue statep[c] for all incoming channels c of p;

        If p wants to initiate a snapshot 
            perform procedure TakeSnapshotp;

        If p receives a basic message m through an incoming channel c0
        if recordedp = true and markerp[c0] = false then 
            statep[c0] ← append(statep[c0],m);
        end if

        If p receives ⟨marker⟩ through an incoming channel c0
            perform procedure TakeSnapshotp;
            markerp[c0] ← true;
            if markerp[c] = true for all incoming channels c of p then
                terminate; 
            end if

        Procedure TakeSnapshotp
        if recordedp = false then
            recordedp ← true;
            send ⟨marker⟩ into each outgoing channel of p; 
            take a local snapshot of the state of p;
        end if


    **Example**

    DRAW FIGURES REPRESENTING THE EXAMPLE AND EXPLAIN USING THE FIGURE. Imagine a distributed system with three processes, labeled Process A, Process B, and Process C, connected by communication channels. When Process A initiates a snapshot, it sends a marker along its outgoing channel. Upon receiving the marker, Process B marks its local state and forwards the marker to Process C. Similarly, Process C marks its state upon receiving the marker. As the marker propagates back through the channels, each process records the messages it sends or receives after marking its state. Finally, once the marker returns to Process A, it collects the markers and recorded states from all processes to construct a consistent global snapshot of the distributed system. This example demonstrates how the Chandy-Lamport algorithm captures a snapshot without halting the system's execution, facilitating analysis and debugging in distributed environments.


    **Correctness:**
    
    *Termination (liveness)*: As each process initiates a snapshot and sends at most one marker message, the snapshot algorithm activity terminates within a finite timeframe. If process p has taken a snapshot by this point, and q is a neighbor of p, then q has also taken a snapshot. This is because the marker message sent by p has been received by q, prompting q to take a snapshot if it hadn't already done so. Since at least one process initiated the algorithm, at least one process has taken a snapshot; moreover, the network's connectivity ensures that all processes have taken a snapshot [Tel2001]_.

    *Correctness*: We need to demonstrate that the resulting snapshot is feasible, meaning that each post-shot (basic) message is received during a post-shot event. Consider a post-shot message, denoted as m, sent from process p to process q. Before transmitting m, process p captured a local snapshot and dispatched a marker message to all its neighbors, including q. As the channels are FIFO (first-in-first-out), q received this marker message before receiving m. As per the algorithm's protocol, q took its snapshot upon receiving this marker message or earlier. Consequently, the receipt of m by q constitutes a post-shot event [Tel2001]_.

    **Complexity:**

    1. **Time Complexity**  The Chandy-Lamport :ref:`Algorithm <ChandyLamportSnapshotAlgorithm>` takes at most O(D) time units to complete where D is ...
    2. **Message Complexity:** The Chandy-Lamport :ref:`Algorithm <ChandyLamportSnapshotAlgorithm>` requires 2|E| control messages.


    **Lai-Yang Snapshot Algorithm:**

    The Lai-Yang algorithm also captures a consistent global snapshot of a distributed system. Lai and Yang proposed a modification of Chandy-Lamport's algorithm for distributed snapshot on a network of processes where the channels need not be FIFO. ALGORTHM, FURTHER DETAILS

.. [Awerbuch1985] Baruch Awerbuch. 1985. Complexity of network synchronization. J. ACM 32, 4 (Oct. 1985), 804–823.


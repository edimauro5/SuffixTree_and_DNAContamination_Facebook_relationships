from graph import Graph


def diffCut(Z, V_sub_Z, vert_mod, graph):
    """ The purpose of this function is to calculate the difference between 
        the cut (sum of weights) between Z and V_sub_Z (with vert_mod added or removed)
                                        &
        the cut between old Z and old V_sub_Z (without vert_mod added or removed)

    Args:
        Z (set): Python set of considered vertices
        V_sub_Z (set): Python set of all vertices except those in Z
        vert_mod (Vertex): Vertex modified in sets
        graph (Graph): Graph containing all vertices and edges

    Returns:
        (int): Difference between cut values
    """
    diff_cuts = 0
    for e in graph.incident_edges(vert_mod):
        if (e._origin != vert_mod and e._origin._element in V_sub_Z) or (e._destination != vert_mod and e._destination._element in V_sub_Z):
            diff_cuts += e.element()
        elif (e._origin != vert_mod and e._origin._element in Z) or (e._destination != vert_mod and e._destination._element in Z):
            diff_cuts -= e.element()
    return diff_cuts


def facebook_enmy(V, E):
    """ The purpose of this function is to obtain by who the set of Democrats and the 
        set of Republicans are formed depending on voters and their enmities. 
        The level of enmity within each group has to be as low as possible, and the 
        level of enmity among the two groups has to be as large as possible. 
        Besides, the level of enmity in a set of voters is computed as the sum of 
        enmities among each pair of these voters that are friends on the social network

    Args:
        V (set): Python set of voters
        E (dict): Python dictionary whose keys are Python tuples representing pairs 
            of voters that have a friendship relationship on Facebook, and whose values 
            represent the enmity level that Facebook assigned to the corresponding pair

    Returns:
        (set): Python set of voters for Democrats
        (set): Python set of voters for Republicans
    """
    graph = Graph()
    v_dict = dict()
    K = set()
    V_sub_K = V.copy()
    C = V.copy()
    V_sub_C = set()

    # fill v_dict with every vertex inserted in graph
    for vertex in V:
        v_dict[vertex] = graph.insert_vertex(vertex)

    # insert every edge in graph
    for edge in E.keys():
        graph.insert_edge(v_dict[edge[0]], v_dict[edge[1]], E.get(edge))

    # execute the diffCut function on every vertex in V
    for vertex in V:
        # temporary add vertex in K and remove it from V_sub_K to calculate the gain
        K.add(vertex)
        V_sub_K.remove(vertex)

        # temporary remove vertex from C and add it in V_sub_C to calculate the gain
        C.remove(vertex)
        V_sub_C.add(vertex)

        # compare the gains to determine where the vertex should be
        if diffCut(K, V_sub_K, v_dict[vertex], graph) >= diffCut(V_sub_C, C, v_dict[vertex], graph):
            # revert changes in sets C and V_sub_C
            C.add(vertex)
            V_sub_C.remove(vertex)
        else:
            # revert changes in sets K and V_sub_K
            K.remove(vertex)
            V_sub_K.add(vertex)

    return K, V - K


def BFS_reduced(g, s, d, discovered):
    """ Perform BFS of the undiscovered portion of Graph g starting at Vertex s
        (should be mapped to None prior to the call) and ending at Vertex d.
        Newly discovered vertices will be added to discovered as a result

    Args:
        g (Graph): Graph containing all vertices and edges
        s (Vertex): Vertex from which to start
        d (Vertex): Vertex that determines the end
        discovered (dict): Python dictionary that maps each vertex to the edge
            that was used to discover it during the BFS
    """
    level = [s]                                         # first level includes only s
    while len(level) > 0:
        next_level = []                                 # prepare to gather newly found vertices
        for u in level:
            ud_edge = g.get_edge(u, d)
            if(ud_edge is not None):                    # exist an edge from u to d
                if ud_edge._element != 0:
                    discovered[d] = ud_edge             # ud_edge is the tree edge that discovered d
                    return
            for e in g.incident_edges(u):               # for every outgoing edge from u
                if e._element != 0:
                    v = e.opposite(u)
                    if v not in discovered:             # v is an unvisited vertex
                        discovered[v] = e               # e is the tree edge that discovered v
                        next_level.append(v)            # v will be further considered in next pass
        level = next_level                              # relabel 'next' level to become current


def facebook_friend(V, E):
    """ The purpose of this function is to obtain by who is formed the set of 
        Democrats and the set of Republicans depending on voters and their friendships.
        The level of friendship within each group has to be as large as possible, and the 
        level of friendship among the two groups has to be as low as possible.
        Besides, the level of friendship in a set of voters is computed as the sum of 
        friendships among each pair of these voters that are friends on the social network.
        Moreover, the function has to maximize the total likelihood of returned groups, 
        where the total likelihood is the sum over all voters v of the likelihood that v
        votes for the candidate of the group at which it is assigned

    Args:
        V (dict): Python dictionary whose keys represent voters, and values are Python
            tuples with the first entry being the likelihood for Democrats and the second
            being the likelihood for Republicans
        E (dict): Python dictionary whose keys represent pairs of voters that have a
            friendness relationship on Facebook, and whose values represent the friendship 
            level that Facebook assigned to the corresponding pair

    Returns:
        (set): Python set of voters for Democrats
        (set): Python set of voters for Republicans
    """
    graph = Graph(True)                                 # there is the Arg True to create a directed graph
    v_dict = dict()
    Dem = graph.insert_vertex("Dem")                    # insert the starting vertex named Dem
    Rep = graph.insert_vertex("Rep")                    # insert the ending vertex named Rep

    # insert every vertex in graph and in v_dict and insert the edges from Dem and to Rep using the likelihoods
    for vertex in V:
        v_app = graph.insert_vertex(vertex)
        v_dict[vertex] = v_app
        graph.insert_edge(Dem, v_app, V[vertex][0])
        graph.insert_edge(v_app, Dem, 0)                # the edge from the added vertex to Dem is initially non-existent
        graph.insert_edge(v_app, Rep, V[vertex][1])
        graph.insert_edge(Rep, v_app, 0)                # the edge from Rep to the added vertex is initially non-existent

    # insert every forward and backward edge between vertices because the graph is directed
    for edge in E:
        graph.insert_edge(v_dict.get(edge[0]), v_dict.get(edge[1]), E[edge])
        graph.insert_edge(v_dict.get(edge[1]), v_dict.get(edge[0]), E[edge])

    # prepare the dictionary for the BFS_reduced function
    discovered = dict()
    discovered[Dem] = None
    BFS_reduced(graph, Dem, Rep, discovered)            # find the first path from Dem to Rep

    # update the graph structure until there are no more edges that link Dem to Rep
    while discovered.get(Rep) is not None:
        edge = discovered.get(Rep)
        min = edge.element()                            # actually the minimum weight is that of the actual edge linked to Rep

        edge = discovered.get(edge._origin)
        while edge is not None:
            if (edge.element() < min):                  # find the minimum weight of edge's path
                min = edge.element()
            edge = discovered.get(edge._origin)

        edge = discovered.get(Rep)
        while edge is not None:
            edge._element -= min                                                # update the weight of forward edges
            graph.get_edge(edge._destination, edge._origin)._element += min     # update the weight of backward edges
            edge = discovered.get(edge._origin)

        discovered = {}
        discovered[Dem] = None
        BFS_reduced(graph, Dem, Rep, discovered)        # find the next path from Dem to Rep

    D = set()

    for vertex in discovered.keys():
        if vertex != Dem:
            D.add(vertex.element())                     # add vertices to Democrats set

    R = V.keys() - D
    return D, R

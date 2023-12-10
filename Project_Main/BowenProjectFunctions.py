import numpy as np
import networkx as nx


def to_int(l):
    """
    Simple function that takes in a list of strings and returns a string of integers
    """
    return [int(i) for i in l]


def route_id(i, node_list):
    """
    Function that returns list of ID's given input route ID number

    :param i: the input route id
    :param node_list: list of the stations
    :return: list of the station ID for that route i
    """
    return [j for j in node_list if str(j)[0:3] == f"80{i}"]


def station_id_to_index(station_id_list, nodelist):
    """
    Will get a list of the indices of your stations in the node list

    :param nodelist: ordered list of the nodes from NetworkX graph object
    :param station_id_list: the stop id of your stations
    :return: the list of the indices correlated with the stop id in node list
    """
    NL_indices = []

    for id in station_id_list:
        NL_indices.append((id, nodelist.index(id)))

    return NL_indices


def index_to_station_id(index_list, nodelist):
    """
    Will get a list of the station id of your index in the node list

    :param nodelist: ordered list of the nodes from NetworkX graph object
    :param index_list: the list of indices
    :return: the list of station id's correlated to node list
    """
    station_list = []

    for i in index_list:
        station_list.append(nodelist[i])

    return station_list


def rlp(f, adjacency, epsilon, max_l=3):
    """
    Implementing the RLP algorithm into python

    :param f: 1xN vector, components corresponding to target nodes are 1 and 0 otherwise
    :param adjacency: NxN adjacency matrix of our network
    :param epsilon: tunable parameter controlling weight of the paths with different lengths
    :param max_l: furthest nodes we consider
    :return: 1xN vector that ranks the importance of nodes on our network
    """
    s_rlp = np.zeros(len(f))

    for l in range(0, max_l):
        summation_iteration = np.power(epsilon, l) * f @ np.linalg.matrix_power(adjacency, l + 1)
        s_rlp = np.add(s_rlp, summation_iteration)

    return s_rlp


def merge(list1, list2):
    """
    We will merge two lists together.
    The objects at the same index will be joined into tuples and inserted into a list.

    :param list1: the first list to be merged
    :param list2: the second list to be merged
    :return: list of tuples
    """
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    return merged_list


def get_ranked_stations(array, nodelist):
    """
    Take the ranking and convert the numbers to stations.

    :param nodelist: ordered list of the nodes from NetworkX graph object
    :param array: the calculated stations
    :return: the station's that are important
    """

    # The indices of the non-zero array values
    indices = list(np.nonzero(array)[1])

    # Get the corresponding values at all the non-zero indices
    values = []
    for i in indices:
        values.append(array[0][i])

    # obtain the station id's from the obtained indices
    stations = index_to_station_id(indices, nodelist)

    # Create list of tuples (station, value of station)
    merged = merge(stations, values)
    # Sort on values, highest values to lowest
    merged.sort(key=lambda x: x[1], reverse=True)

    # Grab first element of each tuple
    station_sorted = (list(zip(*merged))[0])

    return station_sorted


def normalize_graph(G):
    """
    Take a graph object and normalize all its edges to a normal distrubution centered at 1 and std deviation of 1/5.

    :param G: Graph object from NetworkX
    :return: Normalized graph object from NetworkX
    """
    # Get list of old edge weights
    old_edge_weights = [data['weight'] for node1, node2, data in G.edges(data=True)]
    # Calculate mean of old edge weights
    mean_old_edge_weights = sum(old_edge_weights) / len(old_edge_weights)

    # importing Statistics module
    import statistics
    # Calculate standard deviation of old edge weights
    stddev_old_edge_weights = statistics.stdev(old_edge_weights)

    # Create new graph we will add edges to
    new_G = nx.Graph()
    new_G.add_nodes_from(list(G))
    for node1, node2, data in G.edges(data=True):
        # Z-score
        std_weight = (data['weight'] - mean_old_edge_weights) / stddev_old_edge_weights
        # New standard deviation of: std_weight/5
        std_weight = std_weight / 5
        # New mean of 1
        std_weight = std_weight + 1

        # if less than 0, turn to 0
        if std_weight < 0:
            std_weight = 0

        # Add new weights to new graph
        new_G.add_edge(node1, node2, weight=std_weight)

    return new_G

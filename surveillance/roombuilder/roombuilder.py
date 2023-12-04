"""
Used for making room maps and graphs
"""
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import copy
from typing import List
import pickle


class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        renamed_module = module
        if module == 'roombuilder':
            renamed_module = 'surveillance.roombuilder.roombuilder'

        return super(RenameUnpickler, self).find_class(renamed_module, name)


class RoomMap:
    def __init__(self, box_matrix):

        # Box grid: 0 is solid, 1 is empty, 2 is marker (considered empty)
        self.map = box_matrix

        self.BOX_SIZE = 50  # In pixels
        self.BOXES = [np.zeros((self.BOX_SIZE, self.BOX_SIZE)),
                      np.ones((self.BOX_SIZE, self.BOX_SIZE)),
                      np.ones((self.BOX_SIZE, self.BOX_SIZE)) * 0.5]

        # Get total dimensions from map matrix dimensions
        self.DIM_X = len(box_matrix[0])
        self.DIM_Y = len(box_matrix)

        self.graph = self.make_graph()
        self.graph = self._identify_graph()
        self.reduced_graph = self.reduce_graph()

    def make_map_image(self, filename: str) -> None:
        """
        Makes an image visualization of the map
        Filename must contain '.png'
        """
        # Build image from map
        img = np.array([]).reshape((0, self.DIM_X * self.BOX_SIZE))
        # Make pixel matrix
        for x in range(len(self.map)):
            row = np.array([]).reshape((self.BOX_SIZE, 0))
            for y in range(len(self.map[x])):
                row = np.hstack((row, self.BOXES[self.map[x][y]]))
            img = np.vstack((img, row))

        # Create image PNG file
        img = img * 255  # Convert 0-1 grayscale to 0-255 grayscale
        cv.imwrite(filename, img)

    def save(self, filename: str) -> None:
        """
        Serialize this object to a file
        """
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    def load(self, filename: str):
        """
        Load a serialized RoomMap object from a file
        """
        with open(filename, 'rb') as f:
            return RenameUnpickler(f).load()

    def _identify_graph(self):
        """
        Runs _identify_node() on all nodes of the unreduced graph and stores the
        result in the 'type' field of each node
        """

        G = self.graph

        for node in G:
            G[node]['raw_type'] = self._identify_node(node)

        return G

    def make_graph(self) -> dict:
        """
        Returns a simple graph representation of the map
        """

        graph = {}

        nodes = np.reshape(list(range(self.DIM_X * self.DIM_Y)), (self.DIM_Y, self.DIM_X))
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[x][y] != 0:
                    graph[nodes[x][y]] = {
                        'pos': tuple([y, x]),
                        'neighbors': [],  # Contains all neighbors of the node
                        'raw_type': 'default', # Contains a string indentifying the unreduced node type
                        'nbr_str': [],  # Contains neighbors directly up, down, left and right
                        'nbr_diag': []} # Contains neighbors that connect diagonally
                    neighbors = [(x-1, y), (x, y-1), (x+1, y), (x, y+1)]
                    for pos in neighbors:
                        if self.map[pos[0]][pos[1]] != 0:
                            graph[nodes[x][y]]['neighbors'].append(nodes[pos[0]][pos[1]])
                            graph[nodes[x][y]]['nbr_str'].append(nodes[pos[0]][pos[1]])

                    # Check diagonal conectivity:
                    diagonals = [(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)]
                    corners = [
                        [(x - 1, y), (x, y - 1)],
                        [(x + 1, y), (x, y - 1)],
                        [(x - 1, y), (x, y + 1)],
                        [(x + 1, y), (x, y + 1)]]

                    for i, pos in enumerate(diagonals):
                        if self.map[pos[0]][pos[1]] != 0:
                            if (self.map[corners[i][0][0]][corners[i][0][1]] != 0) and \
                               (self.map[corners[i][1][0]][corners[i][1][1]] != 0):
                                # Diagonals only connect if they do not intersect a corner
                                graph[nodes[x][y]]['neighbors'].append(nodes[pos[0]][pos[1]])
                                graph[nodes[x][y]]['nbr_diag'].append(nodes[pos[0]][pos[1]])

        return graph

    def _identify_node(self, node: int) -> str:
        """
        Returns a string that identifies the type of node given
        """
        G = self.graph
        type = 'default'  # Default type for node

        # For nodes with two straight neighbors, get neighbor coordinates and check geometry
        aligned = True
        if len(G[node]['nbr_str']) == 2:  # Hallway corner nodes
            xn1 = G[G[node]['nbr_str'][0]]['pos'][0]
            xn2 = G[G[node]['nbr_str'][1]]['pos'][0]
            yn1 = G[G[node]['nbr_str'][0]]['pos'][1]
            yn2 = G[G[node]['nbr_str'][1]]['pos'][1]
            if not (xn1 == xn2) and not (yn1 == yn2):
                aligned = False

        # Room nodes
        if len(G[node]['neighbors']) > 4:  # Room nodes
            type = 'room'

        # Corner nodes
        if len(G[node]['nbr_str']) == 2:  # Concave corner nodes
            if len(G[node]['nbr_diag']) > 0:  # Make sure it is not a hallway corner
                if not aligned:
                    type = 'corner_ccv'
        elif (len(G[node]['nbr_str']) == 3) and (len(G[node]['nbr_diag']) == 1):  # Doorway corners
            type = 'corner_drw'
        elif (len(G[node]['nbr_str']) == 4) and (len(G[node]['nbr_diag']) == 3):  # Convex corners
            type = 'corner_cvx'

        # Hallway nodes
        if len(G[node]['nbr_diag']) == 0:  # Check it is a hallway node
            if len(G[node]['nbr_str']) == 1:  # Dead ends
                type = 'dead_end'
            elif len(G[node]['nbr_str']) == 2:  # Hallway corner nodes
                if not aligned:
                    type = 'L_junction'
                else:
                    type = 'hallway'
            elif len(G[node]['nbr_str']) == 3:  # T junction nodes
                type = 'T_junction'
            elif len(G[node]['nbr_str']) == 4:  # X junction nodes
                type = 'X_junction'

        return type

    def _is_cluster_node(self, node: int) -> bool:
        """
        Returns True if given node is part of a room cluster in the main graph
        (Room cluster nodes = room nodes and corner nodes)
        False otherwise
        """
        type = self._identify_node(node)

        # Room nodes
        if type == 'room':  # Room nodes
            return True

        # Corner nodes
        if (type == 'corner_ccv') | (type == 'corner_cvx') | (type == 'corner_drw'):
            return True

        return False

    def _is_hallway_node(self, node: int) -> bool:
        """
        Returns True if given node is part of a straight hallway in the main graph
        False otherwise
        """
        type = self._identify_node(node)

        # Room nodes
        if type == 'hallway':  # Hallway nodes
            return True

        return False

    def _bfs(self, G, node: int) -> List[int]:
        """
        Performs BFS starting at given node, and returns the indexes of all explored nodes
        Used to find set of all nodes connected to input node. Does not keep track of
        parent nodes or terminate at any goal node. Fully explores the entire connected
        component of G that is accessible from given node.
        """
        Q = []  # Queue
        explored = set([node])  # List of explored nodes
        Q.append(node)

        while len(Q) != 0:
            v = Q.pop(0)  # Exctract node
            for nbr in G[v]['neighbors']:
                if nbr not in explored:
                    explored.add(nbr)
                    Q.append(nbr)

        return list(explored)

    def _is_exit_node(self, G, node: int, room: List[int]) -> bool:
        """
        Returns True if given node is an exit/doorway node conected to the given
        room cluster, in the given graph. False otherwise
        """

        for room_node in room:
            if node not in room:
                if room_node in G[node]['neighbors']:
                    return True

        return False

    def _remove_node_from_graph(self, G, node: int) -> dict:
        """
        Returns given graph with node removed and its neighbors disconencted
        """

        G_new = G

        for nbr in G[node]['neighbors']:
            G_new[nbr]['neighbors'].remove(node)  # Disconnect neighbors

        G_new.pop(node)  # Delete node

        return G_new

    def reduce_graph(self) -> dict:
        """
        Reduces the graph representation to one node per room
        """

        M = copy.deepcopy(self.graph)  # Minimal graph (M is reduced version of G)

        # 1. LOCATE AND REDUCE ROOMS  -------------------------------------------------
        G = self.graph

        # Find all room/corner nodes
        room_nodes = [node for node in G if self._is_cluster_node(node)]

        # Make graph that only contains room clusters
        G_split = copy.deepcopy(G)
        for node in G:
            if not self._is_cluster_node(node):
                G_split = self._remove_node_from_graph(G_split, node)

        # Split into individual room clusters
        rooms = []
        nodes_to_check = room_nodes
        while len(nodes_to_check) != 0:
            start_node = nodes_to_check[0]  # Pick start node
            cluster = self._bfs(G_split, start_node)  # Explore cluster
            rooms.append(cluster)
            for cluster_node in cluster:
                nodes_to_check.remove(cluster_node)  # Remove cluster nodes from nodes_to_check

        # Process each room cluster
        for room in rooms:
            # Find all exit nodes (doorway nodes that connect outside the cluster)
            exit_nodes = [node for node in G if self._is_exit_node(G, node, room)]

            # Delete all cluster room/corner nodes and insert new node at their avg location
            avg_x = np.average([G[node]['pos'][0] for node in room])  # Find avg x pos of cluster
            avg_y = np.average([G[node]['pos'][1] for node in room])  # Find avg y pos of cluster

            for node_to_remove in room:
                M = self._remove_node_from_graph(M, node_to_remove)  # Remove cluster nodes

            M[room[0]] = {'pos': tuple([avg_x, avg_y]),  # New node reuses one of the removed indexes
                          'neighbors': [],              # to ensure it uses a free index
                          'area': len(room), # Contains the area of the entire room (in boxes)
                          'type': 'room', # Marks this as a room
                   'is_dead_end': False}  # True if room only has 1 entry/exit

            # Set dead end flag
            if len(exit_nodes) == 1:
                M[room[0]]['is_dead_end'] = True

            # Reconnect exit nodes to new node (set neighbors)
            for exit_node in exit_nodes:
                M[room[0]]['neighbors'].append(exit_node)  # Connect room to exit
                M[exit_node]['neighbors'].append(room[0])  # Connect exit to room

        # Mark non-room nodes and cleanup
        for node in M:
            if 'type' not in M[node]:
                if self._identify_node(node) != 'hallway':
                    M[node]['type'] = 'junction'
                    M[node]['area'] = 1 # Set area of jucntions to 1 since it is not set earlier
                    M[node]['is_dead_end'] = False # Set dead end flag to false since it does not apply
                else:
                    M[node]['type'] = 'hallway'
            M[node].pop('nbr_str', None) # Meaningless in the reduced graph so it is removed
            M[node].pop('nbr_diag', None) # Meaningless in the reduced graph so it is removed
            M[node].pop('raw_type', None) # Meaningless in the reduced graph so it is removed

        # 2. LOCATE AND REDUCE HALLWAYS -------------------------------------------------
        G = copy.deepcopy(M)

        # Find all hallway nodes in reduced graph
        hallway_nodes = [node for node in G if self._is_hallway_node(node)]

        # Make graph that only contains hallway nodes
        G_split = copy.deepcopy(G)
        for node in G:
            if not self._is_hallway_node(node):
                G_split = self._remove_node_from_graph(G_split, node)

        # Split into individual hallway strings
        hallways = []
        nodes_to_check = hallway_nodes
        while len(nodes_to_check) != 0:
            start_node = nodes_to_check[0]  # Pick start node
            cluster = self._bfs(G_split, start_node)  # Explore cluster
            hallways.append(cluster)
            for cluster_node in cluster:
                nodes_to_check.remove(cluster_node)  # Remove cluster nodes from nodes_to_check

        # Process each hallway cluster
        for hallway in hallways:
            # Find all exit nodes (doorway nodes that connect outside the cluster)
            exit_nodes = [node for node in G if self._is_exit_node(G, node, hallway)]

            # Delete all cluster room/corner nodes and insert new node at their avg location
            avg_x = np.average([G[node]['pos'][0] for node in hallway])  # Find avg x pos of cluster
            avg_y = np.average([G[node]['pos'][1] for node in hallway])  # Find avg y pos of cluster

            for node_to_remove in hallway:
                M = self._remove_node_from_graph(M, node_to_remove)  # Remove cluster nodes

            M[hallway[0]] = {'pos': tuple([avg_x, avg_y]),  # New node reuses one of the removed indexes
                             'neighbors': [],  # to ensure it uses a free index
                             'area': len(hallway), # Contains the area/length of the entire hallway (in boxes)
                             'type': 'hallway', # Marks this as a room
                      'is_dead_end': False}     # Always false since it does not apply

            # Reconnect exit nodes to new node (set neighbors)
            for exit_node in exit_nodes:
                M[hallway[0]]['neighbors'].append(exit_node)  # Connect room to exit
                M[exit_node]['neighbors'].append(hallway[0])  # Connect exit to room

        return M

    def draw_box_grid(self) -> None:
        """
        Draws the map box grid on the current figure
        """
        plt.imshow(self.map, cmap='gray', vmin=0, vmax=1)

    def draw_graph(self, apply_color: bool = False) -> None:
        """
        Draws the graph network on the current figure
        """

        COLORS = {
            'default': 'black',  # Default node color (unmarked)
            'corner_ccv': 'red',    # Concave (inside) corner node color
            'corner_cvx': 'red',    # Convex (outside) corner node color
            'corner_drw': 'red',    # Doorway corner node color
            'hallway': 'black',  # Straight hallway node color
            'L_junction': 'green',  # Hallway L-junction node color
            'T_junction': 'green',  # Hallway T-junction node color
            'X_junction': 'green',  # Hallway X-junction node color
            'dead_end': 'purple',  # Hallway X-junction node color
            'room': 'orange'
        }  # Room node color
        MARK_CORNERS = True  # Apply special color to corner nodes
        MARK_ROOMS = True  # Apply special color to room nodes
        MARK_JUNCTIONS = True  # Apply special color to hallway junction nodes (Bends, T-junctions, etc.)
        MARK_HALLWAYS = True  # Apply special color to hallway nodes

        G = self.graph

        # Plot graph edges
        for node in G:
            for neighbor in G[node]['neighbors']:
                x = [G[node]['pos'][0], G[neighbor]['pos'][0]]
                y = [G[node]['pos'][1], G[neighbor]['pos'][1]]
                plt.plot(x, y, color='black')

        # Compute colors and positions for all nodes
        node_colors = {}  # Maps node positions to colors

        for node in G:
            x = G[node]['pos'][0]
            y = G[node]['pos'][1]

            node_colors[tuple([x, y])] = COLORS['default']

            if apply_color:  # Apply color scheme to different node types
                type = self._identify_node(node)

                # Mark room nodes
                if MARK_ROOMS:
                    if type == 'room':
                        node_colors[tuple([x, y])] = COLORS[type]

                # Mark corner nodes
                if MARK_CORNERS:
                    if type in ['corner_ccv', 'corner_cvx', 'corner_drw']:
                        node_colors[tuple([x, y])] = COLORS[type]

                # Mark hallway junction nodes
                if MARK_JUNCTIONS:
                    if type in ['L_junction', 'T_junction', 'X_junction', 'dead_end']:
                        node_colors[tuple([x, y])] = COLORS[type]

                # Mark hallway nodes
                if MARK_HALLWAYS:
                    if type == 'hallway':
                        node_colors[tuple([x, y])] = COLORS[type]

        # Plot graph nodes with respective color
        for node in node_colors:
            plt.plot(node[0], node[1], marker='o', color=node_colors[node])

    def draw_reduced_graph(self, apply_color: bool = True, apply_scaling: bool = True):
        """
        Draws the reduced graph network on the current figure
        """

        COLORS = {'default': 'black',  # Default node color (unmarked)
                     'room': 'red',    # Room node color
                 'dead_end': 'orange', # Dead end room node color
                 'junction': 'green',  # Junction node color
                  'hallway': 'black'}  # Hallway node color

        G = self.reduced_graph

        # Plot graph edges
        for node in G:
            for neighbor in G[node]['neighbors']:
                x = [G[node]['pos'][0], G[neighbor]['pos'][0]]
                y = [G[node]['pos'][1], G[neighbor]['pos'][1]]
                plt.plot(x, y, color='black')

        # Compute colors and positions for all nodes
        node_colors = {}  # Maps node positions to color/area pairs

        for node in G:
            x = G[node]['pos'][0]
            y = G[node]['pos'][1]

            node_colors[tuple([x, y])] = tuple([COLORS['default'], G[node]['area']])

            if apply_color == True:
                # Mark nodes with appropriate colors, area value, and dead end flags
                if G[node]['is_dead_end'] == True:
                    node_colors[tuple([x, y])] = tuple([COLORS['dead_end'], G[node]['area']])
                else:
                    node_colors[tuple([x, y])] = tuple([COLORS[G[node]['type']], G[node]['area']])

        # Plot graph nodes with respective color
        for node in node_colors:
            if apply_scaling == True:
                plt.plot(node[0], node[1], marker='o',
                         color=node_colors[node][0], markersize=node_colors[node][1])
            else:
                plt.plot(node[0], node[1], marker='o', color=node_colors[node][0])

    def plot_map(self, plot_grid: bool = True, plot_graph: bool = False, plot_reduced_graph: bool = False,
                 apply_color: bool = False, apply_scaling: bool = True):
        """
        Displays a plot of the map, including the box grid and the graph
        as specified by the parameters
        """
        plt.figure()
        if plot_grid:
            self.draw_box_grid()
        if plot_graph:
            self.draw_graph(apply_color=apply_color)
        if plot_reduced_graph == True:
            self.draw_reduced_graph(apply_color=apply_color, apply_scaling=apply_scaling)
        plt.show()

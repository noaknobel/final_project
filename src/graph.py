from typing import Set, Any, Union


class Vertex:
    def __init__(self, vertex_id):
        self.id = vertex_id
        self.neighbors: Set[Vertex] = set()

    def add_neighbor(self, neighbor):
        if neighbor not in self.neighbors:
            self.neighbors.add(neighbor)

    def remove_neighbor(self, neighbor):
        if neighbor in self.neighbors:
            self.neighbors.remove(neighbor)


class DirectedGraph:
    def __init__(self):
        self.vertices = {}

    def add_vertex(self, vertex: Union[Vertex, Any]) -> bool:
        if isinstance(vertex, Vertex) and vertex.id not in self.vertices:
            self.vertices[vertex.id] = vertex
            return True
        else:
            return False

    def remove_vertex(self, vertex_id):
        if vertex_id in self.vertices:
            del self.vertices[vertex_id]
            for vertex in self.vertices.values():
                vertex.neighbors.discard(vertex_id)

    def add_edge(self, from_vertex, to_vertex):
        if from_vertex in self.vertices and to_vertex in self.vertices:
            self.vertices[from_vertex].add_neighbor(self.vertices[to_vertex])
            return True
        else:
            return False

    def remove_edge(self, from_vertex, to_vertex):
        if from_vertex in self.vertices and to_vertex in self.vertices:
            self.vertices[from_vertex].neighbors.discard(self.vertices[to_vertex])

    def get_vertices(self):
        return self.vertices.keys()

    def __iter__(self):
        return iter(self.vertices.values())

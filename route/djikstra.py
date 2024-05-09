class Graph():
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for _ in range(vertices)] for _ in range(vertices)]

    def printPath(self, parent, j):
        path = []
        if parent[j] == -1:
            path.append(j)
        else:
            path = self.printPath(parent, parent[j])
            path.append(j)
        return path

    def minDistance(self, dist, sptSet):
        min_dist = float('inf')
        min_index = -1
        for v in range(self.V):
            if dist[v] < min_dist and not sptSet[v]:
                min_dist = dist[v]
                min_index = v
        return min_index

    def dijkstra(self, src):
        dist = [float('inf')] * self.V
        dist[src] = 0
        sptSet = [False] * self.V
        parent = [-1] * self.V

        for _ in range(self.V):
            u = self.minDistance(dist, sptSet)
            sptSet[u] = True

            for v in range(self.V):
                if (
                    self.graph[u][v] > 0
                    and not sptSet[v]
                    and dist[v] > dist[u] + self.graph[u][v]
                ):
                    dist[v] = dist[u] + self.graph[u][v]
                    parent[v] = u
        return dist, parent

    def find_min_distance_node(self, dist, sptSet, nodes):
        min_dist = float('inf')
        min_node = None
        for node in nodes:
            if dist[node] < min_dist and not sptSet[node]:
                min_dist = dist[node]
                min_node = node
        return min_node

    def dijkstra_for_specific_nodes(self, src, nodes):
        dist = [float('inf')] * self.V
        dist[src] = 0
        sptSet = [False] * self.V

        for _ in range(self.V):
            u = self.find_min_distance_node(dist, sptSet, nodes)
            if u is None:
                break
            sptSet[u] = True

            for v in range(self.V):
                if (
                    self.graph[u][v] > 0
                    and not sptSet[v]
                    and dist[v] > dist[u] + self.graph[u][v]
                ):
                    dist[v] = dist[u] + self.graph[u][v]
        return dist



# Oluşturulan Grafın Matrissel İfadesi
g = Graph(11)

# buraya dbden rota gelecek
g.graph = [
    [0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 0, 1, 1, 0, 0, 3, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 2, 2, 0, 0, 0, 0],
    [0, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 0, 3, 0, 4, 0, 0],
    [0, 0, 2, 0, 0, 0, 1, 2, 0, 1, 0],
    [0, 3, 2, 0, 3, 1, 0, 0, 2, 0.5, 0],
    [0, 0, 0, 0, 0, 2, 0, 0, 0, 3, 0],
    [0, 0, 0, 0, 4, 0, 2, 0, 0, 3, 0],
    [0, 0, 0, 0, 0, 1, 0.5, 3, 3, 0, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0],
]
source_node = 0
# Database Erişimi İçin Gerekli Bilgiler

# Database'den Verilerin Koda Aktarılması için Kullanılan SQL KOdları

results = list()
specific_nodes = [result[0] for result in results]
route = []
while specific_nodes:
    distances, parent = g.dijkstra(source_node)
    min_distance_node = min(specific_nodes, key=lambda node: distances[node])
    path = g.printPath(parent, min_distance_node)
    route.extend(path)
    specific_nodes.remove(min_distance_node)
    source_node = min_distance_node

unique_route = []
prev_node = None
for node in route:
    if node != prev_node:
        unique_route.append(node)
    prev_node = node

# Tüm Düğümleri Metin Haline Getirmek için Kullanılan Satır
unique_route = [str(node) for node in unique_route]  
print("Yol: " + " -> ".join(unique_route))

# Düğümlere Ait Bilgilere Erişim SQL Sorguları
sql = f"SELECT ID, location FROM trashcans WHERE ID IN ({','.join(unique_route)})"
location_results = list()
location_dict = {row[0]: row[1] for row in location_results}
# Oklar ile Metinsel Yazımın Gerçekleştirildiği Satır
location_string = " -> ".join([location_dict[int(node)] for node in unique_route])
print(location_string)
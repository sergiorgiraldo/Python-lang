from cataclysm import consume
consume(globals())
graph = {
    "A": {"B": 10, "C": 4},
    "B": {"A": 1, "C": 2, "D": 5},
    "C": {"A": 4, "B": 2, "D": 9},
    "D": {"B": 5, "C": 1},
}

shortest_path = find_shortest_path_dijkstra(graph, "A", "D")
print(f"Shortest path: {shortest_path}")
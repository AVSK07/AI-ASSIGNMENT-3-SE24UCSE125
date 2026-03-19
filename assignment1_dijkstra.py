import heapq
from collections import defaultdict

# Road distances (in km) between major Indian cities
INDIAN_CITIES_GRAPH = {
    "Delhi": {
        "Jaipur": 281, "Agra": 206, "Chandigarh": 243, "Lucknow": 555,
        "Amritsar": 447, "Haridwar": 219, "Meerut": 70
    },
    "Mumbai": {
        "Pune": 149, "Surat": 284, "Nashik": 165, "Aurangabad": 335,
        "Goa": 590, "Ahmedabad": 524, "Hyderabad": 711
    },
    "Bangalore": {
        "Chennai": 346, "Hyderabad": 568, "Mysore": 144, "Mangalore": 352,
        "Coimbatore": 360, "Pune": 840
    },
    "Chennai": {
        "Bangalore": 346, "Hyderabad": 626, "Coimbatore": 497,
        "Madurai": 461, "Pondicherry": 162, "Vellore": 140
    },
    "Kolkata": {
        "Bhubaneswar": 443, "Patna": 594, "Siliguri": 596,
        "Ranchi": 390, "Guwahati": 1031
    },
    "Hyderabad": {
        "Bangalore": 568, "Chennai": 626, "Mumbai": 711, "Pune": 559,
        "Nagpur": 501, "Vijayawada": 274, "Warangal": 148
    },
    "Jaipur": {
        "Delhi": 281, "Agra": 232, "Ajmer": 135, "Jodhpur": 335,
        "Udaipur": 393, "Kota": 252
    },
    "Ahmedabad": {
        "Mumbai": 524, "Surat": 265, "Vadodara": 101, "Rajkot": 215,
        "Jaipur": 666
    },
    "Pune": {
        "Mumbai": 149, "Nashik": 210, "Aurangabad": 225,
        "Hyderabad": 559, "Bangalore": 840, "Kolhapur": 228
    },
    "Lucknow": {
        "Delhi": 555, "Kanpur": 82, "Agra": 363, "Varanasi": 286,
        "Allahabad": 205, "Gorakhpur": 271
    },
    "Agra": {
        "Delhi": 206, "Jaipur": 232, "Lucknow": 363, "Gwalior": 119,
        "Mathura": 56
    },
    "Varanasi": {
        "Lucknow": 286, "Allahabad": 121, "Patna": 233, "Gorakhpur": 221
    },
    "Patna": {
        "Varanasi": 233, "Kolkata": 594, "Ranchi": 328, "Gaya": 100
    },
    "Bhopal": {
        "Indore": 196, "Jabalpur": 297, "Gwalior": 400, "Nagpur": 357,
        "Ujjain": 187
    },
    "Nagpur": {
        "Bhopal": 357, "Hyderabad": 501, "Raipur": 295, "Aurangabad": 412
    },
    "Chandigarh": {
        "Delhi": 243, "Amritsar": 207, "Shimla": 114, "Ludhiana": 98
    },
    "Amritsar": {
        "Chandigarh": 207, "Delhi": 447, "Ludhiana": 132, "Jammu": 211
    },
    "Guwahati": {
        "Kolkata": 1031, "Shillong": 98, "Dibrugarh": 439
    },
    "Coimbatore": {
        "Bangalore": 360, "Chennai": 497, "Madurai": 209, "Ooty": 86
    },
    "Madurai": {
        "Chennai": 461, "Coimbatore": 209, "Kochi": 199, "Rameshwaram": 163
    },
    "Kochi": {
        "Madurai": 199, "Thiruvananthapuram": 200, "Kozhikode": 187
    },
    "Indore": {
        "Bhopal": 196, "Ujjain": 54, "Ahmedabad": 392, "Mumbai": 589
    },
    "Goa": {
        "Mumbai": 590, "Bangalore": 560, "Mangalore": 342
    },
    "Jodhpur": {
        "Jaipur": 335, "Ajmer": 200, "Udaipur": 246, "Bikaner": 252
    },
    "Surat": {
        "Mumbai": 284, "Ahmedabad": 265, "Vadodara": 153
    },
    "Vadodara": {
        "Ahmedabad": 101, "Surat": 153, "Mumbai": 410
    },
    "Allahabad": {
        "Lucknow": 205, "Varanasi": 121, "Kanpur": 193
    },
    "Kanpur": {
        "Lucknow": 82, "Agra": 285, "Allahabad": 193
    },
    "Raipur": {
        "Nagpur": 295, "Bhubaneswar": 440, "Jabalpur": 336
    },
    "Ranchi": {
        "Kolkata": 390, "Patna": 328, "Bhubaneswar": 395
    },
    "Bhubaneswar": {
        "Kolkata": 443, "Ranchi": 395, "Raipur": 440, "Visakhapatnam": 443
    },
    "Visakhapatnam": {
        "Bhubaneswar": 443, "Vijayawada": 349, "Hyderabad": 615
    },
    "Vijayawada": {
        "Hyderabad": 274, "Chennai": 427, "Visakhapatnam": 349
    },
    "Shimla": {
        "Chandigarh": 114, "Haridwar": 207
    },
    "Haridwar": {
        "Delhi": 219, "Shimla": 207, "Dehradun": 52
    },
    "Dehradun": {
        "Haridwar": 52, "Delhi": 255, "Mussoorie": 35
    },
    "Thiruvananthapuram": {
        "Kochi": 200, "Madurai": 245
    },
    "Mangalore": {
        "Bangalore": 352, "Goa": 342, "Kochi": 402, "Mysore": 233
    },
    "Mysore": {
        "Bangalore": 144, "Mangalore": 233, "Ooty": 120
    },
    "Aurangabad": {
        "Mumbai": 335, "Pune": 225, "Nagpur": 412
    },
    "Nashik": {
        "Mumbai": 165, "Pune": 210, "Ahmedabad": 430
    },
    "Jabalpur": {
        "Bhopal": 297, "Raipur": 336, "Nagpur": 309
    },
    "Gwalior": {
        "Agra": 119, "Bhopal": 400, "Jhansi": 99
    },
    "Udaipur": {
        "Jaipur": 393, "Jodhpur": 246, "Ahmedabad": 262
    },
    "Ajmer": {
        "Jaipur": 135, "Jodhpur": 200, "Delhi": 390
    },
    "Bikaner": {
        "Jodhpur": 252, "Jaipur": 330, "Delhi": 450
    },
    "Ludhiana": {
        "Chandigarh": 98, "Amritsar": 132, "Delhi": 310
    },
    "Jammu": {
        "Amritsar": 211, "Chandigarh": 310
    },
    "Siliguri": {
        "Kolkata": 596, "Guwahati": 430
    },
    "Kota": {
        "Jaipur": 252, "Bhopal": 392
    },
    "Rajkot": {
        "Ahmedabad": 215, "Surat": 270
    },
    "Gorakhpur": {
        "Lucknow": 271, "Varanasi": 221, "Patna": 260
    },
    "Gaya": {
        "Patna": 100, "Varanasi": 246
    },
    "Shillong": {
        "Guwahati": 98
    },
    "Meerut": {
        "Delhi": 70, "Agra": 200, "Haridwar": 150
    },
    "Kozhikode": {
        "Kochi": 187, "Mangalore": 245
    },
    "Ooty": {
        "Coimbatore": 86, "Mysore": 120
    },
    "Rameshwaram": {
        "Madurai": 163
    },
    "Pondicherry": {
        "Chennai": 162
    },
    "Vellore": {
        "Chennai": 140
    },
    "Kolhapur": {
        "Pune": 228
    },
    "Ujjain": {
        "Indore": 54, "Bhopal": 187
    },
    "Dibrugarh": {
        "Guwahati": 439
    },
    "Jhansi": {
        "Gwalior": 99, "Lucknow": 307
    },
    "Mussoorie": {
        "Dehradun": 35
    },
    "Mathura": {
        "Agra": 56, "Delhi": 150
    }
}
def dijkstra(graph, start, goal=None):
    """
    Dijkstra's Algorithm (Uniform-Cost Search)
    
    Args:
        graph: dict of dicts {city: {neighbor: distance}}
        start: starting city
        goal: target city (if None, finds paths to ALL cities)
    
    Returns:
        distances: dict of shortest distances from start to all cities
        predecessors: dict to reconstruct paths
    """
    priority_queue = [(0, start)]
    
    distances = {city: float('inf') for city in graph}
    distances[start] = 0
    
    predecessors = {city: None for city in graph}
    
    visited = set()
    
    nodes_explored = 0

    while priority_queue:
        current_cost, current_city = heapq.heappop(priority_queue)
        
        if current_city in visited:
            continue
        
        visited.add(current_city)
        nodes_explored += 1
        
        if goal and current_city == goal:
            break
        
        for neighbor, weight in graph.get(current_city, {}).items():
            if neighbor not in visited:
                new_cost = current_cost + weight
                if new_cost < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_cost
                    predecessors[neighbor] = current_city
                    heapq.heappush(priority_queue, (new_cost, neighbor))
    
    return distances, predecessors, nodes_explored


def reconstruct_path(predecessors, start, goal):
    """Reconstruct the shortest path from start to goal."""
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = predecessors.get(current)
    path.reverse()
    if path[0] == start:
        return path
    return [] 


def find_shortest_path(graph, start, goal):
    """Find and display shortest path between two cities."""
    if start not in graph:
        print(f"❌ '{start}' not found in the graph.")
        return
    if goal not in graph:
        print(f"❌ '{goal}' not found in the graph.")
        return
    
    distances, predecessors, nodes_explored = dijkstra(graph, start, goal)
    
    path = reconstruct_path(predecessors, start, goal)
    dist = distances.get(goal, float('inf'))
    
    print(f"\n{'='*60}")
    print(f"  Dijkstra's Shortest Path: {start} → {goal}")
    print(f"{'='*60}")
    
    if dist == float('inf') or not path:
        print(f"  ❌ No path found between {start} and {goal}.")
    else:
        print(f"  📍 Path   : {' → '.join(path)}")
        print(f"  📏 Distance: {dist} km")
        print(f"  🔢 Hops   : {len(path) - 1}")
        print(f"  🔍 Nodes explored: {nodes_explored}")
        
        # Show segment distances
        print(f"\n  Segment breakdown:")
        for i in range(len(path) - 1):
            seg_dist = graph[path[i]][path[i+1]]
            print(f"    {path[i]:20s} → {path[i+1]:20s}: {seg_dist} km")
    print(f"{'='*60}\n")


def find_all_shortest_paths(graph, start):
    """Find shortest paths from one city to ALL other cities."""
    if start not in graph:
        print(f"❌ '{start}' not found in the graph.")
        return
    
    distances, predecessors, nodes_explored = dijkstra(graph, start)
    
    print(f"\n{'='*70}")
    print(f"  All shortest paths from: {start}")
    print(f"{'='*70}")
    print(f"  {'Destination':<25} {'Distance (km)':>15}  Path")
    print(f"  {'-'*25} {'-'*15}  {'-'*25}")
    
    reachable = [(d, c) for c, d in distances.items() if d != float('inf') and c != start]
    reachable.sort()
    
    for dist, city in reachable:
        path = reconstruct_path(predecessors, start, city)
        path_str = " → ".join(path)
        if len(path_str) > 40:
            path_str = path_str[:37] + "..."
        print(f"  {city:<25} {dist:>15} km  {path_str}")
    
    unreachable = [c for c, d in distances.items() if d == float('inf') and c != start]
    if unreachable:
        print(f"\n  ❌ Unreachable cities: {', '.join(unreachable)}")
    
    print(f"\n  Total nodes explored: {nodes_explored}")
    print(f"{'='*70}\n")


def interactive_menu(graph):
    """Interactive menu for the user."""
    cities = sorted(graph.keys())
    
    print("\n" + "🇮🇳 " * 15)
    print("  DIJKSTRA'S ALGORITHM - INDIA ROAD NETWORK")
    print("🇮🇳 " * 15)
    print(f"\n  📊 Network: {len(cities)} cities, "
          f"{sum(len(v) for v in graph.values()) // 2} road connections\n")
    
    while True:
        print("  OPTIONS:")
        print("  1. Find shortest path between two cities")
        print("  2. Find all shortest paths from a city")
        print("  3. List all cities")
        print("  4. Exit")
        
        choice = input("\n  Enter choice (1-4): ").strip()
        
        if choice == '1':
            print(f"\n  Available cities (type name exactly):")
            for i, c in enumerate(cities):
                print(f"    {c}", end="\t" if (i+1) % 4 != 0 else "\n")
            print()
            start = input("  Enter start city: ").strip().title()
            goal  = input("  Enter goal city : ").strip().title()
            find_shortest_path(graph, start, goal)
        
        elif choice == '2':
            print(f"\n  Available cities:")
            for i, c in enumerate(cities):
                print(f"    {c}", end="\t" if (i+1) % 4 != 0 else "\n")
            print()
            start = input("  Enter source city: ").strip().title()
            find_all_shortest_paths(graph, start)
        
        elif choice == '3':
            print(f"\n  {'─'*50}")
            print(f"  All {len(cities)} cities in the network:")
            print(f"  {'─'*50}")
            for i, c in enumerate(cities, 1):
                print(f"  {i:3}. {c}")
            print(f"  {'─'*50}\n")
        
        elif choice == '4':
            print("\n  Goodbye! 👋\n")
            break
        else:
            print("  ⚠️  Invalid choice. Please enter 1–4.")


if __name__ == "__main__":
    interactive_menu(INDIAN_CITIES_GRAPH)

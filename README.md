# AI-ASSIGNMENT-3-SE24UCSE125

This repository contains three Python-based implementations of foundational artificial intelligence search algorithms. The projects range from routing across a macro-level road network to controlling an Unmanned Ground Vehicle (UGV) in both static and dynamic battlefield environments.

System Requirements
Language: Python 3.7+

Dependencies: None (Zero external libraries required. Built entirely using standard libraries: heapq, math, random, and time).

Part 1: India Road Network Routing
File: assignment1_dijkstra.py
Algorithm: Dijkstra's Algorithm (Uniform-Cost Search)

This module calculates the optimal driving routes between major Indian cities using real-world approximate distances.

Key Features:

Maps over 70 Indian cities.

Calculates the shortest path between any two specified cities, providing a full segment-by-segment breakdown.

Generates all shortest paths originating from a single source city.

Includes an interactive terminal menu for ease of use.

Execution: python assignment1_dijkstra.py

Sample Output:

Path: Delhi → Agra → Gwalior → Bhopal → Nagpur → Hyderabad → Chennai
Distance: 2209 km
Hops: 6


Gemini said
Here is a reframed and polished version of your assignment details. It retains all the original technical information but reorganizes it into a cleaner, more professional format—perfect for a project README.md or portfolio submission.

Project Overview: AI Search & Pathfinding Algorithms
Course Code: AI-ASSIGNMENT-3-SE24UCSE135

This repository contains three Python-based implementations of foundational artificial intelligence search algorithms. The projects range from routing across a macro-level road network to controlling an Unmanned Ground Vehicle (UGV) in both static and dynamic battlefield environments.

System Requirements
Language: Python 3.7+

Dependencies: None (Zero external libraries required. Built entirely using standard libraries: heapq, math, random, and time).

Part 1: India Road Network Routing
File: assignment1_dijkstra.py
Algorithm: Dijkstra's Algorithm (Uniform-Cost Search)

This module calculates the optimal driving routes between major Indian cities using real-world approximate distances.

Key Features:

Maps over 70 Indian cities.

Calculates the shortest path between any two specified cities, providing a full segment-by-segment breakdown.

Generates all shortest paths originating from a single source city.

Includes an interactive terminal menu for ease of use.

Execution: python assignment1_dijkstra.py

Sample Output:

Path: Delhi → Agra → Gwalior → Bhopal → Nagpur → Hyderabad → Chennai
Distance: 2209 km
Hops: 6

Part 2: UGV Navigation (Static Obstacles)
File: assignment2_ugv_static.py
Algorithm: A* Search
This simulation tasks a UGV with finding an optimal path across a 70×70 km grid representing a battlefield. In this environment, all obstacles are mapped a-priori (prior to movement).Key Features:Supports 8-directional movement (diagonal movement cost is $\sqrt{2}$).Configurable obstacle densities: LOW (10%), MEDIUM (25%), and HIGH (40%).Provides an ASCII-based grid visualization of the terrain, obstacles, and chosen path.Execution: python assignment2_ugv_static.py

Part 3: UGV Navigation (Dynamic Obstacles)
File: assignment3_ugv_dynamic.py
Algorithm: D* Lite (Incremental Replanning)

An advanced extension of Part 2, this module places the UGV in an unpredictable environment where obstacles are unknown a-priori. Obstacles can dynamically appear or disappear while the UGV is in transit.

Key Features:
Real-time obstacle shifting at every step, completely hidden from the UGV's global map.

Configurable sensor radius, allowing the UGV to only detect obstacles within a limited vicinity.

Highly efficient incremental replanning (it only recalculates the path when new sensor data contradicts the planned route, avoiding full global replans).

A built-in comparison mode to benchmark dynamic performance against static environments.

Expanded MOE reporting that logs sensor scans and replanning events.

Execution: python assignment3_ugv_dynamic.py


#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <queue>
#include <algorithm>
#include <limits>
using namespace std;
struct Node {
    char name;
    double g;
    double f;

    bool operator>(const Node& other) const {
        return f > other.f;
    }
};

struct Edge {
    char target;
    double cost;
};
//returns path and total cost
//accepts four parameters
pair<vector<char>, double> aStar(
    const char &start,
    const char &goal,
    const unordered_map<char, vector<Edge>> &graph,
    const unordered_map<char, double> &heuristics
) {
    //Min heap 
    priority_queue <Node, vector<Node>, greater<Node>> openSet;


    //Lowest g-cost 
    unordered_map <char, double> best_g;

    //Parent_tracker
    unordered_map <char, char> parent;

    double start_h = heuristics.at(start);
    best_g[start] = 0;
    openSet.push({start, 0, 0 + start_h});

    while(!openSet.empty()){
        Node current = openSet.top();
        openSet.pop();
        
        if (current.name == goal){
            vector<char> path;
            char curr = goal;
            while (curr != start){
                path.push_back(curr);
                curr = parent[curr];
            }
            path.push_back(start);
            reverse(path.begin(), path.end());
            return {path, current.g};
        }
        if (current.g > best_g[current.name]) {
            continue;
        }
        auto it = graph.find(current.name);
        if (it == graph.end()) continue;

        for (const Edge& edge : it->second) {
            double tentative_g = current.g + edge.cost;

            if (best_g.find(edge.target) == best_g.end() || tentative_g < best_g[edge.target]) {
                best_g[edge.target] = tentative_g;
                parent[edge.target] = current.name;

                double h = heuristics.at(edge.target);
                double f = tentative_g + h;

                openSet.push({edge.target, tentative_g, f});
            }
        }
    }
    return {{}, numeric_limits<double>::infinity()};
}

//Test
int main() {
    // 1. Predefined Heuristics h(n) [Red values]
    unordered_map<char, double> heuristics = {
        {'A', 10.0},
        {'B', 8.0},
        {'C', 5.0},
        {'D', 7.0},
        {'E', 3.0},
        {'F', 6.0},
        {'G', 5.0},
        {'H', 3.0},
        {'I', 1.0},
        {'J', 0.0}
    };

    // 2. Graph adjacency list [Blue values]
    unordered_map<char, vector<Edge>> graph = {
        {'A', {{'B', 6.0}, {'F', 3.0}}},
        {'B', {{'A', 6.0}, {'C', 3.0}, {'D', 2.0}}},
        {'C', {{'B', 3.0}, {'D', 1.0}, {'E', 5.0}}},
        {'D', {{'B', 2.0}, {'C', 1.0}, {'E', 8.0}}},
        {'E', {{'C', 5.0}, {'D', 8.0}, {'I', 5.0}, {'J', 5.0}}},
        {'F', {{'A', 3.0}, {'G', 1.0}, {'H', 7.0}}},
        {'G', {{'F', 1.0}, {'I', 3.0}}},
        {'H', {{'F', 7.0}, {'I', 2.0}}},
        {'I', {{'E', 5.0}, {'G', 3.0}, {'H', 2.0}, {'J', 3.0}}},
        {'J', {{'E', 5.0}, {'I', 3.0}}}
    };

    auto [path, cost] = aStar('A', 'J', graph, heuristics);

    if (!path.empty()) {
        cout << "Optimal Path: ";
        for (size_t i = 0; i < path.size(); ++i) {
            cout << path[i];
            if (i + 1 < path.size()) {
                cout << " -> ";
            }
        }
        cout << "\nTotal Cost: " << cost << endl;
    } else {
        cout << "No path found." << endl;
    }

    return 0;
}
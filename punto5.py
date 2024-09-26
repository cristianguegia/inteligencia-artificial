import sys
import heapq  # Para usar la cola de prioridad

class Node():
    def __init__(self, state, parent, action, cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost

    # Definir un método para el costo total (g + h)
    def total_cost(self, goal):
        return self.cost + self.heuristic(goal)

    # Heurística: distancia de Manhattan
    def heuristic(self, goal):
        return abs(self.state[0] - goal[0]) + abs(self.state[1] - goal[1])

    # Comparar nodos para la cola de prioridad
    def __lt__(self, other):
        return self.total_cost(other.state) < other.total_cost(self.state)

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Maze():
    def __init__(self, filename):
        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None

    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def solve_bfs(self):
        """Finds a solution to maze using BFS, if one exists."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        frontier = QueueFrontier()  # BFS
        frontier.add(start)
        self.explored = set()

        while True:
            if frontier.empty():
                raise Exception("no solution")

            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    def solve_dfs(self):
        """Finds a solution to maze using DFS, if one exists."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()  # DFS
        frontier.add(start)
        self.explored = set()

        while True:
            if frontier.empty():
                raise Exception("no solution")

            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    def solve_a_star(self):
        """Finds a solution to maze using A*, if one exists."""
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None, cost=0)
        frontier = []
        heapq.heappush(frontier, start)
        self.explored = set()

        while frontier:
            node = heapq.heappop(frontier)
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if state not in self.explored:
                    child = Node(state=state, parent=node, action=action, cost=node.cost + 1)
                    heapq.heappush(frontier, child)

def main():
    while True:
        print("\nMenú de Algoritmos de Búsqueda")
        print("1. DFS (Depth-First Search)")
        print("2. BFS (Breadth-First Search)")
        print("3. A* (A Star)")
        print("4. Salir")

        choice = input("Seleccione una opción (1-4): ")

        if choice == '1':
            filename = input("Ingrese el nombre del archivo del laberinto (ej. maze.txt): ")
            m = Maze(filename)
            print("Maze:")
            m.print()
            print("Resolviendo con DFS...")
            m.solve_dfs()
            print("Estados explorados:", m.num_explored)
            print("Solución:")
            m.print()

        elif choice == '2':
            filename = input("Ingrese el nombre del archivo del laberinto (ej. maze.txt): ")
            m = Maze(filename)
            print("Maze:")
            m.print()
            print("Resolviendo con BFS...")
            m.solve_bfs()
            print("Estados explorados:", m.num_explored)
            print("Solución:")
            m.print()

        elif choice == '3':
            filename = input("Ingrese el nombre del archivo del laberinto (ej. maze.txt): ")
            m = Maze(filename)
            print("Maze:")
            m.print()
            print("Resolviendo con A*...")
            m.solve_a_star()
            print("Estados explorados:", m.num_explored)
            print("Solución:")
            m.print()

        elif choice == '4':
            print("Saliendo del programa.")
            break

        else:
            print("Opción inválida, por favor intente de nuevo.")

if __name__ == "__main__":
    main()

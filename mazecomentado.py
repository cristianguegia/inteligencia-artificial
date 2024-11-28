import sys

# Clase que representa un nodo en el proceso de búsqueda.
class Node():
    def __init__(self, state, parent, action):
        self.state = state  # El estado del nodo, es decir, las coordenadas en el laberinto.
        self.parent = parent  # El nodo anterior (para reconstruir el camino una vez se encuentre la solución).
        self.action = action  # La acción que llevó a este estado (moverse en una dirección).

# Clase que implementa una frontera usando una pila (LIFO).
class StackFrontier():
    def __init__(self):
        self.frontier = []  # La frontera es una lista que actúa como una pila.

    def add(self, node):
        self.frontier.append(node)  # Añade un nodo a la frontera.

    def contains_state(self, state):
        # Revisa si algún nodo en la frontera contiene un estado específico.
        return any(node.state == state for node in self.frontier)

    def empty(self):
        # Revisa si la frontera está vacía.
        return len(self.frontier) == 0

    def remove(self):
        # Si la frontera no está vacía, elimina y retorna el último nodo añadido (pila).
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

# Clase que extiende StackFrontier y usa una cola (FIFO) en lugar de una pila.
class QueueFrontier(StackFrontier):
    def remove(self):
        # Elimina y retorna el primer nodo en la frontera (cola).
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

# Clase que representa el laberinto y su resolución.
class Maze():
    def __init__(self, filename):
        # Lee el archivo que contiene la representación del laberinto.
        with open(filename) as f:
            contents = f.read()

        # Verifica que haya exactamente un punto de inicio (A) y un punto de meta (B).
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determina la altura y el ancho del laberinto, y crea la representación de las paredes.
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self.walls = []  # Lista que contiene la representación del laberinto (True para paredes, False para espacios vacíos).
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    # Marca el punto de inicio ("A") y el de meta ("B").
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)  # Marca las paredes.
                except IndexError:
                    row.append(False)  # Para evitar errores si las filas tienen longitudes diferentes.
            self.walls.append(row)

        self.solution = None  # Variable que guardará la solución, si se encuentra.

    # Método que imprime el laberinto en consola.
    def print(self):
        solution = self.solution[1] if self.solution is not None else None  # Si hay solución, obtén las celdas en el camino.
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")  # Muestra las paredes como "█".
                elif (i, j) == self.start:
                    print("A", end="")  # Muestra el inicio con "A".
                elif (i, j) == self.goal:
                    print("B", end="")  # Muestra la meta con "B".
                elif solution is not None and (i, j) in solution:
                    print("*", end="")  # Muestra el camino de la solución con "*".
                else:
                    print(" ", end="")  # Espacios vacíos.
            print()
        print()

    # Método que devuelve los posibles movimientos (vecinos) de una celda.
    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row + 1, col))
        ]

        result = []
        for action, (r, c) in candidates:
            # Asegura que las nuevas posiciones estén dentro de los límites y no sean paredes.
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    # Método que resuelve el laberinto usando una búsqueda en profundidad.
    def solve(self):
        """Encuentra una solución al laberinto, si existe."""
        self.num_explored = 0  # Contador de nodos explorados.

        # Inicializa la frontera con el nodo de inicio.
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Conjunto de nodos explorados.
        self.explored = set()

        # Bucle principal de búsqueda.
        while True:
            if frontier.empty():  # Si la frontera está vacía, no hay solución.
                raise Exception("no solution")

            # Elige un nodo de la frontera.
            node = frontier.remove()
            self.num_explored += 1

            # Si el nodo es el de la meta, se ha encontrado la solución.
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:  # Reconstruct the path from start to goal.
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()  # Revierte el camino.
                cells.reverse()
                self.solution = (actions, cells)  # Guarda la solución.
                return

            # Marca el nodo actual como explorado.
            self.explored.add(node.state)

            # Añade los vecinos del nodo a la frontera si no han sido explorados ni están en la frontera.
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    # Método para generar una imagen del laberinto y guardarla como archivo PNG.
    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Crea una nueva imagen en blanco.
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        # Si existe una solución, utiliza sus celdas.
        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    fill = (40, 40, 40)  # Paredes en gris oscuro.
                elif (i, j) == self.start:
                    fill = (255, 0, 0)  # El inicio en rojo.
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)  # La meta en verde.
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)  # Celdas en la solución en amarillo claro.
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)  # Celdas exploradas en rojo claro.
                else:
                    fill = (237, 240, 252)  # Espacios vacíos en blanco.

                # Dibuja una celda.
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        # Guarda la imagen generada.
        img.save(filename)

# Verifica que se pase un argumento al script (nombre del archivo del laberinto).
if len(sys.argv) != 2:
    sys.exit("Usage: python mazecomentado.py maze.txt")

# Crea una instancia del laberinto a partir del archivo dado.
m = Maze(sys.argv[1])

# Muestra el laberinto sin solución.
print("Maze:")
m.print()

# Resuelve el laberinto.
print("Solving...")
m.solve()

# Muestra el número de estados explorados y la solución.
print(f"Solution found after {m.num_explored} states explored.")
m.print()

# Opcionalmente, genera una imagen con la solución.
m.output_image("solution.png", show_solution=True)

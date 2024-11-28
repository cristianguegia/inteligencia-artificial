import sys

# Clase que representa un nodo en el árbol de búsqueda
class Node():
    def __init__(self, state, parent, action):
        self.state = state  # Estado (posición) del nodo
        self.parent = parent  # Nodo anterior (de donde se llegó a este nodo)
        self.action = action  # Acción tomada para llegar a este nodo (por ejemplo, "arriba", "abajo")

# Clase para manejar la frontera usando una pila (LIFO) - Usada en DFS
class StackFrontier():
    def __init__(self):
        self.frontier = []  # Lista que representa la frontera de nodos

    def add(self, node):
        self.frontier.append(node)  # Agregar un nodo a la frontera

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)  # Verificar si la frontera contiene el estado dado

    def empty(self):
        return len(self.frontier) == 0  # Verificar si la frontera está vacía

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")  # Si la frontera está vacía, lanzar una excepción
        else:
            node = self.frontier[-1]  # Tomar el último nodo de la frontera (LIFO)
            self.frontier = self.frontier[:-1]  # Eliminar el último nodo de la frontera
            return node  # Retornar el nodo removido

# Clase para manejar la frontera usando una cola (FIFO) - Usada en BFS
class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")  # Si la frontera está vacía, lanzar una excepción
        else:
            node = self.frontier[0]  # Tomar el primer nodo de la frontera (FIFO)
            self.frontier = self.frontier[1:]  # Eliminar el primer nodo de la frontera
            return node  # Retornar el nodo removido

# Clase que representa el laberinto
class Maze():
    def __init__(self, filename):
        # Leer el archivo y establecer las dimensiones del laberinto
        with open(filename) as f:
            contents = f.read()  # Leer el contenido del archivo

        # Validar que haya exactamente un punto de inicio "A" y un punto de meta "B"
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determinar la altura y el ancho del laberinto
        contents = contents.splitlines()  # Dividir el contenido en líneas
        self.height = len(contents)  # La altura es el número de líneas
        self.width = max(len(line) for line in contents)  # El ancho es el largo de la línea más larga

        # Crear una lista de paredes y almacenar la posición de inicio y meta
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":  # Punto de inicio
                        self.start = (i, j)  # Guardar las coordenadas del inicio
                        row.append(False)
                    elif contents[i][j] == "B":  # Punto de meta
                        self.goal = (i, j)  # Guardar las coordenadas de la meta
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)  # Espacio vacío
                    else:
                        row.append(True)  # Pared
                except IndexError:
                    row.append(False)  # En caso de que haya un desbordamiento, se considera vacío
            self.walls.append(row)  # Añadir la fila de paredes al laberinto

        self.solution = None  # Inicialmente no hay solución

    # Función para imprimir el laberinto en la consola
    def print(self):
        solution = self.solution[1] if self.solution is not None else None  # Obtener la solución si existe
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")  # Pared
                elif (i, j) == self.start:
                    print("A", end="")  # Punto de inicio
                elif (i, j) == self.goal:
                    print("B", end="")  # Punto de meta
                elif solution is not None and (i, j) in solution:
                    print("*", end="")  # Parte de la solución
                else:
                    print(" ", end="")  # Espacio vacío
            print()
        print()

    # Función para obtener los vecinos accesibles de un estado dado
    def neighbors(self, state):
        row, col = state  # Desempaquetar las coordenadas
        candidates = [
            ("up", (row - 1, col)),  # Vecino arriba
            ("down", (row + 1, col)),  # Vecino abajo
            ("left", (row, col - 1)),  # Vecino a la izquierda
            ("right", (row, col + 1))  # Vecino a la derecha
        ]

        result = []
        for action, (r, c) in candidates:
            # Verificar si la celda está dentro del laberinto y no es una pared
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))  # Añadir el vecino válido a los resultados
        return result

    # Función que resuelve el laberinto utilizando BFS o DFS
    def solve(self):
        """Finds a solution to maze, if one exists."""

        self.num_explored = 0  # Número de estados explorados

        # Inicializar la frontera con el nodo de inicio
        start = Node(state=self.start, parent=None, action=None)
        frontier = QueueFrontier()  # Usar BFS (QueueFrontier) o DFS (StackFrontier)

        frontier.add(start)  # Añadir el nodo de inicio a la frontera

        # Inicializar el conjunto de nodos explorados
        self.explored = set()

        # Loop hasta encontrar una solución
        while True:
            if frontier.empty():
                raise Exception("no solution")  # Si la frontera está vacía, no hay solución

            # Elegir un nodo de la frontera
            node = frontier.remove()
            self.num_explored += 1  # Incrementar el contador de nodos explorados

            # Si el nodo es el objetivo, se ha encontrado la solución
            if node.state == self.goal:
                actions = []  # Lista de acciones
                cells = []  # Lista de celdas del camino
                while node.parent is not None:
                    actions.append(node.action)  # Guardar la acción que lleva a este nodo
                    cells.append(node.state)  # Guardar el estado (coordenadas) de este nodo
                    node = node.parent  # Retroceder al nodo anterior
                actions.reverse()  # Invertir las acciones para mostrar el camino correcto
                cells.reverse()  # Invertir las celdas del camino
                self.solution = (actions, cells)  # Guardar la solución
                return  # Retornar la solución

            # Marcar el nodo como explorado
            self.explored.add(node.state)

            # Añadir los vecinos del nodo a la frontera
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)  # Crear un nodo hijo
                    frontier.add(child)  # Añadir el hijo a la frontera

    # Función que genera una imagen del laberinto con la solución
    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50  # Tamaño de cada celda
        cell_border = 2  # Borde de la celda

        # Crear una imagen en blanco
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None  # Obtener la solución
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                # Determinar el color de cada celda
                if col:
                    fill = (40, 40, 40)  # Pared
                elif (i, j) == self.start:
                    fill = (255, 0, 0)  # Inicio (rojo)
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)  # Meta (verde)
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)  # Parte de la solución (amarillo claro)
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (100, 100, 100)  # Celdas exploradas (gris)
                else:
                    fill = (255, 255, 255)  # Espacios vacíos (blanco)

                # Dibujar la celda
                draw.rectangle(
                    [j * cell_size + cell_border, i * cell_size + cell_border, 
                     (j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border],
                    fill=fill
                )

        # Guardar la imagen
        img.save(filename)
if len(sys.argv) != 2:
    sys.exit("Usage: python mazecomentado.py maze.txt")
    
    #exploit para correr todo el programa

m = Maze(sys.argv[1])
print("Maze:")
m.print()
print("Solving...")
m.solve()
print("States Explored:", m.num_explored)
print("Solution:")
m.print()
m.output_image("maze.png", show_explored=True)


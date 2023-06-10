import pygame
from queue import PriorityQueue, SimpleQueue
from random import choice

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

WIDTH, HEIGHT = 1200, 600
pygame.init()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT + 80))
pygame.display.set_caption("Maze Generator & Path Finding Algorithms")
CLOCK = pygame.time.Clock()


class Button:
    def __init__(self, x, y, width, height, color, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color

    def draw(self, window, outline):
        pygame.draw.rect(window, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), border_radius=12)
        pygame.draw.rect(window, pygame.Color("lime"), (self.x, self.y, self.width, self.height), border_radius=12)

        font = pygame.font.SysFont("comicsans", 30)
        text = font.render(self.text, True, (0, 0, 0))
        window.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isClicked(self, pos):
        if (self.x < pos[0] < self.x + self.width) and (self.y < pos[1] < self.y + self.height):
            return True

        return False


class Cell:

    def __init__(self, row, col, width, total_rows, total_cols):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.width = width
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.neighbors = []
        self.color = WHITE
        self.walls = {"UP": True, "RIGHT": True, "DOWN": True, "LEFT": True}
        self.visited = False
        self.path = False
        self.start = False
        self.end = False

    def get_pos(self):
        return self.row, self.col

    def draw_current_cell(self, window):
        pygame.draw.rect(window, GREEN, (self.x + 1, self.y + 1, self.width - 2, self.width - 2), 0)
        pygame.display.update()
        CLOCK.tick(30)

    def draw(self, window):
        if self.visited:
            pygame.draw.rect(window, BLACK, (self.x, self.y, self.width, self.width))
        if self.path:
            pygame.draw.rect(window, PURPLE, (self.x + 5, self.y + 5, self.width - 10, self.width - 10),
                             border_radius=12)
        if self.start:
            pygame.draw.rect(window, RED, (self.x, self.y, self.width, self.width))
        if self.end:
            pygame.draw.rect(window, GREEN, (self.x, self.y, self.width, self.width))

        if self.walls["UP"]:
            pygame.draw.line(window, pygame.Color('darkorange'), (self.x, self.y), (self.x + self.width, self.y), 3)
        if self.walls["RIGHT"]:
            pygame.draw.line(window, pygame.Color('darkorange'), (self.x + self.width, self.y),
                             (self.x + self.width, self.y + self.width),
                             3)
        if self.walls["DOWN"]:
            pygame.draw.line(window, pygame.Color('darkorange'), (self.x + self.width, self.y + self.width),
                             (self.x, self.y + self.width),
                             3)
        if self.walls["LEFT"]:
            pygame.draw.line(window, pygame.Color('darkorange'), (self.x, self.y + self.width), (self.x, self.y), 3)

    def check_cell(self, x, y, grid):
        if x < 0 or x > self.total_rows - 1 or y < 0 or y > self.total_cols - 1:
            return False
        return grid[x][y]

    def check_neighbors(self, grid):
        neighbors_g = []
        top = self.check_cell(self.row, self.col - 1, grid)
        right = self.check_cell(self.row + 1, self.col, grid)
        bottom = self.check_cell(self.row, self.col + 1, grid)
        left = self.check_cell(self.row - 1, self.col, grid)
        if top and not top.visited:
            neighbors_g.append(top)
        if right and not right.visited:
            neighbors_g.append(right)
        if bottom and not bottom.visited:
            neighbors_g.append(bottom)
        if left and not left.visited:
            neighbors_g.append(left)
        return choice(neighbors_g) if neighbors_g else False

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2, = p2
    return abs(x2 - x1) + abs(y2 - y1)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current.path = True
        current = came_from[current]
        draw()


def aStar(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))

    g_score = {cell: float("inf") for row in grid for cell in row}
    g_score[start] = 0
    f_score = {cell: float("inf") for row in grid for cell in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}
    came_from = {}

    while not open_set.empty():

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                g_score[neighbor] = temp_g_score
                came_from[neighbor] = current
                f_score[neighbor] = h(neighbor.get_pos(), end.get_pos()) + g_score[neighbor]

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

        draw()

    return False


def bfs(draw, start, end):
    queue = SimpleQueue()
    queue.put(start)
    visited = [start]
    came_from = {}

    while not queue.empty():
        current = queue.get()
        if current == end:
            reconstruct_path(came_from, end, draw)
            break

        for neighbor in current.neighbors:
            if neighbor not in visited:
                queue.put(neighbor)
                visited.append(neighbor)
                came_from[neighbor] = current

        draw()

    return False


def make_grid(rows, cols, cell_width):
    grid = []
    for i in range(rows + 2):
        grid.append([])
        for j in range(cols):
            cell = Cell(i, j, cell_width, rows, cols)
            grid[i].append(cell)

    return grid


def draw(window, grid, resetButton, mazeGeneratorButton, aStarButton, bfsButton):
    window.fill(pygame.Color('navy'))
    resetButton.draw(window, (0, 0, 0))
    mazeGeneratorButton.draw(window, (0, 0, 0))
    aStarButton.draw(window, (0, 0, 0))
    bfsButton.draw(window, (0, 0, 0))

    for row in grid:
        for cell in row:
            cell.draw(window)

    pygame.display.update()


def remove_walls(current, next):
    dx = current.row - next.row
    if dx == 1:
        current.walls["LEFT"] = False
        next.walls["RIGHT"] = False
        current.neighbors.append(next)
    elif dx == -1:
        current.walls["RIGHT"] = False
        next.walls["LEFT"] = False
        current.neighbors.append(next)
    dy = current.col - next.col
    if dy == 1:
        current.walls["UP"] = False
        next.walls["DOWN"] = False
        current.neighbors.append(next)
    elif dy == -1:
        current.walls["DOWN"] = False
        next.walls["UP"] = False
        current.neighbors.append(next)


def get_clicked_pos(pos, cell_width):
    y, x = pos

    row = y // cell_width
    col = x // cell_width

    return row, col


def main(window, width, height):
    resetButton = Button(50, 630, 100, 30, YELLOW, "Reset")
    mazeGeneratorButton = Button(270, 630, 200, 30, YELLOW, "Generate maze")
    aStarButton = Button(600, 630, 200, 30, YELLOW, "A* Algorithm")
    bfsButton = Button(940, 630, 200, 30, YELLOW, "BFS Algorithm")

    cell_width = 50
    rows, cols = width // cell_width, height // cell_width
    grid = make_grid(rows, cols, cell_width)

    mazeCreated = False

    current_cell = grid[0][0]
    stack = []

    start = None
    end = None

    run = True

    while run:
        draw(window, grid, resetButton, mazeGeneratorButton, aStarButton, bfsButton)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, cell_width)

                if not row > rows - 1 and not col > cols - 1:
                    cell = grid[row][col]
                    if not start and cell != end:
                        start = cell
                        start.start = True

                    elif not end and cell != start:
                        end = cell
                        end.end = True

                if mazeGeneratorButton.isClicked(pos):
                    while not mazeCreated:
                        draw(window, grid, resetButton, mazeGeneratorButton, aStarButton, bfsButton)
                        current_cell.visited = True
                        if stack:
                            current_cell.draw_current_cell(window)
                        next_cell = current_cell.check_neighbors(grid)
                        if next_cell:
                            next_cell.visited = True
                            stack.append(current_cell)
                            remove_walls(current_cell, next_cell)
                            current_cell = next_cell

                        elif stack:
                            current_cell = stack.pop()
                        if not stack:
                            mazeCreated = True

                if aStarButton.isClicked(pos) and start and end and mazeCreated:
                    aStar(lambda: draw(window, grid, resetButton, mazeGeneratorButton, aStarButton, bfsButton), grid, start, end)

                if bfsButton.isClicked(pos) and start and end and mazeCreated:
                    bfs(lambda: draw(window, grid, resetButton, mazeGeneratorButton, aStarButton, bfsButton), start, end)

                if resetButton.isClicked(pos):
                    start = None
                    end = None
                    grid = make_grid(rows, cols, cell_width)
                    mazeCreated = False

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, cell_width)

                if not row > rows - 1 and not col > cols - 1:
                    cell = grid[row][col]
                    if cell == start:
                        start.start = False
                        start = None

                    elif cell == end:
                        end.end = False
                        end = None

    pygame.quit()


if __name__ == "__main__":
    main(WINDOW, WIDTH, HEIGHT)

from collections import deque
import sys
import pygame
import math
import random

# todo: change to these variables in the code (easier to read)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 0, 255)
BLUE = (0, 255, 0)
GREY = (50, 50, 50)


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.current = False
        self.is_wall = False
        self.is_target = False
        self.is_start = False
        self.parent = None
        self.is_on_path = False
        self.visited = False
        self.h = math.inf
        self.g = math.inf
        self.f = self.h + self.g

    def get_children(self, grid):
        children = []
        children_indexes = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # relative to self
        for x, y in children_indexes:
            if 0 <= self.x + x < len(grid) and 0 <= self.y + y < len(grid[0]):
                cell = grid[self.x + x][self.y + y]
                if not cell.is_wall and not cell.visited:
                    children += [cell]

        return children

    def __eq__(self, other):
        if not isinstance(other, Node):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.x == other.x and self.y == other.y


class Button:
    # (x, y, w, text)
    def __init__(self, x, y, w, text):
        self.x = x
        self.y = y
        self.w = w
        self.width = 100
        self.height = 50
        b = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(w, (255, 255, 255), b, 1, 3)
        font = pygame.font.SysFont("arial", 24)
        self.text = font.render(text, False, (255, 255, 255))


def create_grid(cells_x, cells_y):
    """in the pygame window, x is horizontal and y is vertical, but the other way around in the calculations."""
    grid = []
    for x in range(cells_x):
        row = []
        for y in range(cells_y):
            n = Node(x, y)
            row += [n]
        grid += [row]
    return grid


def get_start_node(grid):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j].is_start:
                return grid[i][j]
    return None


def get_target_node(grid):  # used for a*
    count = 0
    target_node = None
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j].is_target:
                target_node = grid[i][j]
                count += 1
    return target_node, count


def button_clicked(pos, button):
    return button.x <= pos[0] <= button.x + button.width and button.y <= pos[1] <= button.y + button.height


def print_walls(grid):
    walls = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j].is_wall:
                walls += [(i, j)]
    print(walls)

def main():
    """
    todo:
    * add timer
    * add text showcasing the length of returned path
    * make a "ring" around the search methods with title "choose algorithm:"
    * manually create like 5 grids, store them in a text file. Then, when calling on a random maze, take one from that
    text file. If there is a manually created grid active, choose one of the other 4. If none is active,
    take from all 5. At the moment only focus on 20x20 grids
    """
    pygame.init()
    w_width = 1000  # x
    w_height = 1000  # y
    search_choice = ""  # can be "BFS", "DFS", "A*"

    w = pygame.display.set_mode((w_width + 200, w_height + 200))
    pygame.display.set_caption("Search visualizer")

    size = 50
    cells_x, cells_y = w_width//size, w_height//size
    grid = create_maze(walls1, cells_x, cells_y)
    start_node = None
    edit_mode = False

    # main game loop
    while True:
        # Fix graphics stuff
        w.fill((0, 0, 0))
        # todo: fix this implementation in the button class instead
        pygame.draw.line(w, (255, 255, 255), (1000, 0), (1000, 1000))
        pygame.draw.line(w, (255, 255, 255), (1000, 1000), (0, 1000))
        bfs_button = Button(1050, 650, w, "BFS")
        dfs_button = Button(1050, 750, w, "DFS")
        a_star_button = Button(1050, 850, w, "A*")
        reset_button = Button(1050, 1000, w, "Reset")
        quit_button = Button(1050, 1100, w, "Quit")
        edit_grid_button = Button(1050, 200, w, "Edit grid")
        maze1_button = Button(50, 1100, w, "Maze 1")
        maze2_button = Button(200, 1100, w, "Maze 2")
        w.blit(bfs_button.text, (bfs_button.x + 30, bfs_button.y + 10))
        w.blit(dfs_button.text, (dfs_button.x + 30, dfs_button.y + 10))
        w.blit(a_star_button.text, (a_star_button.x + 30, a_star_button.y + 10))
        w.blit(reset_button.text, (reset_button.x + 30, reset_button.y + 10))
        w.blit(quit_button.text, (quit_button.x + 30, quit_button.y + 10))
        w.blit(edit_grid_button.text, (edit_grid_button.x + 10, edit_grid_button.y + 10))
        w.blit(maze1_button.text, (maze1_button.x + 20, maze1_button.y + 10))
        w.blit(maze2_button.text, (maze2_button.x + 20, maze2_button.y + 10))

        draw_grid(w, size, grid)
        pygame.display.update()
        # End graphics stuff
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # event.button {1,2,3,4,5}. 1 = left click, 3 = right click
                pos = pygame.mouse.get_pos()
                if pos[0] <= w.get_width() - 200 and pos[1] <= w.get_height() - 200:  # grid clicked
                    x, y = pos[0]//size, pos[1]//size
                    clicked_cell = grid[x][y]
                    if not edit_mode:
                        if event.button == 1:  # left click, set start node
                            start = clicked_cell.is_start
                            if start:
                                clicked_cell.is_start = False
                            else:
                                if get_start_node(grid) is None:  # cant have multiple start points
                                    clicked_cell.is_start = True
                                    start_node = clicked_cell
                            pygame.display.update()
                        elif event.button == 3:  # right click, set target target node
                            target = clicked_cell.is_target
                            if target:
                                clicked_cell.is_target = False
                            else:
                                print("Set target node!")
                                clicked_cell.is_target = True
                            pygame.display.update()
                    else:  # edit mode
                        if event.button == 1:  # left click, place walls freely
                            clicked_cell.is_wall = True

                elif button_clicked(pos, reset_button):
                    grid = create_grid(cells_x, cells_y)
                    search_choice = ""
                    # reset(w, size)
                elif button_clicked(pos, dfs_button):
                    if start_node is not None:
                        res = graph_search(grid, start_node, False, w, size)
                        search_choice = "DFS"
                        path_cost = len(res)
                        print(path_cost)
                elif button_clicked(pos, bfs_button):
                    if start_node is not None:
                        res = graph_search(grid, start_node, True, w, size)
                        search_choice = "BFS"
                        path_cost = len(res)
                        print(path_cost)
                elif button_clicked(pos, a_star_button):
                    if start_node is not None:
                        target_node, count = get_target_node(grid)
                        if target_node is not None and count == 1:
                            res = a_star(grid, start_node, target_node, w, size)
                            search_choice = "A*"
                            path_cost = len(res)
                            print(path_cost)
                elif button_clicked(pos, quit_button):
                    exit(0)
                elif button_clicked(pos, edit_grid_button):
                    # grid = random_grid(cells_x, cells_y)
                    if edit_mode:
                        edit_mode = False
                        print_walls(grid)
                    else:
                        edit_mode = True
                elif button_clicked(pos, maze1_button):
                    grid = create_maze(walls1)
                    search_choice = ""
                elif button_clicked(pos, maze2_button):
                    grid = create_maze(walls2)
                    search_choice = ""
                if search_choice:  # if True then some algorithm has run
                    # text at (50, 1050) [search "found a path with length " path_cost!]
                    # or "SEARCH_METHOD found a path from (x, y) to (z, w) with cost x."
                    # remove this text at reset and edit.
                    pass


def random_grid(cells_x, cells_y):
    grid = create_grid(cells_x, cells_y)
    # standard should be 50% walls, 50% empty cells.
    # first idea: create a list of all the coordinates as tuples
    # pick grid.width*grid.height/2 random choices from that list (result is still a list)
    # then loop through that resulting list and place walls in the corresponding positions in the grid
    all_positions = []
    n = cells_x * cells_y // 2  # standard should be 50% walls, 50% empty cells.
    for x in range(cells_x):
        for y in range(cells_y):
            all_positions += [(x, y)]

    random_positions = random.sample(all_positions, n)
    print(random_positions)
    for coordinate in random_positions:
        x, y = coordinate
        grid[x][y].is_wall = True
    return grid


def reset(w, size):
    # grid = create_grid(w.get_width() - 200, w.get_height() - 200)  # manipulate the current grid
    # draw_grid(w, size, grid)
    # pygame.display.update()
    pass


def draw_grid(w, size, grid):
    for i in range(0, w.get_width() - 200, size):
        for j in range(0, w.get_height() - 200, size):
            x, y = i//size, j//size

            square = pygame.Rect(i, j, size, size)
            if not grid[x][y].is_wall:
                pygame.draw.rect(w, (255, 255, 255), square, 0)
            if grid[x][y].is_start:
                pygame.draw.rect(w, (0, 255, 0), square, 0)
            if grid[x][y].is_target:
                pygame.draw.rect(w, (0, 0, 255), square, 0)
            if grid[x][y].visited:
                pygame.draw.rect(w, (0, 0, 255), square, 0)
            if grid[x][y].is_on_path:
                pygame.draw.rect(w, (0, 255, 0), square, 0)


            pygame.draw.rect(w, (50, 50, 50), square, 1)  # outline the cells


def get_path(start, target):
    current_node = target
    path = []
    while current_node != start:
        current_node.is_on_path = True
        path += [current_node]
        current_node = current_node.parent
    return path[::-1]  # path \ start node


def graph_search(grid, start, breadth, w, size):  # uninformed search, find a target node
    queue = deque([start])
    start.visited = True
    while queue:
        current_node = queue.popleft()  # take next node in queue
        # current_node.current = True  # used for graphics
        draw_grid(w, size, grid)
        pygame.display.update()
        # current_node.current = False
        if current_node.is_target:
            return get_path(start, current_node)
        children = current_node.get_children(grid)
        for child in children:
            child.visited = True
            if breadth:
                queue.append(child)
            else:
                queue.appendleft(child)
            child.parent = current_node  # keep track of parent so we can backtrace later


def a_star(grid, start, target, w, size):  # returns the optimal path to target node from start node
    # heuristic function h(c1, c2) = sqrt((c2.x - c1.x)**2 + (c2.y - c1.y)**2))
    # admissible since search cannot take diagonal path
    # cost so far: g
    # f = h + g, i.e. f = cost so far + estimated cost to target
    # start's f is already at 0 so we wont have to initialize it

    open_list = []
    start.g = 0
    start.h = math.sqrt((target.x - start.x)**2+(target.y - start.y)**2)
    start.f = start.h
    open_list += [start]
    while open_list:
        open_list = sorted(open_list, key=lambda n: -n.f)
        current_node = open_list.pop()
        if current_node == target:
            return get_path(start, current_node)
        children = current_node.get_children(grid)  # expand current node
        for child in children:

            temp_g = current_node.g + 1  # since step cost is 1
            # temp_h = math.sqrt((target.x - child.x)**2+(target.y - child.y)**2)
            # child_copy.f = child_copy.g + child_copy.h
            if temp_g < child.g:  # unexplored nodes have inf

                child.parent = current_node
                child.g = temp_g
                child.f = temp_g + math.sqrt((target.x - child.x)**2+(target.y - child.y)**2)
                if child not in open_list:
                    child.visited = True
                    draw_grid(w, size, grid)
                    pygame.display.update()
                    open_list += [child]


def create_maze(wall_list, cells_x, cells_y):
    """Takes a list of tuples with coordinates where walls where put and saves them in a constant maze. """
    grid = create_grid(cells_x, cells_y)
    for i, j in wall_list:
        grid[i][j].is_wall = True
    return grid


walls1 = [(0, 17), (1, 3), (1, 4), (1, 5), (1, 8), (1, 14), (1, 15), (1, 16), (1, 17), (2, 1), (2, 2), (2, 3), (2, 5),
          (2, 6), (2, 8), (2, 11), (2, 12), (3, 2), (3, 3), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12),
          (3, 13), (3, 17), (3, 18), (4, 10), (4, 11), (4, 12), (4, 14), (4, 17), (5, 3), (5, 4), (5, 8), (5, 14),
          (5, 15), (5, 16), (5, 17), (6, 1), (6, 2), (6, 4), (6, 6), (6, 10), (6, 11), (6, 12), (6, 14), (6, 15),
          (7, 1), (7, 4), (7, 6), (7, 12), (7, 16), (8, 1), (8, 4), (8, 6), (8, 7), (8, 8), (8, 11), (8, 12), (8, 15),
          (8, 16), (9, 1), (9, 4), (9, 8), (9, 11), (9, 17), (10, 0), (10, 1), (10, 3), (10, 4), (10, 5), (10, 8),
          (10, 9), (10, 10), (10, 11), (11, 4), (11, 11), (11, 14), (11, 15), (11, 18), (12, 4), (12, 6), (12, 14),
          (12, 15), (12, 17), (12, 18), (13, 2), (13, 3), (13, 4), (13, 8), (13, 9), (13, 13), (14, 1), (14, 2),
          (14, 6), (14, 7), (14, 8), (14, 13), (14, 14), (15, 1), (15, 11), (15, 16), (15, 17), (16, 1), (16, 2),
          (16, 3), (16, 11), (16, 16), (17, 4), (17, 6), (17, 8), (17, 11), (17, 13), (17, 18), (18, 1), (18, 6),
          (18, 9), (18, 10), (18, 13), (18, 14), (18, 17), (18, 18), (19, 0), (19, 1), (19, 13)]

walls2 = [(0, 8), (0, 13), (0, 18), (1, 1), (1, 2), (1, 3), (1, 4), (1, 7), (1, 8), (1, 9), (1, 10), (1, 12), (1, 13),
          (1, 15), (1, 16), (1, 17), (1, 18), (2, 18), (3, 2), (3, 5), (3, 6), (3, 11), (3, 12), (3, 16), (3, 17),
          (3, 18), (4, 2), (4, 3), (4, 5), (4, 8), (4, 11), (4, 17), (5, 2), (5, 7), (5, 8), (5, 9), (5, 11), (5, 15),
          (5, 16), (5, 17), (6, 0), (6, 8), (6, 17), (7, 0), (7, 1), (7, 5), (7, 12), (7, 13), (7, 14), (7, 18),
          (8, 0), (8, 3), (8, 5), (8, 6), (8, 11), (8, 12), (8, 18), (9, 2), (9, 3), (9, 7), (9, 14), (9, 15), (9, 16),
          (10, 8), (10, 15), (10, 16), (11, 0), (11, 1), (11, 5), (11, 6), (11, 8), (11, 9), (11, 10), (11, 12),
          (11, 15), (11, 19), (12, 1), (12, 4), (12, 5), (12, 10), (12, 12), (12, 13), (12, 18), (12, 19), (13, 1),
          (13, 13), (13, 19), (14, 6), (14, 7), (14, 8), (14, 14), (15, 2), (15, 4), (15, 11), (15, 15), (15, 16),
          (16, 1), (16, 2), (16, 3), (16, 4), (16, 5), (16, 9), (16, 10), (16, 11), (16, 18), (17, 2), (17, 3),
          (17, 9), (17, 13), (17, 14), (17, 18), (18, 0), (18, 1), (18, 2), (18, 3), (18, 4), (18, 14), (18, 16),
          (18, 17), (18, 18), (19, 17)]


main()

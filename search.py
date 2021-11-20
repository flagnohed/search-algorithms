from collections import deque
import sys
import pygame
import math


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


def main():
    """
    todo:
    * fix colors
    * add timer
    * add walls random (make random maze)
    * add text showcasing the length of returned path
    * make a "ring" around the search methods with title "choose algorithm:"
    """
    pygame.init()
    w_width = 1000  # x
    w_height = 1000  # y
    search_choice = ""  # can be "BFS", "DFS", "A*"

    w = pygame.display.set_mode((w_width + 200, w_height + 200))
    pygame.display.set_caption("Search visualizer")

    size = 20
    cells_x, cells_y = w_width//size, w_height//size
    grid = create_grid(cells_x, cells_y)
    start_node = None
    # main game loop
    while True:
        # Fix graphics stuff
        w.fill((0, 0, 0))
        bfs_button = Button(1050, 650, w, "BFS")
        dfs_button = Button(1050, 750, w, "DFS")
        a_star_button = Button(1050, 850, w, "A*")
        reset_button = Button(1050, 1000, w, "Reset")
        quit_button = Button(1050, 1100, w, "Quit")
        w.blit(bfs_button.text, (bfs_button.x + 30, bfs_button.y + 10))
        w.blit(dfs_button.text, (dfs_button.x + 30, dfs_button.y + 10))
        w.blit(a_star_button.text, (a_star_button.x + 30, a_star_button.y + 10))
        w.blit(reset_button.text, (reset_button.x + 30, reset_button.y + 10))
        w.blit(quit_button.text, (quit_button.x + 30, quit_button.y + 10))
        pygame.draw.line(w, (255, 255, 255), (1000, 0), (1000, 1000))
        pygame.draw.line(w, (255, 255, 255), (1000, 1000), (0, 1000))

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
                if search_choice:  # if True then some algorithm has run
                    # text at (50, 1050) [search "found a path with length " path_cost!]
                    pass
                # click on reset button:
                    # grid = create_grid(cells_x, cells_y)
                    # reset(w, size)
        # if run button is clicked:
            # run search


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
            if grid[x][y].is_start:
                pygame.draw.rect(w, (0, 255, 0), square, 0)
            if grid[x][y].is_target:
                pygame.draw.rect(w, (0, 0, 255), square, 0)
            if grid[x][y].visited:
                pygame.draw.rect(w, (255, 0, 0), square, 0)
            if grid[x][y].is_on_path or grid[x][y].current:
                pygame.draw.rect(w, (255, 255, 255), square, 0)

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
        current_node.current = True  # used for graphics
        draw_grid(w, size, grid)
        pygame.display.update()
        current_node.current = False
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

    """
    open_list := sorted list on node.f
    closed_list := final path
    set start.f = 0, start.g = 0 and add start to open_list
    while open_list not empty:
        pick node with lowest f
        if node == target:
            return get_path(start, node)
        for child in node.children:
            child_copy = child
            child_copy.g = len(get_path(start, child))
            child_copy.h = heuristic(child, target)
            child_copy.f = child.g + child.h
            if child in open_list:
                if child_copy.f < child.f:
                    # found better
                    child = child_copy # update
            else:
                open_list += [child_copy]

        closed_list += [node]

    """
    open_list = []
    closed_list = []
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
                    open_list += [child]












main()

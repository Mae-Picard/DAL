render_distance = 16
campain_stage = 0
maze = {}

import setup as s
import math
import random
import pyray as pr

in_menu = True
in_world = False
switching_stage = True
first_time = True

def show_resume():
    first_time = False

def initialize_maze():
    maze = {}
    for x, y in [(0, 0), (-16, 0), (0, -16), (-16, -16)]:
        maze = gen_empty_chunk(maze, x, y)
        maze = gen_maze_chunck(maze, x, y)
    return maze


def is_maze_filled(maze):
    for c in maze:
        if len(maze[c]) == 0:
            return False
    return True


def gen_lines_maze(maze, less_x, less_y):
    updated_maze = maze
    for _ in range(8):
        dx, dy = random.choice([(0, 1), (-1, 0), (1, 0), (0, -1)])
        t = 0
        flag = True
        orig_coord = (random.randrange(less_x + 2, less_x + 14), random.randrange(less_y + 2, less_y + 14))
        while flag and ((orig_coord not in updated_maze) or len(updated_maze[orig_coord]) > 0):
            orig_coord = (random.randrange(less_x, less_x + 16), random.randrange(less_y, less_y + 16))
            if t > 32: flag = False
            t += 1
        if flag:
            previous_cell = orig_coord
            ox, oy = orig_coord
            for i in range(1, 9):
                next_cell = (ox + dx * i, oy + dy * i)
                if next_cell not in updated_maze: break # Stop if out of bounds
                updated_maze = connect_cells(updated_maze, previous_cell, next_cell)
                if len(updated_maze[next_cell]) > 0: break # Stop if cell is already connected
                previous_cell = next_cell
    return updated_maze


def rdm_walk(maze, path):
    if len(maze[path[-1]]) > 0: return path
    x, y = path[-1]
    p = path.copy() # Use a copy to avoid unintended mutations
    dx, dy = random.choice([(0, 1), (-1, 0), (1, 0), (0, -1)])
    new_pos = (x + dx, y + dy)
    if new_pos in maze:
        if new_pos not in path: p.append(new_pos)
        else: p = path[:path.index(new_pos) + 1] # Truncate the path to form a loop
    return rdm_walk(maze, p)


def gen_paths_maze(maze, less_x, less_y):
    updated_maze = maze
    t2 = 0
    while not is_maze_filled(updated_maze) and t2 < 128:
        t = 0
        t2 += 1
        flag = True
        orig_coord = (random.randrange(less_x + 2, less_x + 14), random.randrange(less_y + 2, less_y + 14))
        while flag and ((orig_coord not in updated_maze) or len(updated_maze[orig_coord]) > 0):
            orig_coord = (random.randrange(less_x, less_x + 16), random.randrange(less_y, less_y + 16))
            if t > 32: flag = False
            t += 1
        if flag:
            path = rdm_walk(updated_maze, [orig_coord])
            previous_coord = orig_coord
            for coord in path[1:]:
                updated_maze = connect_cells(updated_maze, previous_coord, coord)
                previous_coord = coord
    return updated_maze


def gen_empty_chunk(maze, less_x, less_y):
    for x in range(16):
        for y in range(16):
            coords = (x + less_x, y + less_y)
            if not coords in maze:
                maze[(x + less_x, y + less_y)] = []
    return maze


def gen_maze_chunck(maze, less_x, less_y):
    # Fill the chunck
    updated_maze = maze
    updated_maze = gen_lines_maze(updated_maze, less_x, less_y)
    updated_maze = gen_paths_maze(updated_maze, less_x, less_y)
    return updated_maze


def connect_cells(maze, a, b):
    if a in maze and b in maze:
        if b not in maze[a]: maze[a].append(b)
        if a not in maze[b]: maze[b].append(a)
    return maze


def add_chunck_maze(player_x, player_y):
    global maze
    threshold = 10
    flag = True
    if (player_x + threshold, player_y) not in maze:
        new_less_x = math.copysign((player_x + threshold >> 4) << 4, player_x - 0.1)
        new_less_y = math.copysign((player_y >> 4) << 4, player_y - 0.1)
        flag = False
    elif (player_x - threshold, player_y) not in maze:
        new_less_x = math.copysign((player_x - threshold  >> 4) << 4, player_x - 0.1)
        new_less_y = math.copysign((player_y>> 4) << 4, player_y - 0.1)
        flag = False
    if (player_x, player_y + threshold) not in maze:
        new_less_x = math.copysign((player_x >> 4) << 4, player_x - 0.1)
        new_less_y = math.copysign((player_y + threshold >> 4) << 4, player_y - 0.1)
        flag = False
    elif (player_x, player_y - threshold) not in maze:
        new_less_x = math.copysign((player_x >> 4) << 4, player_x - 0.1)
        new_less_y = math.copysign((player_y - threshold >> 4) << 4, player_y - 0.1)
        flag = False
    if flag: return False
    maze = gen_empty_chunk(maze, new_less_x, new_less_y)
    maze = gen_maze_chunck(maze, new_less_x, new_less_y)
    return True


def wall_pos_for_maze(maze):
    wall_pos = []
    for coord in maze:
        x, y = coord
        connections = maze[coord]
        if random.choice([True, False]):
            if (x, y + 1) not in connections:
                wall_pos.append((coord, "West"))
            elif (x - 1, y) not in connections:
                wall_pos.append((coord, "North"))
        else:
            if (x - 1, y) not in connections:
                wall_pos.append((coord, "North"))
            elif (x, y + 1) not in connections:
                wall_pos.append((coord, "West"))
    return wall_pos


def create_maze(maze):
    walls = wall_pos_for_maze(maze)
    for pos, orientation in walls:
        # dépendant de la région ??
        model, color, refraction = (s.brickwall_model, s.brickwall_color, s.brickwall_refraction)
        s.Wall((pos[0] * s.wall_length, 1, pos[1] * s.wall_length), orientation,
               model, color, refraction, height=5)


def gen_campain(campain_stage):
    global maze
    if campain_stage == -1: # Mode test
        # Création des murs
        s.Wall((1, 1, 0), "North", s.white_wall_model, s.white_wall_color, s.white_wall_refraction)
        s.Wall((6, 1, 0), "North", s.brickwall_model, s.brickwall_color, s.brickwall_refraction)
        # Création des platformes
        s.Floor((10, 3, 7), 3, 4, s.brickwall_model, s.brickwall_color, s.brickwall_refraction)
        s.Floor((3, 1, 5), 3, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        # Pose des blocs
        s.Block((8, 1, 6), s.red_wall_model, s.red_wall_color, s.red_wall_refraction)
        # Ajout des monstres monstrueux
        s.Mob((10, 2, 2), s.mob_model1, 3, 4, 3)
        s.Mob((12, 2, 5), s.mob_model2, 4, 8, 6)
        s.Mob((15, 2, 10), s.mob_model3, 8, 5, 5)
        # Ajout des items
        s.Item((5, 2, 8), s.woodenwall_model, "Block")
        # Séléction de l'arme
        s.gun = s.Gun(s.main_gun_frames, 12, 7, -100, "main")  # arme principale
        s.gun_hotbar = [True, True]

    if campain_stage == 0:  # Mode labyrinthe
        # Création des murs
        maze = initialize_maze()
        create_maze(maze)
        # Séléction de l'arme
        s.gun = s.Gun(s.main_gun_frames, 12, 7, -100, "main")  # arme principale

    if campain_stage == 1:
        # Weapon
        s.gun = s.Gun(s.main_gun_frames, 12, 7, -100, "main")  # arme principale

        # 1st Room Walls
        s.Wall((11, 1, -11), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=23)
        s.Wall((-11, 1, -11), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=23)
        s.Wall((-11, 1, -11), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=23)
        s.Wall((3, 1, 11), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        s.Wall((-10, 1, 11), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        # 1st Room Ground
        s.Floor((0, 0, 0), 21, 21, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        # 1st Corridor
        s.Wall((-3, 1, 11), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=10)
        s.Wall((3, 1, 11), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=10)
        s.Floor((0, 0, 16), 5, 10, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)

        # 2nd Room Walls
        s.Wall((8, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=19)
        s.Wall((-33, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=19)
        s.Wall((3, 1, 20), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=5)
        s.Wall((-33, 1, 20), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=31)
        s.Wall((-25, 1, 38), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=33)
        s.Wall((-32, 1, 38), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=2)
        # 2nd Room Ground
        s.Floor((-13, 0, 29), 41, 17, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        # 2nd Corridor
        s.Wall((-31, 1, 39), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=6)
        s.Wall((-25, 1, 39), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=11)
        s.Wall((-43, 1, 50), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=19)
        s.Wall((-43, 1, 44), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=13)
        s.Floor((-28, 0, 44), 5, 12, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-36, 0, 47), 15, 5, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)

        # 3rd Room
        s.Wall((-59, 1, 20), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=17)
        s.Wall((-59, 1, 60), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=17)
        s.Wall((-43, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=25)
        s.Wall((-43, 1, 51), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=9)
        s.Wall((-59, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        s.Wall((-59, 1, 33), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=28)
        # 3rd Room Ground
        s.Floor((-51, 0, 41), 17, 40, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        # 3rd Corridor
        s.Wall((-66, 1, 27), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        s.Wall((-66, 1, 33), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        s.Floor((-62, 0, 30), 8, 5, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)

        # 4th Room Walls
        s.Wall((-66, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        s.Wall((-66, 1, 33), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=28)
        s.Wall((-107, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=41)
        s.Wall((-107, 1, 61), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=41)
        s.Wall((-107, 1, 20), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=15)
        s.Wall((-87, 1, 20), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=21)
        # 4th Room Ground
        s.Floor((-87, 0, 41), 41, 41, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        # 4th Corridor (with stairs)
        s.Floor((-90, 0, 19), 5, 4, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 1, 15), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 2, 12), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 3, 9), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Wall((-87, 1, 8), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=12, length=12)
        s.Wall((-93, 1, 8), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=12, length=12)
        # stairs roof
        s.Floor((-90, 8, 19), 5, 4, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 9, 15), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 10, 12), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 11, 9), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)

        # Final Room
        s.Wall((-87, 3, 8), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=60)
        s.Wall((-107, 3, 8), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=15)
        s.Wall((-107, 3, -30), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=80)
        s.Wall((-107, 3, -30), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=38)
        s.Wall((-27, 3, -30), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=38)
        # Final Room Ground
        s.Floor((-67, 3, -11), 80, 38, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        
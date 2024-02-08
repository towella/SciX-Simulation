import pygame, math
from random import randint
from game_data import tile_size, screen_width, screen_height
from support import get_angle_rad, get_angle_deg, get_distance


# SET UP FOR PLATFORMER SINCE PLATFORMERS ARE HARDER TO CREATE A PLAYER FOR
class Bilby(pygame.sprite.Sprite):
    def __init__(self, screen_surface, spawn):
        super().__init__()
        self.surface = screen_surface

        # -- player setup --
        # - Body -
        self.speed = 1
        body_radius = 1
        self.body = BodySegment(screen_surface, [spawn[0], spawn[1]], body_radius)

        # -- player movement --
        # collisions -- provides a buffer allowing late collision
        self.collision_tolerance = tile_size

        # - Brain -
        self.brain = Brain(self.body)

# -- getters and setters --
    def get_pos(self):
        return self.body.get_pos()

    def apply_scroll(self, scroll_value):
        # shift position
        pos = self.body.get_pos()
        pos = [pos[0] - int(scroll_value[0]), pos[1] - int(scroll_value[1])]
        self.body.set_pos(pos)
        self.body.sync_hitbox()

        # shift target
        self.brain.target = [self.brain.target[0] - int(scroll_value[0]), self.brain.target[1] - int(scroll_value[1])]

        # shift path
        for t in range(len(self.brain.path)):
            point = self.brain.path[t]
            point = [point[0] - int(scroll_value[0]), point[1] - int(scroll_value[1])]
            self.brain.path[t] = point

# -- update methods --
    def update(self, tiles, scroll_value):
        # -- CHECKS/UPDATE --
        pos = self.body.get_pos()
        # - update brain -
        self.brain.update(tiles)
        target = self.brain.get_target()
        # update body with target
        self.body.update(tiles, target, self.speed)

        # move towards target

        self.apply_scroll(scroll_value)

# -- visual methods --

    def draw(self):
        self.body.draw()

        for i in range(1, len(self.brain.path)):
            pygame.draw.line(self.surface, "red", self.brain.path[i-1], self.brain.path[i], 1)


# --------- BODY ---------

# --- body segments ---

class BodySegment(pygame.sprite.Sprite):
    def __init__(self, surface, spawn, body_rad):
        super().__init__()

        self.surface = surface  # segment render surface
        self.pos = [spawn[0], spawn[1]]  # segment position
        self.prev_pos = self.pos
        self.direction = pygame.Vector2()

        # segment values
        self.radius = body_rad  # collisions and drawn circle

        # collision
        diameter = self.radius * 2
        self.hitbox = pygame.Rect(self.pos[0], self.pos[1], diameter, diameter)
        self.rect = self.hitbox
        self.collision_tolerance = tile_size

    # --- COLLISIONS ---

    '''def collision(self, tiles):
        for tile in tiles:
            distance = get_distance(self.pos, tile.hitbox.center)
            if distance - (tile.radius + self.radius) < 0:
                angle = get_angle_rad(self.pos, self.prev_pos)  # angle to move back towards where seg came from
                self.hitbox.centerx += math.sin(angle) * (tile.radius + self.radius - distance + 1)
                self.hitbox.centery += math.cos(angle) * (tile.radius + self.radius - distance + 1)

                self.pos = [self.hitbox.centerx, self.hitbox.centery]'''

    # checks collision for a given hitbox against given tiles on the x
    def collision_x(self, tiles):
        # -- X Collisions --
        for tile in tiles:
            if tile.hitbox.colliderect(self.hitbox):
                # - normal collision checks -
                # abs ensures only the desired side registers collision
                if abs(tile.hitbox.right - self.hitbox.left) < self.collision_tolerance:
                    self.hitbox.left = tile.hitbox.right
                elif abs(tile.hitbox.left - self.hitbox.right) < self.collision_tolerance:
                    self.hitbox.right = tile.hitbox.left

                self.pos[0] = self.hitbox.centerx

    def collision_y(self, tiles):
        # -- Y Collisions --
        for tile in tiles:
            if tile.hitbox.colliderect(self.hitbox):
                # abs ensures only the desired side registers collision
                if abs(tile.hitbox.top - self.hitbox.bottom) < self.collision_tolerance:
                    self.hitbox.bottom = tile.hitbox.top
                elif abs(tile.hitbox.bottom - self.hitbox.top) < self.collision_tolerance:
                    self.hitbox.top = tile.hitbox.bottom

                self.pos[1] = self.hitbox.centery

    # --- GETTERS AND SETTERS ---

    def get_prev_pos(self):
        return self.prev_pos

    def get_pos(self):
        return self.pos

    def get_radius(self):
        return self.radius

    def set_pos(self, pos):
        self.pos = [pos[0], pos[1]]
        self.sync_hitbox()

    # --- UPDATE AND DRAW ---

    def sync_hitbox(self):
        self.hitbox.center = self.pos
        self.rect = self.hitbox

    def update(self, tiles, target, speed):
        # -- find angle to target --
        angle = get_angle_deg((int(self.pos[0]), int(self.pos[1])), target)
        # TODO dont understand
        if angle == 90:
            angle = 270
        elif angle == 270:
            angle = 90
        angle = math.radians(angle)
        print(math.degrees(angle))
        # -- update position and collision detection --
        # X
        self.pos[0] -= math.sin(angle) * speed
        self.sync_hitbox()  # sync hitbox after pos has been moved ready for collision detection
        self.collision_x(tiles)  # radial x collisions after x movement (separate to y movement)
        # Y
        self.pos[1] += math.cos(angle) * speed
        self.sync_hitbox()  # sync hitbox after pos has been moved ready for collision detection
        self.collision_y(tiles)  # radial y collisions after y movement (separate to x movement)

        self.prev_pos = self.pos  # store current pos in prev_pos ready for next frame

    def draw(self):
        # -- body --
        pygame.draw.circle(self.surface, 'purple', self.pos, 1)
        pygame.draw.circle(self.surface, 'green', self.pos, self.radius, 1)

        pygame.draw.rect(self.surface, 'grey', self.hitbox, 1)  # TODO TESTING hitbox


# --------- BRAIN ---------

class Brain:
    def __init__(self, body):
        self.body = body

        # -- pathfinding --
        pos = [int(body.get_pos()[0]), int(body.get_pos()[1])]
        self.target = pos
        self.path = [pos]  # start path as current position (no target yet defined). Len must be > 0
        self.path_precision = 10  # 15 !!!!! diagonal should be less than tile size !!!!!

    # -- calculate propeties --

    def pathfind(self, target, tiles):
        # TODO simplify code
        target_rect = pygame.Rect((target[0] - self.path_precision // 2, target[1] - self.path_precision // 2), (self.path_precision, self.path_precision))
        # neighbours includes cardinal and diagonal neighbours
        neighbours = [(self.path_precision, 0),
                      (0, self.path_precision),
                      (-self.path_precision, 0),
                      (0, -self.path_precision),
                      (self.path_precision, self.path_precision),
                      (self.path_precision, -self.path_precision),
                      (-self.path_precision, self.path_precision),
                      (-self.path_precision, -self.path_precision)]
        start = (int(self.body.get_pos()[0]), int(self.body.get_pos()[1]))
        # for open and closed dicts: {(xpos, ypos): nodeInstance}
        open = {start: PathNode(start, 0, start, target)}  # nodes to be evaluated (initally only contains starting node)
        closed = {}  # nodes that have been evaluated

        run = True
        while run:
            # if open is empty, indicates no possible path can be found. Generate new target
            if not open.keys():
                return []

            # find node with lowest f cost in open
            current_node = open[list(open.keys())[0]]
            for node in open.keys():
                # if node has better f cost than current node or (the f costs are the same but
                # the h cost is better), set to current
                if open[node].get_f() < current_node.get_f() or (open[node].get_f() == current_node.get_f() and open[node].get_h() < current_node.get_h()):
                    current_node = open[node]

            current_pos = current_node.get_pos()
            # update dicts
            closed[current_pos] = current_node  # add node to closed
            del open[current_pos]  # remove node from open

            # if not the target, check through all the neighbouring positions
            for i in neighbours:
                # find adjacent coordinate
                neighbour_pos = (int(current_pos[0] + i[0]), int(current_pos[1] + i[1]))

                # check node is not already in closed before looping over tiles, if it is skip to next neighbour
                if neighbour_pos not in closed.keys():

                    # ends when neighbour is in target hitbox (prevents path overshoot and also prevents hanging bug
                    # where no neighbour can be both in the hitbox and not in a tile).
                    if target_rect.collidepoint(neighbour_pos):
                        run = False

                    # checks if neighbour is traversable or not, if not skip to next neighbour
                    traversable = True
                    for tile in tiles:
                        if tile.hitbox.collidepoint(neighbour_pos):
                            traversable = False
                            break
                    if traversable:
                        neighbour_g = current_node.get_g() + self.path_precision  # increases g one node further along path
                        # if it is either not in open or path to neighbour is shorter (based on g cost), add to open
                        if neighbour_pos not in open.keys() or neighbour_g < open[neighbour_pos].get_g():
                            # set/update node in open
                            open[neighbour_pos] = PathNode(neighbour_pos, neighbour_g, start, target, current_node)

        # -- Return full path --
        node = closed[current_pos]
        path = [target]
        # keep adding parent positions to path until start node is reached. Follow path using parents
        # does not include start node position (already there)
        while node.get_pos() != start:
            path.append(node.get_pos())
            node = node.get_parent()
        # exit loop with the full path (reversed so the start is at the start and the target is at the end)
        path.reverse()

        return path

    def find_target(self, tiles):
        self.target = (randint(0, screen_width), randint(0, screen_height))
        # continue to randomly generate point until point not in a tile
        repeat = True
        while repeat:
            repeat = False  # assume no repeat required until proven neccessary
            for tile in tiles:
                if tile.hitbox.collidepoint(self.target):
                    self.target = (randint(0, screen_width), randint(0, screen_height))
                    repeat = True  # point has been re-randomized and needs to be tested again
                    break

    # -- getters and setters --
    # returns next point in the path to the real final target
    def get_target(self):
        return self.path[0]

    # -- update --
    def update(self, tiles):
        pos = [int(self.body.pos[0]), int(self.body.pos[1])]

        # find target, if target has been collected (collided with hitbox or equal to pos (for 1px rad))
        if pos == self.target or self.body.hitbox.collidepoint(self.target):
            self.find_target(tiles)

        # create or modify path to target (collided with hitbox or equal to pos (for 1px rad))
        if pos == self.path[0] or self.body.hitbox.collidepoint(self.path[0]):
            self.path = self.path[1:]

        # if path is empty or the final point (the target) != to the current target, recalculate path
        if len(self.path) == 0 or self.path[-1] != self.target:
            self.path = self.pathfind(self.target, tiles)
            # if no path can be found, will return empty path. Gen new target and path
            while not self.path:
                self.find_target(tiles)
                self.path = self.pathfind(self.target, tiles)


class PathNode:
    def __init__(self, pos, g_cost, start, target, parent=None):
        # position
        self.pos = (int(pos[0]), int(pos[1]))

        # points
        self.start = start
        self.target = target

        # parents and children
        self.parent = parent
        self.children = []

        # costs
        # TODO may cause problems if this is incorrect way of calculating them
        self.g = g_cost  # distance from node to start node (not counting this node)
        self.h = int(get_distance(self.pos, target))  # distance from node to target node (not counting this node)
        self.f = self.g + self.h

    # -- getters and setters --

    def get_pos(self):
        return self.pos

    def get_g(self):
        return self.g

    def get_h(self):
        return self.h

    def get_f(self):
        return self.f

    def get_parent(self):
        return self.parent

    def get_children(self):
        return self.children

    def add_child(self, node):
        self.children.append(node)

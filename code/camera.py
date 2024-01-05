import pygame
from game_data import tile_size


class Camera():
    def __init__(self, surface, screen_rect, abs_boundaries):
        self.scroll_value = [0, 0]  # the scroll, shifts the world to create camera effect
        self.abs_boundaries = abs_boundaries

        # -- move --
        self.move_speed = 5

        #-- zoom --
        self.zoom = 1
        self.zoom_speed = 0.1

        # lerp = linear interpolation. Speed the camera takes to center on the player as it moves, (camera smoothing)
        # -- normal lerp --
        self.norm_lerp = 15  # (15) normal camera interpolation speed
        # -- lerp active values --
        self.lerp_x = self.norm_lerp  # controls scroll interpolation amount x (sensitivity of camera to movement of target)
        self.lerp_y = self.norm_lerp  # controls scroll interpolation amount y (sensitivity of camera to movement of target)

        # -- screen dimensions and rect --
        self.screen_width = surface.get_width()
        self.screen_height = surface.get_height()
        self.screen_center_x = surface.get_width() // 2
        self.screen_center_y = surface.get_height() // 2
        self.screen_rect = screen_rect

        # -- boundary collision --
        # separate for x and y so that the shorter one doesn't glitch out with too large a tolerance
        # half screen dimension to snap camera to wall as soon as player turns around anywhere on wall side of screen
        self.collision_tolerance_x = self.screen_width // 2
        self.collision_tolerance_y = self.screen_height // 2

# -- input --

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN]:
            self.scroll_value[1] += self.move_speed
        if keys[pygame.K_UP]:
            self.scroll_value[1] -= self.move_speed
        if keys[pygame.K_LEFT]:
            self.scroll_value[0] -= self.move_speed
        if keys[pygame.K_RIGHT]:
            self.scroll_value[0] += self.move_speed

        # TODO testing remove potentially
        if keys[pygame.K_LSHIFT] and keys[pygame.K_c]:
            self.change_zoom(-self.zoom_speed)
        elif keys[pygame.K_c]:
            self.change_zoom(self.zoom_speed)

# -- camera --

    def change_zoom(self, zoom_amount):
        # Sets zoom amount
        self.zoom += zoom_amount
        # caps min zoom (no negative zoom)
        if self.zoom < 1:
            self.zoom = 1

    def camera_boundaries(self):
        # enables scroll camera boundaries
        for tile in self.abs_boundaries['x']:
            # having proxy variables allows modification of value for maths without moving actual tile pos
            tile_right = tile.hitbox.right
            tile_left = tile.hitbox.left
            # if the screen's horizontal is a pixel away or inside of tile within collision tollerance, stop scroll and snap
            # must be moving towards the wall, otherwise cant move away from the wall in the other direction
            # TODO if on the screen
            # TODO respawn
            # TODO general bounds
            if self.collision_tolerance_x > tile_right >= self.screen_rect.left and self.scroll_value[0] < 0:

                # stop scroll
                self.scroll_value[0] = 0
                # while the screen is in the tile, snap the screen to the tile grid.
                # allows pixel perfect boundaries
                while tile_right > self.screen_rect.left:
                    self.scroll_value[0] += 1
                    tile_right -= 1
                break
            # TODO potentially need abs?
            elif (self.screen_rect.right - self.collision_tolerance_x) < tile_left <= self.screen_rect.right and \
                    self.scroll_value[0] > 0:
                self.scroll_value[0] = 0
                while tile_left < self.screen_rect.right:
                    self.scroll_value[0] -= 1
                    tile_left += 1
                break

        for tile in self.abs_boundaries['y']:
            tile_top = tile.hitbox.top
            tile_bottom = tile.hitbox.bottom
            # TODO potentially need abs?
            if (self.screen_rect.bottom - self.collision_tolerance_y) < tile_top <= self.screen_rect.bottom and \
                    self.scroll_value[1] > 0:
                self.scroll_value[1] = 0
                while tile_top < self.screen_rect.bottom:
                    self.scroll_value[1] -= 1
                    tile_top += 1
                break
            elif self.collision_tolerance_y > tile_bottom >= self.screen_rect.top and self.scroll_value[1] < 0:
                self.scroll_value[1] = 0
                while tile_bottom > self.screen_rect.top:
                    self.scroll_value[1] += 1
                    tile_bottom -= 1
                break

# -- Getters and Setters --

    # scrolls the world when the player hits certain points on the screen
    # dynamic camera tut, dafluffypotato:  https://www.youtube.com/watch?v=5q7tmIlXROg
    def get_scroll(self, dt):
        self.scroll_value = [0, 0]  # reset
        self.get_input()

        self.camera_boundaries()

        # dt
        self.scroll_value[0] = round(self.scroll_value[0] * dt)
        self.scroll_value[1] = round(self.scroll_value[1] * dt)

        return self.scroll_value

    # returns zoom value and offset required to zoom into target point (currently center of screen)
    def get_zoom(self):
        # compensates for zooming to origin by offsetting screen with scroll value
        width = pygame.display.get_surface().get_width()
        height = pygame.display.get_surface().get_height()
        # x = (xz - x)/2
        offset = ((width * self.zoom - width) // 2, (height * self.zoom - height) // 2)
        return self.zoom, offset
# - libraries -
import pygame
from pytmx.util_pygame import load_pygame  # allows use of tiled tile map files for pygame use
# - general -
from game_data import tile_size, fonts
from support import *
# - tiles -
from tiles import StaticTile, CollideableTile, HazardTile
# - agents -
from bilby import Bilby
# - systems -
from camera import Camera
from text import Font


class Level:
    def __init__(self, level_data, sim_data, screen_surface, screen_rect, starting_spawn):
        # TODO testing, remove
        self.dev_debug = False

        # level setup
        self.screen_surface = screen_surface  # main screen surface
        self.screen_rect = screen_rect
        self.screen_width = screen_surface.get_width()
        self.screen_height = screen_surface.get_height()

        self.starting_spawn = starting_spawn
        self.player_spawn = None  # begins as no spawn as filled when player is initialised

        self.pause = False
        self.pause_pressed = False

        dt = 1

        # - get level data -
        tmx_data = load_pygame(resource_path(level_data))  # tile map file
        self.all_tile_sprites = pygame.sprite.Group()  # contains all tile sprites for ease of updating/scrolling
        self.all_object_sprites = pygame.sprite.Group()

        # get tiles
        self.collideable = self.create_tile_layer(tmx_data, 'collideable', 'CollideableTile')
        self.hazards = self.create_tile_layer(tmx_data, 'hazards', 'HazardTile')

        # spawn animals
        self.agents = pygame.sprite.Group()
        self.bilbies = self.create_animals(sim_data["pop_data"]["0"], "bilby")

        # - camera setup -
        room_dim = [tmx_data.width * tile_size, tmx_data.height * tile_size]
        self.camera = Camera(self.screen_surface, self.screen_rect, room_dim)
        scroll_value = self.camera.get_scroll(dt)  # returns scroll
        #self.player.sprite.apply_scroll(scroll_value)  # applies new scroll to player
        self.all_tile_sprites.update(scroll_value)  # applies new scroll to all tile sprites
        self.all_object_sprites.update(scroll_value)  # applies new scroll to all object sprites'''

        # - text setup -
        self.small_font = Font(resource_path(fonts['small_font']), 'white')
        self.large_font = Font(resource_path(fonts['large_font']), 'white')

# -- set up room methods --

    def create_animals(self, pop, type):
        group = pygame.sprite.Group()
        if type == "bilby":
            for i in range(pop):
                spawn = (100, 100)  # TODO randomise within land size
                agent = Bilby(self.screen_surface, spawn)
                self.agents.add(agent)
                group.add(agent)

        return group


    # creates all the neccessary types of tiles seperately and places them in individual layer groups
    def create_tile_layer(self, tmx_file, layer_name, type):
        sprite_group = pygame.sprite.Group()
        layer = tmx_file.get_layer_by_name(layer_name)
        tiles = layer.tiles()
        parallax = (layer.parallaxx, layer.parallaxy)

        if type == "StaticTile":
            # gets layer from tmx and creates StaticTile for every tile in the layer, putting them in both SpriteGroups
            for x, y, surface in tiles:
                tile = StaticTile((x * tile_size, y * tile_size), (tile_size, tile_size), parallax, surface)
                sprite_group.add(tile)
                self.all_tile_sprites.add(tile)

        elif type == 'CollideableTile':
            for x, y, surface in tiles:
                tile = CollideableTile((x * tile_size, y * tile_size), (tile_size, tile_size), parallax, surface)
                sprite_group.add(tile)
                self.all_tile_sprites.add(tile)

        elif type == 'HazardTile':
            pass
            '''for x, y, surface in tiles:
                tile = HazardTile((x * tile_size, y * tile_size), (tile_size, tile_size), parallax, surface,
                                  self.player.sprite)
                sprite_group.add(tile)
                self.all_tile_sprites.add(tile)'''

        else:
            raise Exception(f"Invalid create_tile_group type: '{type}' ")

        return sprite_group

# -- check methods --

    def get_input(self):
        keys = pygame.key.get_pressed()

        # pause pressed prevents holding key and rapidly switching between T and F
        if keys[pygame.K_p]:
            if not self.pause_pressed:
                self.pause = not self.pause
            self.pause_pressed = True
        # if not pressed
        else:
            self.pause_pressed = False

        # TODO testing, remove
        if keys[pygame.K_z] and keys[pygame.K_LSHIFT]:
            self.dev_debug = False
        elif keys[pygame.K_z]:
            self.dev_debug = True

# -- visual --

    # draw tiles in tile group but only if in camera view (in tile.draw method)
    def draw_tile_group(self, group):
        for tile in group:
            # render tile
            tile.draw(self.screen_surface, self.screen_rect)
            # TODO testing, remove
            if self.dev_debug:
                pygame.draw.rect(self.screen_surface, 'green', tile.hitbox, 1)

    # OPTIMISE WITH CAMERA VISION RENDERED ONLY
    def draw_agents(self):
        for agent in self.agents:
            agent.draw()

# -- menus --

    def pause_menu(self):
        pause_surf = pygame.Surface((self.screen_surface.get_width(), self.screen_surface.get_height()))
        pause_surf.fill((40, 40, 40))
        self.screen_surface.blit(pause_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        width = self.large_font.width('PAUSED')
        self.large_font.render('PAUSED', self.screen_surface, (center_object_x(width, self.screen_surface), 20))

# -------------------------------------------------------------------------------- #

    # updates the level allowing tile scroll and displaying tiles to screen
    # order is equivalent of layers
    def update(self, dt):
        # #### INPUT > GAME(checks THEN UPDATE) > RENDER ####
        # checks deal with previous frames interactions. Update creates interactions for this frame which is then diplayed

        # -- INPUT --
        self.get_input()

        # -- CHECKS (For the previous frame)  --
        if not self.pause:

            # scroll -- must be first, camera calculates scroll, stores it and returns it for application
            scroll_value = self.camera.get_scroll(dt)

        # -- UPDATES -- player needs to be before tiles for scroll to function properly
            # TODO IF TILES_IN_SCREEN ATTR IS CHANGED TO INCLUDE MORE LAYERS, CHANGE BACK TO self.collideable HERE!!!!
            self.agents.update(self.collideable, scroll_value)
            self.all_tile_sprites.update(scroll_value)

        # -- RENDER --
        # Draw
        self.draw_tile_group(self.collideable)
        self.draw_tile_group(self.hazards)
        self.draw_agents()

        # must be after other renders to ensure menu is drawn last
        if self.pause:
            self.pause_menu()

        # Dev Tools
        if self.dev_debug:
            '''put debug tools here'''
            pygame.draw.circle(self.screen_surface, "red", (self.screen_width//2, self.screen_height//2), 1)
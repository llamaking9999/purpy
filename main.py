
import pygame
import sys

from soundmanager import SoundManager
from scene import Scene
from levelselect import LevelSelect
from level import Level
from inputmanager import InputManager
from imagemanager import ImageManager
from renderer import Renderer

USE_OPENGL = True

if USE_OPENGL:
    from opengl_renderer import OpenGLRenderer
else:
    from pygame_renderer import PygameRenderer

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
LOGICAL_WIDTH = 320
LOGICAL_HEIGHT = 180
FRAME_RATE = 60


class Game:
    clock = pygame.time.Clock()
    back_buffer: pygame.Surface
    static: pygame.Surface
    renderer: Renderer

    images: ImageManager
    inputs: InputManager
    sounds: SoundManager

    scene: Scene | None

    def __init__(self):
        pygame.init()

        self.back_buffer = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        pygame.display.set_caption('purpy')

        logical = pygame.Rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT)
        destination = self.compute_scaled_buffer_dest()
        window = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        print('initializing renderer')
        if USE_OPENGL:
            self.renderer = OpenGLRenderer(logical, destination, window)
        else:
            self.renderer = PygameRenderer(logical, destination, window)

        print('loading game content')
        self.images = ImageManager()
        self.inputs = InputManager()
        self.sounds = SoundManager()

        if len(sys.argv) > 1:
            self.scene = Level(None, sys.argv[1])
        else:
            self.scene = LevelSelect(None, 'assets/levels')

    def compute_scaled_buffer_dest(self) -> pygame.Rect:
        target_aspect_ratio = LOGICAL_WIDTH / LOGICAL_HEIGHT
        needed_width = target_aspect_ratio * WINDOW_HEIGHT
        if needed_width <= WINDOW_WIDTH:
            # The window is wider than needed.
            return pygame.Rect((WINDOW_WIDTH - needed_width)//2, 0, needed_width, WINDOW_HEIGHT)
        else:
            # The window is taller than needed.
            needed_height = WINDOW_WIDTH / target_aspect_ratio
            return pygame.Rect(0, (WINDOW_HEIGHT - needed_height)//2, WINDOW_WIDTH, needed_height)

    def update(self) -> bool:
        """ Returns True if the game should keep running. """
        if self.scene is None:
            return False

        # Update the actual game logic.
        self.scene = self.scene.update(self.inputs, self.sounds)
        if self.scene is None:
            return False

        self.inputs.update()

        # Clear the back buffer with solid black.
        back_buffer_src = pygame.Rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT)
        self.back_buffer.fill((0, 0, 0), back_buffer_src)
        # Draw the scene.
        self.scene.draw(self.back_buffer, back_buffer_src, self.images)

        self.renderer.render(self.back_buffer)

        return True

    def main(self):
        game_running = True
        while game_running:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        game_running = False
                    case (pygame.KEYDOWN | pygame.KEYUP |
                          pygame.JOYBUTTONDOWN | pygame.JOYBUTTONUP |
                          pygame.JOYAXISMOTION | pygame.JOYHATMOTION |
                          pygame.JOYDEVICEADDED | pygame.JOYDEVICEREMOVED):
                        self.inputs.handle_event(event)

            if not self.update():
                game_running = False

            self.clock.tick(FRAME_RATE)
        pygame.quit()


game = Game()
game.main()

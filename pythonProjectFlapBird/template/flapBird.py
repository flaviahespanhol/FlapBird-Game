import pygame
import os
import random

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

IMAGE_PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGE_FLOOR = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGE_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGES_BIRD = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]
new_width = 550
new_height = 550
IMAGE_GAME_OVER = pygame.image.load(os.path.join('imgs', 'newGameOver.jpeg'))
IMAGE_GAME_OVER_RESIZED = pygame.transform.scale(IMAGE_GAME_OVER, (new_width, new_height))

pygame.font.init()
FONT = pygame.font.SysFont('arial', 38)


class Bird:
    IMAGES = IMAGES_BIRD
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.count_image = 0
        self.image = self.IMAGES[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        displacement = 1.5 * (self.time ** 2) + self.speed * self.time

        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2

        self.y += displacement

        if displacement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPEED

    def draw(self, screen):
        self.count_image += 1

        if self.count_image < self.ANIMATION_TIME:
            self.image = self.IMAGES[0]
        elif self.count_image < self.ANIMATION_TIME * 2:
            self.image = self.IMAGES[1]
        elif self.count_image < self.ANIMATION_TIME * 3:
            self.image = self.IMAGES[2]
        elif self.count_image < self.ANIMATION_TIME * 4:
            self.image = self.IMAGES[1]
        elif self.count_image >= self.ANIMATION_TIME * 4 + 1:
            self.image = self.IMAGES[0]
            self.count_image = 0

        if self.angle <= -80:
            self.image = self.IMAGES[1]
            self.count_image = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.image, self.angle)
        center_image = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotated_image.get_rect(center=center_image)
        screen.blit(rotated_image, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE_PIPE = 240
    SPEED = 8

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.base = 0
        self.TOP_PIPE = pygame.transform.flip(IMAGE_PIPE, False, True)
        self.BASE_PIPE = IMAGE_PIPE
        self.passed_through = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.TOP_PIPE.get_height()
        self.base = self.height + self.DISTANCE_PIPE

    def move(self):
        self.x -= self.SPEED

    def draw(self, screen):
        screen.blit(self.TOP_PIPE, (self.x, self.top))
        screen.blit(self.BASE_PIPE, (self.x, self.base))

    def collision(self, bird):
        bird_mask = bird.get_mask()
        topo_mask = pygame.mask.from_surface(self.TOP_PIPE)
        base_mask = pygame.mask.from_surface(self.BASE_PIPE)

        distancia_topo = (self.x - bird.x, self.top - round(bird.y))
        distancia_base = (self.x - bird.x, self.base - round(bird.y))

        top_point = bird_mask.overlap(topo_mask, distancia_topo)
        base_point = bird_mask.overlap(base_mask, distancia_base)

        if base_point or top_point:
            return True
        else:
            return False


class Floor:
    SPEED = 5
    WIDTH = IMAGE_FLOOR.get_width()
    IMAGE = IMAGE_FLOOR

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x1, self.y))
        screen.blit(self.IMAGE, (self.x2, self.y))


class Game:

    def __init__(self):
        self.bird = Bird(230, 350)
        self.floor = Floor(730)
        self.pipe = [Pipe(700)]
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.score = 0
        self.time = pygame.time.Clock()
        self.running = True
        self.game_over = False

    def run_game(self):
        while self.running:
            while self.game_over:
                self.screen.fill((0, 0, 0))
                final_img = IMAGE_GAME_OVER_RESIZED.get_rect()
                self.screen.blit(IMAGE_GAME_OVER_RESIZED, final_img)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        pygame.quit()
                        quit()

            self.time.tick(30)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    quit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP or evento.type == pygame.FINGERDOWN:
                        self.bird.jump()

            self.bird.move()
            self.floor.move()

            add_pipe = False
            remove_pipe = []
            for cano in self.pipe:
                if cano.collision(self.bird):
                    self.game_over = True
                if not cano.passed_through and self.bird.x > cano.x:
                    cano.passed_through = True
                    add_pipe = True
                cano.move()
                if cano.x + cano.TOP_PIPE.get_width() < 0:
                    remove_pipe.append(cano)

            if add_pipe:
                self.score += 1
                self.pipe.append(Pipe(600))
            for cano in remove_pipe:
                self.pipe.remove(cano)

            if (self.bird.y + self.bird.image.get_height()) > self.floor.y or self.bird.y < 0:
                self.game_over = True

            self.draw_screen()

    def draw_screen(self):
        self.screen.blit(IMAGE_BACKGROUND, (0, 0))
        self.bird.draw(self.screen)
        for pipe in self.pipe:
            pipe.draw(self.screen)

        text = FONT.render(f"Score: {self.score}", 1, (255, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
        self.floor.draw(self.screen)
        pygame.display.update()


def main():
    pygame.init()
    game = Game()
    game.run_game()


if __name__ == "__main__":
    main()

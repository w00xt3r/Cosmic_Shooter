import pygame

class Sprite(pygame.sprite.Sprite):

  def __init__(self, image, startx, starty):
    super().__init__()
    
    self.image = pygame.image.load(image)
    self.rect = self.image.get_rect()
    self.rect.center = (startx, starty)
    self.collider = self.rect.inflate(-5, -5)
    self.x = startx
    self.y = starty

  def draw(self, screen):
    screen.blit(self.image, self.rect)

  def update(self, *args):
    pass

  def move(self, x, y):
    self.rect.move_ip([x, y])
    self.collider.move_ip([x, y])

  def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
  
  def rect(self, value):
        self.x, self.y = value.center
    
class Animation(Sprite):

    def __init__(self, images, startx, starty):
        super().__init__(images[0], startx, starty)
        self.index = 0
        self.images = tuple(map(lambda img: pygame.image.load(img), images))

    def update(self, *args):
        super().update(*args)
        
        self.index += 0.1
        if self.index >= len(self.images):
            self.on_complete()

        self.image = self.images[int(self.index)]

    def on_complete(self):
        self.index = 0

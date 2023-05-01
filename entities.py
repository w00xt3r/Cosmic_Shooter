import pygame, random, math
from pygame.locals import USEREVENT
from sprites import Sprite, Animation
from score import Score

WIDTH, HEIGHT = 600, 400
DEAD = USEREVENT
score = Score(10)

class Player(Sprite):
    def __init__(self, startx, starty, radius):
        spriteId = random.choice(range(0, 12))
        super().__init__(f"assets/ships/ship_00{spriteId:02}.png", startx, starty)
        self.speed = 3.5
        self.lives = 3
        self.last_shot = 0
        self.shoot_delay = 400
        self.radius = self.rect.height // 2
        self.trail = []
        self.inertia = 0.1
        self.angle = 0
        self.original_image = self.image
        self.rotated_image = self.original_image
    def set_speed(self, value):
        self.speed = value

    def set_shoot_delay(self, value):
        self.shoot_delay = value

    def set_image(self, value):
        self.image = value

    def set_rect(self, value):
        self.rect = value

    def set_hitbox(self, value):
        self.hitbox = value

    def set_lives(self, value):
        self.lives = value

    def update(self, enemies, missiles, *args):
        super().update(*args)
        for enemy in enemies:
            distance = math.dist(enemy.rect.center, self.rect.center)
            if distance < self.radius + enemy.radius:
                self.kill()
                event = pygame.event.Event(DEAD, {})
                pygame.event.post(event)
        
        # Collision between player and enemy
        enemy_collisions = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_collisions:
            explosion = Explosion(*enemy.rect.center, size=3)
            missiles.add(explosion)
            self.lives -= 1
            enemy.reset()              
        if self.lives <= 0:
            self.kill()
            pygame.mixer.music.stop()
        
        # MOVEMEENT OF PLAYER
        # Keep the player inside the screen boundaries
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

        # Move the player based on key's pressed
        key = pygame.key.get_pressed()
        self.x_speed = 0
        self.y_speed = 0
        if key[pygame.K_LEFT] or key[pygame.K_a]:
            self.x_speed = -self.speed
            self.angle = 20
        elif key[pygame.K_RIGHT] or key[pygame.K_d]:
            self.x_speed = self.speed
            self.angle = -20
        else:
            self.angle = 0
        if key[pygame.K_UP] or key[pygame.K_w]:
            self.y_speed = -self.speed
        elif key[pygame.K_DOWN] or key[pygame.K_s]:
            self.y_speed = self.speed

        # Normalize the movement vector if necessary
        if self.x_speed != 0 and self.y_speed != 0:
            self.x_speed /= math.sqrt(2)
            self.y_speed /= math.sqrt(2)

        # Apply inertia to player movement
        self.x_speed -= self.inertia * self.x_speed
        self.y_speed -= self.inertia * self.y_speed

        # Move player
        self.move(self.x_speed, self.y_speed)
        #MOVEMENT OF PLAYER FINISH

        # Rotate the player image based on the movement angle
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
            
        # Handle shooting
        now = pygame.time.get_ticks()
        if key[pygame.K_SPACE] and now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot_delay = 400   
            missile_path = space_missile_path
            new_missile = Missile(self.rect.centerx, self.rect.top, missile_path)
            missiles.add(new_missile)
        elif key[pygame.K_LALT] and now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot_delay = 200  
            missile_path = alt_missile_path
            new_missile = Missile(self.rect.centerx, self.rect.top, missile_path)
            missiles.add(new_missile)

        # Remove old trail points that are off-screen
        self.trail = [(x, y + self.speed + 1) for x, y in self.trail if y + 1 < HEIGHT - 90]

        # Add new trail point
        self.trail.append((self.rect.x + 15, self.rect.y + 10))

        # Draw the trail
        trail_color = (90, 90, 110)
        for x, y in self.trail:
            trail_rect = pygame.Rect(x, y, 3, 3)
            pygame.draw.rect(pygame.display.get_surface(), trail_color, trail_rect)
         
class Enemy(Sprite):

  def __init__(self, startx, starty, radius): 
    spriteId = random.choice(range(12, 24))
    super().__init__(f"assets/ships/ship_00{spriteId:02}.png", startx, starty)
    self.image = pygame.transform.rotate(self.image, 180)
    self.radius = self.rect.height // 2
    self.speed = random.uniform(1.0, 1.5)  # randomly initialize speed between 1.0 and 2.0

  def update(self, missiles, *args):
    super().update(*args)
    self.move(0, self.speed * 2)  # move with speed multiplied by 2

  def move(self, x, y):
    if self.rect.y >= HEIGHT:
      self.reset()

    super().move(x, y)
  
  def reset(self):
    self.rect.x += random.randint(0, 100) - 50
    self.rect.y = -random.randint(0, 200)
    self.speed = random.randint(1.0, 2.0)  # randomly initialize speed again after reset
    

class Explosion(Animation):

  def __init__(self, startx, starty, size):
    super().__init__(['assets/props/tile_0006.png'], startx, starty)

  def update(self, *args):
    super().update(*args)
    self.move(0, 1)

  def on_complete(self):
    super().on_complete()
    self.kill()
    
class Missile(pygame.sprite.Sprite):

  def __init__(self, x, y, image_path):
    super().__init__()
    self.image = pygame.image.load(image_path)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.speed = 9

  def update(self, enemies, missiles):
    self.rect.y -= self.speed
    if self.rect.bottom < 0:
      self.kill()

    collisions = pygame.sprite.spritecollide(self, enemies, False)
    for enemy in collisions:
      missiles.add(Explosion(*enemy.rect.center, size=any))
      enemy.reset()
      self.kill()
      score.increment(num_enemies=len(enemies))

# Define the paths for each image
space_missile_path = 'assets/props/tile_0012.png'
alt_missile_path = 'assets/props/tile_0013.png'

# Initialize the missile variable with space_missile_path
missile_path = space_missile_path

class PowerUp(pygame.sprite.Sprite):
    
    POWERUPS = {
        'health': 'assets/props/tile_0024.png',
        'power': 'assets/props/tile_0027.png',
        'speed': 'assets/props/tile_0028.png',
        'small': 'assets/props/tile_0030.png'    
    }

    def __init__(self, kind):
        super().__init__()
        self.image = pygame.image.load(self.POWERUPS[kind])
        self.rect = self.image.get_rect()
        self.kind = kind
        self.timer = 0
        self.timer_started = pygame.time.get_ticks()  # set the timer_started attribute when the powerup is created
        
        # set the power-up's position to a random location
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)

    def update(self, dt):
        self.timer += dt  # update timer with time passed since last frame
        if self.timer >= 5000:  # if timer exceeds 5 seconds (5000 milliseconds)
            self.kill()  # remove the power-up from the group

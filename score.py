import pygame

pygame.init()

screen = pygame.display.set_mode((600, 300))

class Score:
    # handles the score and displays it on the game screen

    def __init__(self, score_increment, time_increment=1):
        #initialize the score object
        self.score_increment = score_increment
        self.time_increment = time_increment
        self.score = 0
        self.score_images = self.load_score_images()
        self.start_time = pygame.time.get_ticks()

    def load_score_images(self):
        #Load the images for displaying the score
        score_images = []
        for i in range(0, 10):
            num_images = [pygame.image.load(f"assets/props/tile_{str(i).zfill(3)}.png").convert_alpha()]
            score_images.append(num_images)
        return score_images

    def get_score_image(self):
        #get the images for displaying the current score
        num_str = str(self.score).zfill(5)
        num_images = [self.score_images[int(i)][0] for i in num_str]
        return num_images

    def draw(self, screen):
        #draw the score on the game screen
        score_images_to_draw = self.get_score_image()
        score_width = 0
        for score_image in score_images_to_draw:
            screen.blit(score_image, (10 + score_width, 10))
            score_width += score_image.get_width() + 2

    def increment(self, num_enemies):
        #increase the score when an enemy is destroyed
        elapsed_time = pygame.time.get_ticks() - self.start_time
        self.score += num_enemies * self.score_increment + elapsed_time // self.time_increment
        self.start_time = pygame.time.get_ticks()

    def reset(self):
        # reset the score to 0 and update the start time
        self.score = 0
        self.start_time = pygame.time.get_ticks()
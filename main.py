import pygame, sys, random
from entities import Player, Enemy, PowerUp
from score import Score


pygame.font.init()
pygame.init()

# Screen dimensions and score increment
WIDTH, HEIGHT = 600, 400
SCORE_INCREMENT = 1
WHITE = (255, 255, 255)

# set the icon for the display surface
icon = pygame.image.load('assets/icon3.png')
pygame.display.set_icon(icon)

intro_shown = False
game_started = False

# Load the score images
def load_score_images():
    score_images = []
    for i in range(10):
        filename = f"assets/props/tile_{i:03}.png"
        image = pygame.image.load(filename)
        score_images.append(image)
    return score_images

# Get the score image for a given score
def get_score_image(score_images, score):
    num_images = []
    for digit in str(score):
        if digit.isdigit():
            num_images.append(score_images[int(digit)])
    return num_images

# Main function
def main():
    pygame.init()
    global intro_shown, game_started

    # Set up the game window and clock
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Set the window caption
    pygame.display.set_caption('C O M S I C   S H O O T E R 🚀')

    # Create the player, enemies, missiles, and score objects
    player = Player(300, 200, 20)
    enemies = pygame.sprite.Group()
    missiles = pygame.sprite.Group()    
    score = Score(SCORE_INCREMENT)
    score.reset()

    # Initialize game over & timer
    game_over = False
    game_over_delay = 1000
    
    # Add the player to the sprite group
    players = pygame.sprite.Group()
    players.add(player)

    # Create the initial enemies and add them to the sprite group    
    for x in range(0, WIDTH, 70):
        x += random.choice(range(0, 100)) - 50
        y = random.choice(range(20, 200)) - 300
        enemies.add(Enemy(x, y, 20))

     # Font set up 
    font = pygame.font.Font('fonts/Pixellettersfull-BnJ5.ttf', 37)
    font_2 = pygame.font.Font('fonts/Pixellettersfull-BnJ5.ttf', 30)

    if not intro_shown:

        instruction_text = "*Instructions*\n Press 'Space' or 'Alt' To Shoot\n'Q' To Exit The Game\n  Press 'Enter' To Continue"

        # Split the instruction text into multiple lines and render each line of the instruction text
        line_surfaces = [font.render(line, True, (WHITE)) for line in instruction_text.splitlines()]

        # Calculate the total height of the instruction text and the y-offset for each line
        total_height = sum(surface.get_height() for surface in line_surfaces)
        y_offset = (HEIGHT - total_height) // 2

        # Blit each line of the instruction text to the screen and update the screen
        for i, line_surface in enumerate(line_surfaces):
            line_rect = line_surface.get_rect(center=(WIDTH // 2, y_offset + i * line_surface.get_height()))
            screen.blit(line_surface, line_rect)

        pygame.display.flip()
        intro_shown = True

    # Wait for the player to start the game
    while not game_started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Start the game
                game_started = True

    # Update the screen
    pygame.display.flip()

    # Set up the DEAD event timer
    DEAD_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(DEAD_EVENT, 2000) 

    # Load score images
    score_images = load_score_images()

    # Define start time
    start_time = pygame.time.get_ticks()

    # Music
    music = pygame.mixer.Sound("audio/background.wav")
    music.set_volume(0.2)
    music.play()

    # Powerup 
    powerups = pygame.sprite.Group()
    POWERUP_TIMER_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(POWERUP_TIMER_EVENT, 5000)
    powerup_duration = 5000

    # Main while loop
    while True:
        game_over = player.lives == 0 and game_over
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Start the game
                game_over = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_r and game_over:
                    game_over = False
                    music.stop()
                    return
                                                
            if event.type == POWERUP_TIMER_EVENT:
                kind = random.choice(list(PowerUp.POWERUPS.keys()))
                powerup = PowerUp(kind)
                powerups.add(powerup)

            for powerup in powerups:
                if powerup.timer_started is None:
                    powerup.timer_started = pygame.time.get_ticks()
                elif pygame.time.get_ticks() - powerup.timer_started >= powerup_duration:
                    powerups.remove(powerup)

                else:
                    powerup_actions = {
                        'speed': lambda player: player.set_speed(player.speed + 0.5),
                        'power': lambda player: player.set_shoot_delay(player.shoot_delay - 75),
                        'small': lambda player: (
                            player.set_image(pygame.transform.scale(player.image, (int(player.rect.width * 0.8), int(player.rect.height * 0.8)))),
                            player.set_rect(player.image.get_rect(center=player.rect.center)),
                            player.set_hitbox(pygame.Rect(player.rect.x + 8, player.rect.y + 8, player.rect.width - 16, player.rect.height - 16)),
                        ),
                        'health': lambda player: player.set_lives(player.lives + 1),
                    }

                    # Check for collision between player and powerup
                    if pygame.sprite.collide_rect(player, powerup):
                        if powerup.kind in powerup_actions:
                            powerup_actions[powerup.kind](player)
                            powerups.remove(powerup)
                                                                         
        # Delay Game Over
        if len(players.sprites()) == 0:
            game_over_delay -= clock.get_time()
        
        if game_over_delay <= 0:
            game_over = True

        # If game not over, update variables
        if not game_over:
            # Fill screen with white color
            background = pygame.image.load('assets/horizonbg.jpg')
            screen.blit(background, (0, 0))
            
            # Game over text
            text = font_2.render(f'LIVES: {player.lives}', True, (WHITE))
            screen.blit(text, (WIDTH - 95, 10))

            pygame.event.pump() # Reset all events
            
            # Update all
            players.update(enemies, missiles)
            enemies.update(missiles)
            missiles.update(enemies, missiles)
            score.increment(SCORE_INCREMENT + (pygame.time.get_ticks() - start_time) // 1000)
                  
            # Draw score
            score_images_to_draw = get_score_image(score_images, score.score)
            score_width = 0
            for score_image in score_images_to_draw:
                screen.blit(score_image, (10 + score_width, 10))
                score_width += score_image.get_width() + 2

            # Draw everything on the screen        
            players.draw(screen)
            missiles.draw(screen)
            enemies.draw(screen)
            powerups.draw(screen)

        else:
            # Define text to display and its position
            game_over_texts = [
                ('GAME OVER', (WIDTH, HEIGHT // 2 - 120)),
                ('FINAL SCORE: {}'.format(score.score), (WIDTH, HEIGHT // 2 - 80)),
                ('Press "R" to Restart', (WIDTH, HEIGHT // 2 + 30)),
                ('Press "Q" to Quit', (WIDTH, HEIGHT // 2 + 80))
            ]

            # Display each text on the screen
            for text, position in game_over_texts:
                rendered_text = font.render(text, False, (WHITE))
                text_x = (position[0] - rendered_text.get_width()) // 2
                text_y = position[1] - rendered_text.get_height() // 2
                screen.blit(rendered_text, (text_x, text_y))

        pygame.display.update() # Update the screen
        clock.tick(100)

if __name__ == "__main__":
    while True:
        main()
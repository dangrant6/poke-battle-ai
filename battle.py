import pygame
from pygame.locals import *
import openai
import random
from dotenv import load_dotenv
import os
import sys
import time

load_dotenv()

pygame.init()
openai.api_key = os.getenv("KEY")

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Pokemon Battle')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

font_small = pygame.font.Font(None, 24)
font_medium = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 48)

poke_types = {
    'Normal': ['Fighting'],
    'Fire': ['Water', 'Rock'],
    'Water': ['Electric', 'Grass'],
    'Electric': ['Ground'],
    'Grass': ['Fire', 'Ice', 'Poison', 'Flying', 'Bug'],
    'Ice': ['Fire', 'Fighting', 'Rock', 'Steel'],
    'Fighting': ['Flying', 'Psychic', 'Fairy'],
    'Poison': ['Ground', 'Psychic'],
    'Ground': ['Water', 'Grass', 'Ice'],
    'Flying': ['Electric', 'Ice', 'Rock'],
    'Psychic': ['Bug', 'Ghost', 'Dark'],
    'Bug': ['Fire', 'Flying', 'Rock'],
    'Rock': ['Water', 'Grass', 'Fighting', 'Ground', 'Steel'],
    'Ghost': ['Ghost', 'Dark'],
    'Dragon': ['Ice', 'Dragon', 'Fairy'],
    'Dark': ['Fighting', 'Bug', 'Fairy'],
    'Steel': ['Fire', 'Fighting', 'Ground'],
    'Fairy': ['Poison', 'Steel']
}

pygame.mixer.music.load("Pokémon HeartGold & SoulSilver - Champion & Red Battle Music (HQ).mp3")

# Create the Pokemon objects
class Pokemon:
    def __init__(self, name, type, level, moves, sprite):
        self.name = name
        self.type = type
        self.level = level
        self.max_health = level * 3.3
        self.current_health = self.max_health
        self.moves = moves
        self.sprite = sprite

    def __str__(self):
        return f'{self.name} ({self.type}) - Level {self.level}'

    def take_damage(self, damage, damage_multiplier=1.0):
        self.current_health -= damage * damage_multiplier
        if self.current_health < 0:
            self.current_health = 0

    def is_fainted(self):
        return self.current_health <= 0
    
    def get_weaknesses(self):
        return poke_types.get(self.type, [])
    
def draw_battle_scene(player_pokemon, ai_pokemon, moves):
    # Load and scale the background image
    img = pygame.image.load("img/bgd.png")  # Replace "red_battle.png" with the actual filename of the image
    img = pygame.transform.scale(img, (800, 600))  # Adjust the screen size as needed

    screen.blit(img, (0, 0))  # Blit the background image onto the screen

    # Draw player's Pokemon
    player_sprite = pygame.image.load(player_pokemon.sprite)
    player_sprite = pygame.transform.scale(player_sprite, (160, 160))  # Adjust the sprite size as needed
    screen.blit(player_sprite, (50, 260))  # Adjust the sprite position
    player_pokemon_text = font_medium.render(str(player_pokemon), True, (0, 0, 0))  # Use black text color
    screen.blit(player_pokemon_text, (240, 260))
    player_moves_label = font_small.render("MOVES", True, (255, 255, 255))  # Use black text color
    screen.blit(player_moves_label, (50, 430))  # Adjust the label position

    if ai_pokemon:
        # Draw AI's Pokemon
        ai_sprite = pygame.image.load(ai_pokemon.sprite)
        ai_sprite = pygame.transform.scale(ai_sprite, (160, 160))  # Adjust the sprite size as needed
        screen.blit(ai_sprite, (590, 40))  # Adjust the sprite position
        ai_pokemon_text = font_medium.render(str(ai_pokemon), True, (255, 255, 255))  # Use black text color
        screen.blit(ai_pokemon_text, (370, 40))

        # Draw health bars
        player_health_bar_width = player_pokemon.current_health / player_pokemon.max_health * 160
        ai_health_bar_width = ai_pokemon.current_health / ai_pokemon.max_health * 160
        pygame.draw.rect(screen, (255, 0, 0), (240, 320, player_health_bar_width, 10))  # Use red color for the player's health bar
        pygame.draw.rect(screen, (255, 0, 0), (590, 180, ai_health_bar_width, 10))  # Use red color for the AI's health bar

        # Draw health labels
        player_health_label = font_small.render(f"{player_pokemon.current_health}/{player_pokemon.max_health}", True, (255, 255, 255))  # Use black text color
        screen.blit(player_health_label, (240, 340))
        ai_health_label = font_small.render(f"{ai_pokemon.current_health}/{ai_pokemon.max_health}", True, (255, 255, 255))  # Use black text color
        screen.blit(ai_health_label, (590, 200))

        # Draw available moves
        for i, move in enumerate(moves):
            move_label = font_small.render(f"{i+1}. {move}", True, (255, 255, 255))  # Use black text color
            screen.blit(move_label, (50, 455 + i * 30))
    pygame.display.update()

def draw_pokemon_selection(pokemon_list):
    screen.fill((255, 255, 255))  # Set a white background color

    img = pygame.image.load("img\sel.jpg")  # Replace "img.png" with your image file
    img = pygame.transform.scale(img, (width, height))
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill((0, 0, 0))  # Fill the surface with black color
    fade_surface.set_alpha(150)  # Adjust the alpha value (0-255) to control the level of fade

    screen.blit(img, (0, 0))
    screen.blit(fade_surface, (0, 0))

    title_label = font_medium.render("Choose Your Pokemon Keys 1-9 0=10:", True, (255, 255, 255))  # Use black text color
    title_x = width // 2 - title_label.get_width() // 2
    title_y = 10  # Adjusted position for the title text
    screen.blit(title_label, (title_x, title_y))

    box_width = 100  # Adjusted box width
    box_height = 120  # Adjusted box height
    padding_x = 40  # Adjusted horizontal padding
    padding_y = 60  # Adjusted vertical padding
    max_columns = 4

    total_width = (box_width + padding_x) * max_columns
    total_height = ((len(pokemon_list) - 1) // max_columns + 1) * (box_height + padding_y)

    start_x = (width - total_width) // 2  # Calculate the starting x position
    start_y = (height - total_height) // 2 + 20  # Adjusted starting y position with an offset

    for i, pokemon in enumerate(pokemon_list):
        # Calculate the position of each Pokemon box
        column = i % max_columns
        row = i // max_columns
        box_x = start_x + column * (box_width + padding_x)
        box_y = start_y + row * (box_height + padding_y)

        # Check if it's the last row
        if row == (len(pokemon_list) - 1) // max_columns:
            # Calculate the number of empty spaces to center the last row
            remaining_pokemon = len(pokemon_list) - (max_columns * row)
            empty_spaces = max_columns - remaining_pokemon
            box_x += (empty_spaces * (box_width + padding_x)) // 2

        # Draw the box for each Pokemon
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (220, 220, 220), box_rect)  # Use a light gray color for the box

        # Load and display the Pokemon sprite
        pokemon_sprite = pygame.image.load(pokemon.sprite)
        pokemon_sprite = pygame.transform.scale(pokemon_sprite, (box_width - 20, box_height - 20))  # Slightly smaller size
        screen.blit(pokemon_sprite, (box_x + 10, box_y + 10))  # Adjusted sprite position

        # Draw the Pokemon label
        pokemon_label = font_small.render(pokemon.name, True, (255, 255, 255))  # Use black text color
        label_x = box_x + (box_width - pokemon_label.get_width()) // 2
        label_y = box_y + box_height + 10
        screen.blit(pokemon_label, (label_x, label_y))

        # Draw the Pokemon level
        level_label = font_small.render(f"Lv. {pokemon.level}", True, (255, 255, 255))  # Use black text color
        level_x = box_x + (box_width - level_label.get_width()) // 2
        level_y = label_y + pokemon_label.get_height() + 5
        screen.blit(level_label, (level_x, level_y))

    pygame.display.update()

# Select the player's Pokemon
def select_player_pokemon(pokemon_list, selected_pokemon_count):
    selected_pokemon = []
    keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
    while len(selected_pokemon) < selected_pokemon_count:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key in keys:
                key_index = keys.index(event.key)
                if len(pokemon_list) >= key_index + 1:
                    selected_pokemon.append(pokemon_list.pop(key_index))

        draw_pokemon_selection(pokemon_list)

    return selected_pokemon

def display_transition_screen():
    pygame.init()
    #pygame.mixer.music.play(-1)
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pokemon")

    # Load the background image
    img = pygame.image.load("red.gif")  # Replace "red_image.png" with the actual filename of your image

    # Create a pixelated version of the background image
    pixelated_img = pygame.transform.scale(img, (160, 120))  # Increase the size of the pixelated image
    pixelated_img = pygame.transform.scale(pixelated_img, (800, 600))  # Scale it back to the desired dimensions

    # Create a surface with the same size as the pixelated image
    fade_surface = pygame.Surface((800, 600))
    fade_surface.fill((0, 0, 0))  # Fill the surface with black color

    # Gradually increase the alpha value of the pixelated image surface
    for alpha in range(0, 256):
        pixelated_img.set_alpha(alpha)
        screen.blit(pixelated_img, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30)  # Delay between each frame to control the speed of the fade-in

    # After the fade-in effect, display the final pixelated image
    screen.blit(pixelated_img, (0, 0))
    pygame.display.flip()

    # Display the "Battle vs. Red" text
    font = pygame.font.Font(None, 64)  # Adjust the font and size as needed
    text = font.render("Battle vs. Red", True, (255, 0, 0))  # Adjust the text color as needed (red: (255, 0, 0))
    text_rect = text.get_rect(center=(400, 50))  # Adjust the text position as needed
    screen.blit(pixelated_img, (0, 0))  # Display the pixelated image as the background
    screen.blit(text, text_rect)
    pygame.display.flip()


    # Wait for 5 seconds
    time.sleep(3)

def generate_ai_response(message):
    # Call the OpenAI API to generate AI responses in parallel
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=message,
        max_tokens=30,  # Adjust the value to limit the response length
        temperature=0.5,  # Adjust the value to control the randomness
        n=3,  # Adjust the number of parallel completions
        stop=None,
        timeout=10,
    )
    choices = response.choices
    return choices[0].text.strip()

def battle(player_team, ai_team):
    #pygame.mixer.music.play(-1)
    # Allow the player to choose their move
    moves = player_team[0].moves
    player_move = None
    while True:
        # Update the display
        draw_battle_scene(player_team[0], ai_team[0], moves)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and len(moves) >= 1:
                    player_move = moves[0]
                elif event.key == pygame.K_2 and len(moves) >= 2:
                    player_move = moves[1]
                elif event.key == pygame.K_3 and len(moves) >= 3:
                    player_move = moves[2]
                elif event.key == pygame.K_4 and len(moves) >= 4:
                    player_move = moves[3]

        if player_move:
            break

    # Generate AI response based on player's move
    player_message = f"The player's Pokemon uses '{player_move}'."
    ai_response = generate_ai_response(player_message)

    # Simulate the AI move
    ai_move = random.choice(ai_team[0].moves)

    # Generate AI response for AI's move
    ai_message = f"The AI's Pokemon uses '{ai_move}'."
    ai_response = generate_ai_response(ai_message)

    # Calculate damage with a random factor
    player_damage = random.randint(1, 6) * 35
    ai_damage = random.randint(1, 6) * 35

    # Check if player's Pokemon type is AI's weakness
    if player_team[0].type in poke_types[ai_team[0].type]:
        player_damage = int(player_damage * 1.5)  # Increase damage by 50%
    if ai_team[0].type in poke_types[player_team[0].type]:
        ai_damage = int(ai_damage * 1.5)  # Increase damage by 50%

    # Apply damage to Pokemon
    player_team[0].take_damage(ai_damage)
    ai_team[0].take_damage(player_damage)

    # Draw the battle scene after the first move
    draw_battle_scene(player_team[0], ai_team[0], moves)

    # Print the AI's move and damage
    print(f"The AI's Pokemon uses '{ai_move}' and deals {ai_damage} damage.")
    if ai_damage > 175:
        print("It's super effective!")
    print(f"Your Pokemon deals {player_damage} damage.")
    if player_damage > 210:
        print("It's super effective!")

    # Generate AI response for player's damage
    player_damage_message = f"Your Pokemon deals {player_damage} damage."
    ai_damage_response = generate_ai_response(player_damage_message)

    # Determine the battle result
    if player_team[0].is_fainted() and ai_team[0].is_fainted():
        print("It's a tie!")
        if len(player_team) > 1 and len(ai_team) > 1:
            player_team.pop(0)
            ai_team.pop(0)
            battle(player_team, ai_team)
    elif player_team[0].is_fainted():
        print("Your Pokemon fainted!")
        # Switch to the next available Pokemon
        player_team.pop(0)
    elif ai_team[0].is_fainted():
        print("The AI's Pokemon fainted!")
        # Switch to the next available Pokemon
        ai_team.pop(0)
    else:
        print("The battle continues!")

    pygame.time.wait(500)  # Wait for 1 second before proceeding to the next move


# Create a list of available Pokemon for the player to choose from
available_pokemon = [
    Pokemon('Mewtwo', 'Psychic', 100, ['Psycho Cut', 'Close Combat', 'Psychic', 'Shadow Ball'], 'img\mewtwo.png'),
    Pokemon('Tornadus', 'Flying', 100, ['Omnious Wind', 'Hurricane', 'Blackwind Storm', 'Air Slash'], 'img/tornadus.png'),
    Pokemon('Moltres', 'Fire', 100, ['Flamethrower', 'Overheat', 'AncientPower', 'Heat Wave'], 'img\moltres.png'),
    Pokemon('Lucario', 'Fighting', 100, ['Shadow Claw', 'Close Combat', 'Aura Sphere', 'Giga Impact'], 'img\lucario.png'),
    Pokemon('Groudon', 'Ground', 100, ['Eruption', 'Crunch', 'Earthquake', 'Earth Power'], 'img\groudon.png'),
    Pokemon('Kyogre', 'Water', 100, ['Hydro Pump', 'Water Spout', 'Muddy Water', 'Surf'], 'img\kyogre.png'),
    Pokemon('Zapdos', 'Electric', 100, ['Thunder', 'Fly', 'Thunderbolt', 'Discharge'], 'img\zapdos.png'),
    Pokemon('Giratina', 'Ghost', 100, ['Shadow Ball', 'Dark Pulse', 'Psychic', 'Earthquake'], 'img\giratina.png'),
    Pokemon('Torterra', 'Grass', 100, ['Thunder', 'Solar Beam', 'Leaf Storm', 'Energy Ball'], 'img/torterra.png'),
    Pokemon('Articuno', 'Ice', 100, ['Ice Beam', 'Blizzard', 'Aerial Ace', 'Sky Attack'], 'img/articuno.png')
]

def select_ai_pokemon(player_team, available_pokemon):
    player_weaknesses = []
    for player_pokemon in player_team:
        player_weaknesses.extend(player_pokemon.get_weaknesses())

    max_weakness_count = float('-inf')
    best_ai_pokemon = None

    for ai_pokemon in available_pokemon:
        ai_weaknesses = ai_pokemon.get_weaknesses()
        weaknesses_count = sum(1 for weakness in ai_weaknesses if weakness in player_weaknesses)
        if weaknesses_count > max_weakness_count:
            max_weakness_count = weaknesses_count
            best_ai_pokemon = ai_pokemon

    return best_ai_pokemon

# Team draft process
def team_draft(pokemon_list):
    player_team = select_player_pokemon(pokemon_list[:], 3)
    ai_team = []

    for _ in range(3):
        available_pokemon = [pokemon for pokemon in pokemon_list if pokemon not in player_team + ai_team]
        if not available_pokemon:
            break

        ai_pokemon = select_ai_pokemon(player_team, available_pokemon)
        if ai_pokemon:
            ai_team.append(ai_pokemon)
        else:
            break
    fade_surf = pygame.Surface((800, 600))
    fade_surf.fill((0, 0, 0))  # Fill the surface with black initially
    for alpha in range(0, 255, 15):  # Adjust the increment value as needed for the desired fade speed
        fade_surf.set_alpha(alpha)
        screen.blit(fade_surf, (0, 0))
        pygame.display.flip()
        pygame.time.delay(50)  # Adjust the delay time as needed
    return player_team, ai_team

# Perform the team draft
player_team, ai_team = team_draft(available_pokemon)
pygame.mixer.music.play(-1)
display_transition_screen()


# Start the battle
battle(player_team, ai_team)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # Perform the battle
    battle(player_team, ai_team)

    # Check if either team is out of Pokemon
    if len(player_team) == 0 or len(ai_team) == 0:
        running = False

pygame.quit()
sys.exit()
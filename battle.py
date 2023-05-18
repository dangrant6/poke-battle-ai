import pygame
import openai
import random
from dotenv import load_dotenv, dotenv_values
import os
import sys

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

# Create the Pokemon objects
class Pokemon:
    def __init__(self, name, type, level):
        self.name = name
        self.type = type
        self.level = level
        self.max_health = level * 3.3
        self.current_health = self.max_health

    def __str__(self):
        return f'{self.name} ({self.type}) - Level {self.level}'

    def take_damage(self, damage):
        self.current_health -= damage
        if self.current_health < 0:
            self.current_health = 0

    def is_fainted(self):
        return self.current_health <= 0

def draw_battle_scene(player_pokemon, ai_pokemon, moves):
    screen.fill(WHITE)

    # Draw player's Pokemon
    player_pokemon_text = font_medium.render(str(player_pokemon), True, BLACK)
    screen.blit(player_pokemon_text, (50, 50))
    player_moves_label = font_small.render("Moves:", True, BLACK)
    screen.blit(player_moves_label, (50, 100))

    if ai_pokemon:
        # Draw AI's Pokemon
        ai_pokemon_text = font_medium.render(str(ai_pokemon), True, BLACK)
        screen.blit(ai_pokemon_text, (width - ai_pokemon_text.get_width() - 50, 50))

        # Draw health bars
        player_health_bar_width = player_pokemon.current_health / player_pokemon.max_health * (width // 2 - 100)
        ai_health_bar_width = ai_pokemon.current_health / ai_pokemon.max_health * (width // 2 - 100)
        pygame.draw.rect(screen, RED, (50, 150, player_health_bar_width, 30))
        pygame.draw.rect(screen, RED, (width // 2 + 50, 150, ai_health_bar_width, 30))

        # Draw health labels
        player_health_label = font_small.render(f"HP: {player_pokemon.current_health}/{player_pokemon.max_health}", True, BLACK)
        screen.blit(player_health_label, (50, 200))
        ai_health_label = font_small.render(f"HP: {ai_pokemon.current_health}/{ai_pokemon.max_health}", True, BLACK)
        screen.blit(ai_health_label, (width - ai_health_label.get_width() - 50, 200))

        # Draw available moves
        for i, move in enumerate(moves):
            move_label = font_small.render(f"{i+1}. {move}", True, BLACK)
            screen.blit(move_label, (50, 250 + i*30))

    # Update the display
    pygame.display.update()

# Draw the Pokemon selection screen
def draw_pokemon_selection(pokemon_list):
    screen.fill(WHITE)

    title_label = font_medium.render("Choose Your Pokemon:", True, BLACK)
    screen.blit(title_label, (width // 2 - title_label.get_width() // 2, 50))

    for i, pokemon in enumerate(pokemon_list):
        pokemon_label = font_small.render(f"{i+1}. {pokemon}", True, BLACK)
        screen.blit(pokemon_label, (width // 2 - pokemon_label.get_width() // 2, 150 + i*30))

    pygame.display.update()

# Select the player's Pokemon
def select_player_pokemon(pokemon_list, selected_pokemon_count):
    selected_pokemon = []
    while len(selected_pokemon) < selected_pokemon_count:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and len(pokemon_list) >= 1:
                    selected_pokemon.append(pokemon_list.pop(0))
                elif event.key == pygame.K_2 and len(pokemon_list) >= 2:
                    selected_pokemon.append(pokemon_list.pop(0))
                elif event.key == pygame.K_3 and len(pokemon_list) >= 3:
                    selected_pokemon.append(pokemon_list.pop(0))

        draw_pokemon_selection(pokemon_list)

    return selected_pokemon

# Perform a battle between the player and AI
def battle(player_team, ai_team):
    # Allow the player to choose their move
    moves = ['Tackle', 'Growl', 'Ember']
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

        if player_move:
            break

    # Simulate the AI move
    ai_move = random.choice(moves)

    # Calculate damage with a random factor
    player_damage = random.randint(1, 6) * 35
    ai_damage = random.randint(1, 6) * 35

    # Apply damage to Pokemon
    player_team[0].take_damage(ai_damage)
    ai_team[0].take_damage(player_damage)

    # Check if any Pokemon is fainted
    player_fainted = player_team[0].is_fainted()
    ai_fainted = ai_team[0].is_fainted()

    # Draw the final battle scene
    draw_battle_scene(player_team[0], ai_team[0], moves)

    # Print the AI's move and damage
    print(f"The AI's Pokemon uses '{ai_move}' and deals {ai_damage} damage.")
    print(f"Your Pokemon deals {player_damage} damage.")

    # Determine the battle result
    if player_fainted and ai_fainted:
        print("It's a tie!")
    elif player_fainted:
        print("You lost the battle.")
    elif ai_fainted:
        print("You won the battle!")
    else:
        print("The battle continues!")

# Create a list of available Pokemon for the player to choose from
available_pokemon = [Pokemon('Galade', 'Psychic', 100), Pokemon('Ninetales', 'Fire', 100), Pokemon('Moltres', 'Fire', 100), Pokemon('Lucario', 'Fighting', 100), Pokemon('Tyrantitar', 'Ground', 100), Pokemon('Porygon2', 'Normal', 100)]

# Team draft process
def team_draft(pokemon_list):
    player_team = select_player_pokemon(pokemon_list[:], 3)
    ai_team = random.sample(pokemon_list, 3)
    return player_team, ai_team

# Perform the team draft
player_team, ai_team = team_draft(available_pokemon)

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

    # Check if either Pokemon has fainted
    if player_team[0].is_fainted() or ai_team[0].is_fainted():
        running = False

pygame.quit()
sys.exit()
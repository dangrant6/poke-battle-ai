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
    screen.fill(WHITE)

    # Draw player's Pokemon
    player_pokemon_text = font_medium.render(str(player_pokemon), True, BLACK)
    screen.blit(player_pokemon_text, (50, 50))
    player_sprite = pygame.image.load(player_pokemon.sprite)
    screen.blit(player_sprite, (50, 50))
    player_moves_label = font_small.render("Moves:", True, BLACK)
    screen.blit(player_moves_label, (50, 100))

    if ai_pokemon:
        # Draw AI's Pokemon
        ai_pokemon_text = font_medium.render(str(ai_pokemon), True, BLACK)
        screen.blit(ai_pokemon_text, (width - ai_pokemon_text.get_width() - 50, 50))
        ai_sprite = pygame.image.load(ai_pokemon.sprite)
        screen.blit(ai_sprite, (width - ai_sprite.get_width() - 50, 50))

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

# Perform a battle between the player and AI
def battle(player_team, ai_team):
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

    # Simulate the AI move
    ai_move = random.choice(ai_team[0].moves)

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

    pygame.time.wait(1000)  # Wait for 1 second before proceeding to the next move


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

    # Check if either team is out of Pokemon
    if len(player_team) == 0 or len(ai_team) == 0:
        running = False

pygame.quit()
sys.exit()
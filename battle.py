import pygame
from pygame.locals import *
import random
import requests
from dotenv import load_dotenv
import os
import sys
import time
import math

load_dotenv()
pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Pokemon Battle')
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
font_small = pygame.font.Font(None, 24)
font_medium = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 48)

# Add new music loading function
def load_music(filename):
    return pygame.mixer.Sound(os.path.join("mus", filename))

# Load music files
selection_music = load_music("select.mp3")
victory_music = [load_music("frlg.mp3"), load_music("platinum.mp3")]
defeat_music = load_music("cafe.mp3")

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

pygame.mixer.music.load("mus/hgss.mp3")

class Pokemon:
    def __init__(self, name, type, level, moves, sprite):
        self.name = name
        self.type = type
        self.level = level
        self.max_health = int(level * 3.3)
        self.current_health = self.max_health
        self.moves = moves
        self.sprite = sprite

    def __str__(self):
        return f'{self.name} ({self.type}) - Level {self.level}'

    def take_damage(self, damage, damage_multiplier=1.0):
        self.current_health -= int(damage * damage_multiplier)
        self.current_health = max(0, self.current_health - damage)

    def is_fainted(self):
        return self.current_health <= 0
    
    def get_weaknesses(self):
        return poke_types.get(self.type, [])
    
available_pokemon = [
    Pokemon('Mewtwo', 'Psychic', 100, ['Psycho Cut', 'Close Combat', 'Psychic', 'Shadow Ball'], r'img\mewtwo.png'),
    Pokemon('Tornadus', 'Flying', 100, ['Omnious Wind', 'Hurricane', 'Blackwind Storm', 'Air Slash'], 'img/tornadus.png'),
    Pokemon('Moltres', 'Fire', 100, ['Flamethrower', 'Overheat', 'AncientPower', 'Heat Wave'], r'img\moltres.png'),
    Pokemon('Lucario', 'Fighting', 100, ['Shadow Claw', 'Close Combat', 'Aura Sphere', 'Giga Impact'], r'img\lucario.png'),
    Pokemon('Groudon', 'Ground', 100, ['Eruption', 'Crunch', 'Earthquake', 'Earth Power'], r'img\groudon.png'),
    Pokemon('Kyogre', 'Water', 100, ['Hydro Pump', 'Water Spout', 'Muddy Water', 'Surf'], r'img\kyogre.png'),
    Pokemon('Zapdos', 'Electric', 100, ['Thunder', 'Fly', 'Thunderbolt', 'Discharge'], r'img\zapdos.png'),
    Pokemon('Giratina', 'Ghost', 100, ['Shadow Ball', 'Dark Pulse', 'Psychic', 'Earthquake'], r'img\giratina.png'),
    Pokemon('Torterra', 'Grass', 100, ['Thunder', 'Solar Beam', 'Leaf Storm', 'Energy Ball'], 'img/torterra.png'),
    Pokemon('Articuno', 'Ice', 100, ['Ice Beam', 'Blizzard', 'Aerial Ace', 'Sky Attack'], 'img/articuno.png')
]

class BattleScene:
    def __init__(self):
        self.background = self.load_battle_background()

    def load_battle_background(self):
        backgrounds = [
            "img/e4_bg.png",
            "img/grass_bg.png",
            "img/cave_bg.png",
            "img/water_bg.png"
        ]
        selected_background = pygame.image.load(random.choice(backgrounds))
        return pygame.transform.scale(selected_background, (800, 600))

    def draw(self, screen, player_pokemon, ai_pokemon, moves):
        screen.blit(self.background, (0, 0))

        player_sprite = pygame.image.load(player_pokemon.sprite)
        player_sprite = pygame.transform.scale(player_sprite, (160, 160)) 
        screen.blit(player_sprite, (50, 260)) 
        player_pokemon_text = font_medium.render(str(player_pokemon), True, (255, 255, 255)) 
        screen.blit(player_pokemon_text, (240, 260))
        player_moves_label = font_small.render("MOVES", True, (255, 255, 255)) 
        screen.blit(player_moves_label, (50, 430))  

        if ai_pokemon:
            ai_sprite = pygame.image.load(ai_pokemon.sprite)
            ai_sprite = pygame.transform.scale(ai_sprite, (160, 160)) 
            screen.blit(ai_sprite, (590, 40)) 
            ai_pokemon_text = font_medium.render(str(ai_pokemon), True, (255, 255, 255)) 
            screen.blit(ai_pokemon_text, (370, 40))

            player_health_bar_width = int(player_pokemon.current_health / player_pokemon.max_health * 160)
            ai_health_bar_width = int(ai_pokemon.current_health / ai_pokemon.max_health * 160)
            pygame.draw.rect(screen, (255, 0, 0), (240, 320, player_health_bar_width, 10)) 
            pygame.draw.rect(screen, (255, 0, 0), (590, 180, ai_health_bar_width, 10)) 

            player_health_label = font_small.render(f"{int(player_pokemon.current_health)}/{player_pokemon.max_health}", True, (255, 255, 255))
            screen.blit(player_health_label, (240, 340))
            ai_health_label = font_small.render(f"{int(ai_pokemon.current_health)}/{ai_pokemon.max_health}", True, (255, 255, 255))
            screen.blit(ai_health_label, (590, 200))

            for i, move in enumerate(moves):
                move_label = font_small.render(f"{i+1}. {move}", True, (255, 255, 255))
                screen.blit(move_label, (50, 455 + i * 30))
        
        pygame.display.update()

def draw_pokemon_selection(pokemon_list):
    screen.fill((255, 255, 255))

    img = pygame.image.load("img/sel.jpg")
    img = pygame.transform.scale(img, (width, height))
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill((0, 0, 0)) 
    fade_surface.set_alpha(150) 
    screen.blit(img, (0, 0))
    screen.blit(fade_surface, (0, 0))

    title_label = font_medium.render("Choose Your Pokemon Keys 1-9 0=10:", True, (255, 255, 255))
    title_x = width // 2 - title_label.get_width() // 2
    title_y = 10
    screen.blit(title_label, (title_x, title_y))

    box_width = 100 
    box_height = 120 
    padding_x = 40 
    padding_y = 60 
    max_columns = 4
    total_width = (box_width + padding_x) * max_columns
    total_height = ((len(pokemon_list) - 1) // max_columns + 1) * (box_height + padding_y)
    start_x = (width - total_width) // 2 
    start_y = (height - total_height) // 2 + 20 

    for i, pokemon in enumerate(pokemon_list):
        column = i % max_columns
        row = i // max_columns
        box_x = start_x + column * (box_width + padding_x)
        box_y = start_y + row * (box_height + padding_y)
        if row == (len(pokemon_list) - 1) // max_columns:
            remaining_pokemon = len(pokemon_list) - (max_columns * row)
            empty_spaces = max_columns - remaining_pokemon
            box_x += (empty_spaces * (box_width + padding_x)) // 2
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (220, 220, 220), box_rect) 
        pokemon_sprite = pygame.image.load(pokemon.sprite)
        pokemon_sprite = pygame.transform.scale(pokemon_sprite, (box_width - 20, box_height - 20)) 
        screen.blit(pokemon_sprite, (box_x + 10, box_y + 10)) 
        pokemon_label = font_small.render(pokemon.name, True, (255, 255, 255)) 
        label_x = box_x + (box_width - pokemon_label.get_width()) // 2
        label_y = box_y + box_height + 10
        screen.blit(pokemon_label, (label_x, label_y))
        level_label = font_small.render(f"Lv. {pokemon.level}", True, (255, 255, 255))
        level_x = box_x + (box_width - level_label.get_width()) // 2
        level_y = label_y + pokemon_label.get_height() + 5
        screen.blit(level_label, (level_x, level_y))
    pygame.display.update()

def select_player_pokemon(pokemon_list, selected_pokemon_count):
    selection_music.play(-1)
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

    selection_music.stop()
    return selected_pokemon

def transition_screen():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pokemon")
    img = pygame.image.load("img/red.gif")

    pixelated_img = pygame.transform.scale(img, (160, 120))
    pixelated_img = pygame.transform.scale(pixelated_img, (800, 600)) 
    fade_surface = pygame.Surface((800, 600))
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 256):
        pixelated_img.set_alpha(alpha)
        screen.blit(pixelated_img, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30) 
    screen.blit(pixelated_img, (0, 0))
    pygame.display.flip()

    font = pygame.font.Font(None, 64) 
    text = font.render("Battle vs. Red", True, (255, 0, 0)) 
    text_rect = text.get_rect(center=(400, 50))
    screen.blit(pixelated_img, (0, 0)) 
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(3)

def end_game_screen(result):
    screen.fill((0, 0, 0))
    bg_image = pygame.image.load("img/end_bg.png")
    bg_image = pygame.transform.scale(bg_image, (width, height))
    screen.blit(bg_image, (0, 0))
    # semi-transparent overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    # Render the result text
    if result == "win":
        text = font_large.render("Victory!", True, (255, 215, 0))  # Gold color for victory
        random.choice(victory_music).play()
    else:
        text = font_large.render("Defeat", True, (255, 0, 0))  # Red color for defeat
        defeat_music.play()
    
    text_rect = text.get_rect(center=(width // 2, height // 2))
    screen.blit(text, text_rect)
    
    exit_text = font_small.render("Press any key to exit", True, (255, 255, 255))
    exit_text_rect = exit_text.get_rect(center=(width // 2, height - 50))
    screen.blit(exit_text, exit_text_rect)
    
    pygame.display.flip()
    
    # Wait for a keypress or quit event
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

    # Stop all music
    pygame.mixer.stop()

# Llama 3.1
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Please set the OPENROUTER_API_KEY in your .env file")

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def generate_ai_response(message, temperature=0.7):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [{"role": "user", "content": message}],
        "temperature": temperature
    }
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "I couldn't generate a response. Please try again."

def generate_ai_strategy(ai_pokemon, player_pokemon):
    prompt = f"""
    As an AI Pokemon trainer, devise a strategy for the next turn:
    Your Pokemon: {ai_pokemon.name} (type: {ai_pokemon.type}, moves: {', '.join(ai_pokemon.moves)})
    Opponent's Pokemon: {player_pokemon.name} (type: {player_pokemon.type})
    Consider type advantages and potential moves. Provide a brief strategy explanation.
    """
    return generate_ai_response(prompt, temperature=0.7)

def generate_battle_commentary(player_pokemon, ai_pokemon, player_move, ai_move, player_damage, ai_damage):
    prompt = f"""
    Provide a brief, exciting commentary for this Pokemon battle turn:
    Player's {player_pokemon.name} (type: {player_pokemon.type}) used {player_move} and dealt {player_damage} damage.
    AI's {ai_pokemon.name} (type: {ai_pokemon.type}) used {ai_move} and dealt {ai_damage} damage.
    Consider type advantages and the effectiveness of the moves. Keep it concise and thrilling!
    """
    return generate_ai_response(prompt, temperature=0.8)

def battle(screen, player_team, ai_team):
    battle_scene = BattleScene()
    moves = player_team[0].moves
    player_move = None

    while len(player_team) > 0 and len(ai_team) > 0:
        player_pokemon = player_team[0]
        ai_pokemon = ai_team[0]
        moves = player_pokemon.moves
        player_move = None

        while True:
            battle_scene.draw(screen, player_pokemon, ai_pokemon, moves)
            
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
        
        ai_strategy = generate_ai_strategy(ai_pokemon, player_pokemon)
        print("AI's strategy:", ai_strategy)
        
        ai_move_prompt = f"Based on the strategy: '{ai_strategy}', choose a move for {ai_pokemon.name} from: {', '.join(ai_pokemon.moves)}. Respond with only the move name."
        ai_move = generate_ai_response(ai_move_prompt, temperature=0.5)

        player_damage = random.randint(35, 210)
        ai_damage = random.randint(35, 210)

        if player_pokemon.type in poke_types[ai_pokemon.type]:
            player_damage = int(player_damage * 1.5)
        if ai_pokemon.type in poke_types[player_pokemon.type]:
            ai_damage = int(ai_damage * 1.5)

        player_pos = (210, 340)
        ai_pos = (590, 140)

        if player_move:
            attack_animation(screen, battle_scene, player_pokemon, ai_pokemon, moves, player_pos, ai_pos)
        if ai_move:
            attack_animation(screen, battle_scene, player_pokemon, ai_pokemon, moves, ai_pos, player_pos)

        old_player_health = player_pokemon.current_health
        old_ai_health = ai_pokemon.current_health

        player_pokemon.take_damage(ai_damage)
        ai_pokemon.take_damage(player_damage)

        animate_health_bar(screen, battle_scene, player_pokemon, ai_pokemon, moves, player_pokemon, old_player_health, player_pokemon.current_health)
        animate_health_bar(screen, battle_scene, player_pokemon, ai_pokemon, moves, ai_pokemon, old_ai_health, ai_pokemon.current_health)

        battle_scene.draw(screen, player_pokemon, ai_pokemon, moves)

        commentary = generate_battle_commentary(player_pokemon, ai_pokemon, player_move, ai_move, player_damage, ai_damage)
        print(commentary)

        if player_pokemon.is_fainted() and ai_pokemon.is_fainted():
            print("Both Pokemon fainted!")
            player_team.pop(0)
            ai_team.pop(0)
        elif player_pokemon.is_fainted():
            print("Your Pokemon fainted!")
            player_team.pop(0)
        elif ai_pokemon.is_fainted():
            print("The AI's Pokemon fainted!")
            ai_team.pop(0)
        else:
            print("The battle continues!")

        pygame.time.wait(2000)

        # Check if either team has been defeated
        if len(player_team) == 0:
            return "loss"
        elif len(ai_team) == 0:
            return "win"

    # If we somehow exit the loop without a clear winner, return a draw
    return "draw"

def select_ai_pokemon(player_team, available_pokemon):
    prompt = f"""
    As an AI Pokemon trainer, choose the best Pokemon to battle against the player's team:
    Player's team: {', '.join([f"{p.name} ({p.type})" for p in player_team])}
    Available Pokemon: {', '.join([f"{p.name} ({p.type})" for p in available_pokemon])}
    Consider type advantages and team composition. Respond with only the name of the chosen Pokemon.
    """
    chosen_name = generate_ai_response(prompt, temperature=0.5).strip()
    chosen_pokemon = next((p for p in available_pokemon if p.name.lower() == chosen_name.lower()), None)
    return chosen_pokemon or random.choice(available_pokemon)

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
    fade_surf.fill((0, 0, 0))
    for alpha in range(0, 255, 15):
        fade_surf.set_alpha(alpha)
        screen.blit(fade_surf, (0, 0))
        pygame.display.flip()
        pygame.time.delay(50)
    return player_team, ai_team

def attack_animation(screen, battle_scene, player_pokemon, ai_pokemon, moves, attacker_pos, target_pos, duration=500):
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        elapsed = pygame.time.get_ticks() - start_time
        progress = elapsed / duration
        
        x = attacker_pos[0] + (target_pos[0] - attacker_pos[0]) * progress
        y = attacker_pos[1] + (target_pos[1] - attacker_pos[1]) * progress - math.sin(progress * math.pi) * 50
        
        battle_scene.draw(screen, player_pokemon, ai_pokemon, moves)
        pygame.draw.circle(screen, (255, 0, 0), (int(x), int(y)), 10)
        pygame.display.flip()
        pygame.time.delay(16)

def animate_health_bar(screen, battle_scene, player_pokemon, ai_pokemon, moves, target_pokemon, start_health, end_health, duration=1000):
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        elapsed = pygame.time.get_ticks() - start_time
        progress = elapsed / duration
        current_health = int(start_health + (end_health - start_health) * progress)
        target_pokemon.current_health = max(0, min(current_health, target_pokemon.max_health))
        battle_scene.draw(screen, player_pokemon, ai_pokemon, moves)
        pygame.display.flip()
        pygame.time.delay(16)

# Main game loop
def main():
    player_team, ai_team = team_draft(available_pokemon)
    pygame.mixer.music.play(-1)
    transition_screen()
    
    result = battle(screen, player_team, ai_team)

    pygame.mixer.music.stop()
    end_game_screen(result)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
# enemies.py
import random
from colorama import Fore, Style
from spells import spell_lookup
from colorama import Fore
from ui_utils import render_bar

class Enemy:
    def __init__(self, name, hp, mp, speed, attack_power, magic_power,
                 defense=0, resistance=0, spells=None, description=""):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp
        self.speed = speed
        self.attack_power = attack_power
        self.magic_power = magic_power
        self.defense = defense
        self.resistance = resistance
        self.spells = spells or []
        self.description = description
        # Mental and physical status effects
        self.is_confused = False
        self.is_feared = False
        self.is_insane = False
        self.is_mindfired = False
        self.is_bleeding = False
        self.is_stunned = False
        self.mindfire_turns = 0
        self.bleeding_turns = 0
        self.mental_resistance_turns = 0
        self.confusion_turns = 0
        self.fear_turns = 0
        self.madness_turns = 0

    def is_alive(self):
        return self.hp > 0

    def display_bars(self):
        hp_bar = render_bar("HP", self.hp, self.max_hp, Fore.RED, bar_width=25)
        print(f"{self.name:<15} {hp_bar}")
        print()  # Adds vertical spacing between enemies

    def choose_action(self):
        if self.hp < (0.4 * self.max_hp):
            healing_spells = [s for s in self.spells if s.category == "heal" and s.cost <= self.mp]
            if healing_spells:
                return "spell", random.choice(healing_spells)

        affordable_spells = [s for s in self.spells if s.cost <= self.mp]
        if affordable_spells and random.random() < 0.6:
            return "spell", random.choice(affordable_spells)

        # Use melee spell as fallback (no longer "attack")
        melee_spells = [s for s in self.spells if s.category == "melee"]
        if melee_spells:
            return "spell", random.choice(melee_spells)

        # Absolute fallback (some 0-cost magic spell, or default behavior)
        zero_cost_spells = [s for s in self.spells if s.cost == 0]
        if zero_cost_spells:
            return "spell", random.choice(zero_cost_spells)

        return "skip", None  # nothing usable


    def take_physical_damage(self, amount):
        reduced = max(0, amount - self.defense)
        self.hp = max(0, self.hp - reduced)
        return reduced

    def take_magical_damage(self, amount):
        reduced = max(0, amount - self.resistance)
        self.hp = max(0, self.hp - reduced)
        return reduced

    def cast_spell(self, spell, target):
        self.mp -= spell.cost
        base_dmg = random.randint(*spell.damage_range)
        total_dmg = base_dmg + self.magic_power
        reduced_dmg = max(0, total_dmg - target.resistance)
        target.hp = max(0, target.hp - reduced_dmg)
        return reduced_dmg

# ------------------------------------
# 🎭 Enemy List
# ------------------------------------

lesser_spawn = Enemy(
    name="Lesser Spawn", hp=60, mp=20, speed=25, # MP Currently unused; reserved for future spell expansion
    attack_power=12, magic_power=8, defense=2, resistance=3,
    spells=[spell_lookup["Claw"], spell_lookup["Unsettling Gaze"], spell_lookup["Sanguine Pounce"]],
    description="A twisted horror, vaguely humanoid, dripping with ichor."
)

shoggoth = Enemy(
    name="Shoggoth", hp=90, mp=50, speed=15, 
    attack_power=16, magic_power=18, defense=6, resistance=10,
    spells=[spell_lookup["Void Bolt"], spell_lookup["Engulf"], spell_lookup["Mutilate"], spell_lookup["Unsettling Gaze"], spell_lookup["Cosmic Vampirism"]],
    description="A roiling mass of eyes and mouths, oozing through the cracks of the dungeon."
)

moon_beast = Enemy(
    name="Moon-Beast", hp=120, mp=55, speed=20,
    attack_power=20, magic_power=20, defense=5, resistance=8,
    spells=[spell_lookup["Void Bolt"], spell_lookup["Eldritch Flame"], spell_lookup["Bite"], spell_lookup["Tear"], spell_lookup["Snap"]],
    description="A bloated monstrosity that shambles forward, guided by unseen forces."
)

clay_golem = Enemy(
    name="Clay Golem", hp=100, mp=0, speed=10,
    attack_power=25, magic_power=0, defense=12, resistance=3,
    spells=[spell_lookup["Pummel"], spell_lookup["Smash"], spell_lookup["Stomp"]],
    description="A hulking mass of hardened clay, cracks running deep in its body."
)

hunting_horror = Enemy(
    name="Hunting Horror", hp=80, mp=30, speed=30,
    attack_power=18, magic_power=10, defense=4, resistance=5,
    spells=[spell_lookup["Void Bolt"], spell_lookup["Tentacle Swipe"], spell_lookup["Hypnotic Gaze"]],
    description="A long, sinewy creature that slithers silently through shadowed halls."
)

flying_polyp = Enemy(
    name="Flying Polyp", hp=75, mp=65, speed=35,
    attack_power=14, magic_power=22, defense=2, resistance=12,
    spells=[spell_lookup["Bite"], spell_lookup["Void Bolt"], spell_lookup["Fireball"], spell_lookup["Cosmic Wind"], spell_lookup["Unnerving Aura"], spell_lookup["Foul Affliction"], spell_lookup["Horrific Wail"]],
    description="A formless terror that whips the air with invisible appendages."
)

dimensional_shambler = Enemy(
    name="Dimensional Shambler", hp=95, mp=30, speed=28,
    attack_power=22, magic_power=15, defense=5, resistance=6,
    spells=[spell_lookup["Void Bolt"], spell_lookup["Strangle"], spell_lookup["Eviscerate"], spell_lookup["Unsettling Gaze"]],
    description="An aberrant being phasing in and out of existence."
)

# ------------------------------------
# 👑 Final Boss
# ------------------------------------

boss_enemy = Enemy(
    name="Avatar of Nyarlathotep", hp=450, mp=150, speed=40,
    attack_power=30, magic_power=35, defense=10, resistance=15,
    spells=[
        spell_lookup["Abyssal Grasp"],
        spell_lookup["Void Bolt"],
        spell_lookup["Fireball"],
        spell_lookup["Eldritch Flame"],
        spell_lookup["Arcane Cataclysm"],
        spell_lookup["Cursed Blow"],
        spell_lookup["Gaze of the Abyss"],
        spell_lookup["Hypnotic Gaze"],
        spell_lookup["Dread Aura"],
        spell_lookup["Curse of the Stars"]
    ],
    description=Fore.RED + "The Servant of the Nameless Mist, whispering promises of oblivion..." + Fore.RESET
)

# ------------------------------------
# 🧬 Enemy Templates
# ------------------------------------

enemy_templates = {
    "Lesser Spawn": {
        "name": "Lesser Spawn",
        "hp": 60,
        "mp": 20,
        "speed": 25,
        "attack_power": 12,
        "magic_power": 8,
        "defense": 2,
        "resistance": 3,
        "spells": ["Claw", "Unsettling Gaze", "Sanguine Pounce"],
        "description": "A twisted horror, vaguely humanoid, dripping with ichor."
    },
    "Shoggoth": {
        "name": "Shoggoth",
        "hp": 90,
        "mp": 50,
        "speed": 15,
        "attack_power": 16,
        "magic_power": 18,
        "defense": 6,
        "resistance": 10,
        "spells": ["Void Bolt", "Engulf", "Mutilate", "Unsettling Gaze", "Cosmic Vampirism"],
        "description": "A roiling mass of eyes and mouths, oozing through the cracks of the dungeon."
    },
    "Moon-Beast": {
        "name": "Moon-Beast",
        "hp": 120,
        "mp": 55,
        "speed": 20,
        "attack_power": 20,
        "magic_power": 20,
        "defense": 5,
        "resistance": 8,
        "spells": ["Void Bolt", "Eldritch Flame", "Bite", "Tear", "Snap"],
        "description": "A bloated monstrosity that shambles forward, guided by unseen forces."
    },
    "Clay Golem": {
        "name": "Clay Golem",
        "hp": 100,
        "mp": 0,
        "speed": 10,
        "attack_power": 25,
        "magic_power": 0,
        "defense": 12,
        "resistance": 3,
        "spells": ["Pummel", "Smash", "Stomp"],
        "description": "A hulking mass of hardened clay, cracks running deep in its body."
    },
    "Hunting Horror": {
        "name": "Hunting Horror",
        "hp": 80,
        "mp": 30,
        "speed": 30,
        "attack_power": 18,
        "magic_power": 10,
        "defense": 4,
        "resistance": 5,
        "spells": ["Void Bolt", "Tentacle Swipe", "Hypnotic Gaze"],
        "description": "A long, sinewy creature that slithers silently through shadowed halls."
    },
    "Flying Polyp": {
        "name": "Flying Polyp",
        "hp": 75,
        "mp": 65,
        "speed": 35,
        "attack_power": 14,
        "magic_power": 22,
        "defense": 2,
        "resistance": 12,
        "spells": ["Bite", "Void Bolt", "Fireball", "Cosmic Wind", "Unnerving Aura", "Foul Affliction", "Horrific Wail"],
        "description": "A formless terror that whips the air with invisible appendages."
    },
    "Dimensional Shambler": {
        "name": "Dimensional Shambler",
        "hp": 95,
        "mp": 30,
        "speed": 28,
        "attack_power": 22,
        "magic_power": 15,
        "defense": 5,
        "resistance": 6,
        "spells": ["Void Bolt", "Strangle", "Eviscerate", "Unsettling Gaze"],
        "description": "An aberrant being phasing in and out of existence."
    },
    "Avatar of Nyarlathotep": {
        "name": "Avatar of Nyarlathotep",
        "hp": 450,
        "mp": 150,
        "speed": 40,
        "attack_power": 30,
        "magic_power": 35,
        "defense": 10,
        "resistance": 15,
        "spells": [
            "Abyssal Grasp", "Void Bolt", "Fireball", "Eldritch Flame",
            "Arcane Cataclysm", "Cursed Blow", "Gaze of the Abyss",
            "Hypnotic Gaze", "Dread Aura", "Curse of the Stars"
        ],
        "description": Fore.RED + "The Servant of the Nameless Mist, whispering promises of oblivion..." + Fore.RESET
    }
}

# ------------------------------------
# 🧪 Factory Function to Spawn New Enemy
# ------------------------------------

def spawn_enemy(name):
    data = enemy_templates.get(name)
    if not data:
        print(Fore.RED + f"⚠️  Enemy template '{name}' not found." + Style.RESET_ALL)
        return None

    # Translate spell names to spell objects
    resolved_spells = [spell_lookup[s] for s in data["spells"] if s in spell_lookup]

    return Enemy(
        name=data["name"],
        hp=data["hp"],
        mp=data["mp"],
        speed=data["speed"],
        attack_power=data["attack_power"],
        magic_power=data["magic_power"],
        defense=data["defense"],
        resistance=data["resistance"],
        spells=resolved_spells,
        description=data["description"]
    )

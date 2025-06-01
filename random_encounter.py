# random_encounter.py
import random
from vivid_battle import start_battle
from enemies import spawn_enemy
from colorama import Fore, Style
from rooms import rooms_map
from items import item_lookup, apply_item_effect, teach_spell_to_party

# Calm room flavor text
calm_flavor = [
    "🎵 The silence in this room is unsettling...",
    "💀 You feel watched, but nothing stirs...",
    "🕯️ Shadows dance along the walls — no foe appears.",
    "🌫️ The air is thick, but no danger reveals itself.",
    "🪞 You see your reflection... but something feels off."
]

# Environmental hazards (some affect one, some all)
hazards = [
    {"type": "hp", "value": -3, "text": "A loose stone gives way — someone stumbles and loses 3 HP.", "target": "single"},
    {"type": "hp", "value": -5, "text": "A hidden dart grazes someone's arm. -5 HP.", "target": "single"},
    {"type": "sanity", "value": -2, "text": "Everyone hears faint whispers... Sanity slips by 2.", "target": "all"},
    {"type": "sanity", "value": -4, "text": "A sigil pulses in everyone's mind. -4 Sanity.", "target": "all"},
]

def sanity_warning(unit):
    """Prints sanity warnings based on thresholds."""
    if unit.sanity < 25:
        print(Fore.MAGENTA + f"😱 {unit.name} is on the edge of madness, whispering to unseen horrors..." + Style.RESET_ALL)
    elif unit.sanity < 50:
        print(Fore.MAGENTA + f"🌀 {unit.name}'s hands shake as visions cloud their eyes..." + Style.RESET_ALL)
    elif unit.sanity < 75:
        print(Fore.MAGENTA + f"😧 {unit.name} breathes heavily, shadows swirling in the corners of their vision." + Style.RESET_ALL)

def random_encounter(players, current_room, shared_inventory, enemies=None, overlay=None):
    """Trigger a random encounter or hazard when entering a room."""
    room = rooms_map[current_room]

    # Check room for item pickup
    contents = room.contents if isinstance(room.contents, list) else [room.contents]
    for item_name in contents:
        if item_name == "none":
            continue

        # 🎲 Randomize actual potion tier if 'Health Potion' or 'Mana Potion'
        if item_name in ["Health Potion", "Mana Potion"]:
            tier_weights = {
                "Health Potion": (["Minor", "Standard", "Major"], [0.4, 0.4, 0.2]),
                "Mana Potion": (["Standard", "Greater"], [0.7, 0.3])
            }
            tiers, weights = tier_weights[item_name]
            selected_tier = random.choices(tiers, weights=weights, k=1)[0]
            item_name = f"{selected_tier} {item_name}"
            room.contents = [item_name]  # Make room remember the real item name

        # look up the actual item after name changes
        item = item_lookup.get(item_name)

        if not item:
            print(Fore.RED + f"⚠️ Could not find item: {item_name}" + Style.RESET_ALL)
            continue


        if item.found is False:
            print(Fore.LIGHTYELLOW_EX + f"\n✨ You found: {item.name}!" + Style.RESET_ALL)
            print(f"{item.description}")
            if item.pickup_text:
                print(item.pickup_text)

            if item.item_type == "scroll":
                teach_spell_to_party(players, item)
            else:
                for player in players:
                    apply_item_effect(player, item)
                shared_inventory.append({"item": item, "qty": 1})

            if hasattr(item, "found"):
                item.found = True
        elif item.found is not None:
            print(Fore.LIGHTBLACK_EX + f"You already collected the {item.name} here." + Style.RESET_ALL)

    # Treasure room bonus cache
    if getattr(room, "is_treasure_room", False):
        bonus_candidates = [i for i in item_lookup.values() if not i.unique and i.item_type in ("healing", "mana", "attack")]
        random.shuffle(bonus_candidates)
        bonus_pile = bonus_candidates[:random.randint(2, 3)]
        print(Fore.LIGHTYELLOW_EX + "\n💰 You stumble upon a hidden cache of supplies!" + Style.RESET_ALL)
        for item in bonus_pile:
            print(Fore.YELLOW + f" - {item.name}" + Style.RESET_ALL)
            shared_inventory.append({"item": item, "qty": 1})

    # Calm room effects
    if room.enemy == "none":
        print(Fore.LIGHTBLACK_EX + "\n" + random.choice(calm_flavor) + Style.RESET_ALL)

        # 35% chance of bonus loot
        if random.random() < 0.35:
            bonus_candidates = [i for i in item_lookup.values() if not i.unique and i.item_type in ("healing", "mana")]
            if bonus_candidates:
                bonus_item = random.choice(bonus_candidates)
                print(Fore.YELLOW + f"\n🎁 You also find a bonus item: {bonus_item.name}!" + Style.RESET_ALL)
                shared_inventory.append({"item": bonus_item, "qty": 1})

        # 30% chance of hazard
        if random.random() < 0.3:
            hazard = random.choice(hazards)
            print(Fore.YELLOW + f"⚠️  {hazard['text']}" + Style.RESET_ALL)

            living_players = [p for p in players if p.is_alive()]
            if not living_players:
                return

            if hazard["target"] == "all":
                for p in living_players:
                    if hazard["type"] == "hp":
                        p.hp = max(1, p.hp + hazard["value"])
                    elif hazard["type"] == "sanity":
                        p.sanity = max(0, p.sanity + hazard["value"])
                        sanity_warning(p)
                    print(f"🧠 {p.name} is affected.")
            else:
                target = random.choice(living_players)
                if hazard["type"] == "hp":
                    target.hp = max(1, target.hp + hazard["value"])
                elif hazard["type"] == "sanity":
                    target.sanity = max(0, target.sanity + hazard["value"])
                    sanity_warning(target)
                print(f"🧍 {target.name} is affected.")

            # Combat encounter (65% chance if enemy not yet defeated)
    elif not room.enemy_defeated and random.random() <= 0.65:
        print(Fore.MAGENTA + "\n⚔️  You sense danger lurking in the shadows..." + Style.RESET_ALL)
        enemy = spawn_enemy(room.enemy)
        if enemy:
            input(Fore.RED + "⚠️  A hostile force draws near... Press [Enter] to prepare for battle!" + Style.RESET_ALL)
            if enemies is not None and enemy:
                enemies.clear()
                enemies.append(enemy)
            result = start_battle(players, enemies, shared_inventory, overlay)
            room.enemy_defeated = True

            if result == "win":
                return "win"
            elif result == "lose":
                return "lose"

        else:
            print(Fore.RED + f"⚠️  No enemy data found for '{room.enemy}' (check rooms.py or enemies.py)." + Style.RESET_ALL)
            return "none"

    # Post-clear random enemy (farming mode)
    elif room.enemy_defeated and not getattr(room, "just_fought", False) and random.random() < 0.25:
        print(Fore.MAGENTA + "\n💀 A new horror emerges from the shadows..." + Style.RESET_ALL)
        random_enemy_name = random.choice(list(spawn_enemy.keys()))
        random_enemy = spawn_enemy(random_enemy_name)
        if enemies is not None:
            enemies.clear()
            enemies.append(random_enemy)

        result = start_battle(players, enemies, shared_inventory, overlay)
        room.just_fought = True  # Prevent chaining battles
        if result == "win":
            return "win"
        elif result == "lose":
            return "lose"

    return "none"  # No battle occurred

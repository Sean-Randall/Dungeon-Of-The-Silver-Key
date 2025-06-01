# dungeon_traverse.py

from colorama import Fore, Style
from vivid_battle import start_battle
from random_encounter import random_encounter
from rooms import rooms_map
from items import item_lookup
from enemies import boss_enemy
from ui_utils import post_loot_menu, cycle_party_inspect
from items import apply_item_effect, teach_spell_to_party
from rooms import spawn_treasure_room
from status_effects import handle_status_effects
visited_room_ids = set()
battles_won = 0

# Room connection logic
room_connections = {
    1: {'s': 2, 'e': 6},
    2: {'n': 1, 's': 3, 'e': 7},
    3: {'n': 2, 's': 4, 'e': 8},
    4: {'n': 3, 's': 5, 'e': 9},
    5: {'n': 4, 'e': 10},
    6: {'s': 7, 'e': 11, 'w': 1},
    7: {'n': 6, 's': 8, 'e': 12, 'w': 2},
    8: {'n': 7, 's': 9, 'e': 13, 'w': 3},
    9: {'n': 8, 's': 10, 'e': 14, 'w': 4},
    10: {'n': 9, 'e': 15, 'w': 5},
    11: {'s': 12, 'e': 16, 'w': 6},
    12: {'n': 11, 's': 13, 'e': 17, 'w': 7},
    13: {'n': 12, 's': 14, 'e': 18, 'w': 8},
    14: {'n': 13, 's': 15, 'e': 19, 'w': 9},
    15: {'n': 14, 'e': 20, 'w': 10},
    16: {'s': 17, 'e': 21, 'w': 11},
    17: {'n': 16, 's': 18, 'e': 22, 'w': 12},
    18: {'n': 17, 's': 19, 'e': 23, 'w': 13},
    19: {'n': 18, 's': 20, 'e': 24, 'w': 14},
    20: {'n': 19, 'e': 25, 'w': 15},
    21: {'s': 22, 'w': 16},
    22: {'n': 21, 's': 23, 'w': 17},
    23: {'n': 22, 's': 24, 'w': 18},
    24: {'n': 23, 's': 25, 'w': 19},
    25: {'n': 24, 'w': 20},
    26: {},  # Final boss room - no exits
}

# Cleared rooms (no repeat loot or battles)
cleared_rooms = set()
boss_defeated = False

def traverse_dungeon(players, shared_inventory, overlay=None, enemies=None):
    """Main dungeon crawl loop."""
    global battles_won
    current_room = 13  # Start at Room 13

    while True:
        room = rooms_map[current_room]
        print(Fore.CYAN + f"\n🧭 You are now in Room {room.RoomNumber}!")
        print(Fore.WHITE + room.RoomDescription)

        # 🎒 Item Pickup Logic
        if current_room not in cleared_rooms and room.contents:
            print(Fore.YELLOW + f"\n✨ You spot an item: {', '.join(room.contents)}!")
            pickup = input(Fore.LIGHTWHITE_EX + "Pick up the item? (Y/N): ").strip().lower()

            if pickup == "y":
                for item_name in room.contents:
                    matching_item = item_lookup.get(item_name.strip())
                    if not matching_item:
                        print(Fore.RED + f"\n⚠️  ERROR: {item_name} not found in item database.")
                        continue

                    existing = next((entry for entry in shared_inventory if entry["item"].name == matching_item.name), None)

                    if matching_item.pickup_text:
                        print(matching_item.pickup_text)

                    was_effective = False
                    if matching_item.item_type == "scroll":
                        was_effective = teach_spell_to_party(players, matching_item)
                        if was_effective:
                            print(Fore.LIGHTBLACK_EX + "The scroll fades after sharing its knowledge." + Style.RESET_ALL)
                    elif matching_item.stat_boost:
                        for player in players:
                            if apply_item_effect(player, matching_item):
                                was_effective = True

                    if existing:
                        existing["qty"] += 1
                        print(Fore.GREEN + f"\nAnother {matching_item.name} added to the party stash! (x{existing['qty']})")
                    else:
                        shared_inventory.append({"item": matching_item, "qty": 1})
                        print(Fore.GREEN + f"\n{matching_item.name} added to the party stash!")

                room.contents = []

        # Show post-loot menu only if the room hasn't been cleared
        if current_room not in cleared_rooms:
            post_loot_menu(players, shared_inventory, current_room)

        # ☠️ Random Encounter Check
        room.just_fought = False
        result = random_encounter(players, current_room, shared_inventory, enemies, overlay)

        if result == "win":
            if current_room != 26:
                print(Fore.CYAN + "\n🛡️ You have a brief moment to heal before moving on.")
                post_loot_menu(players, shared_inventory, current_room)

            battles_won += 1
            if battles_won >= 3:
                treasure_room = spawn_treasure_room(battles_won, visited_room_ids)
                if treasure_room:
                    print(Fore.CYAN + "\n✨ A hidden treasure room has been revealed somewhere in the dungeon!" + Style.RESET_ALL)

        elif result == "lose":
            print(Fore.RED + "\n⚔️ The dungeon consumes your party. Game over.")
            return

        elif result == "none":
            pass  # No battle occurred

                # 🛡️ Final Boss Room
        if current_room == 26 and not boss_defeated:
            print(Fore.RED + Style.BRIGHT + "\n👹 You have entered the final chamber...")
            if enemies is not None:
                enemies.clear()
                enemies.append(boss_enemy)

            result = start_battle(players, enemies, shared_inventory, overlay)

            if result == "lose":
                print(Fore.RED + "\n⚔️ The dungeon consumes your party. Game over.")
                return

            print(Fore.GREEN + "\n🏆 You have conquered the Dungeon of the Silver Key!")
            print(Fore.CYAN + "\nThanks for playing! The shadows retreat... for now.")
            boss_defeated = True
            return  # ⬅ This cleanly exits the game loop

        if current_room != 26:
            cleared_rooms.add(current_room)

        # 🧭 Show Movement Options
        if current_room not in room_connections:
            print(Fore.RED + f"\n⚠️ Room {current_room} has no known exits... The air is still." + Style.RESET_ALL)
            available_moves = []
        else:
            # 🧭 Show Movement Options
            available_moves = []
            if 'n' in room_connections[current_room]: available_moves.append('N')
            if 's' in room_connections[current_room]: available_moves.append('S')
            if 'e' in room_connections[current_room]: available_moves.append('E')
            if 'w' in room_connections[current_room]: available_moves.append('W')

        print(Fore.GREEN + f"\nAvailable exits: {', '.join(available_moves)}")
        print(Fore.LIGHTWHITE_EX + "You may also [P]arty Inspect.\n")

        move = input("Choose a direction or press 'P' to inspect party: ").strip().lower()

        if move == "dev":
            try:
                current_room = int(input("🧪 Enter room number to teleport to: "))
                continue
            except:
                print("❌ Invalid room.")
                continue

        if move == "p":
            cycle_party_inspect(players, shared_inventory)
            continue

        if move in room_connections[current_room]:
            current_room = room_connections[current_room][move]

            # 🔁 Decrement status effects each room move
            for player in players:
                _ = handle_status_effects(player)

            # 🚪 Instant Boss Portal Trigger (on room arrival)
            if current_room == 15 and any(entry["item"].name == "Silver Key" for entry in shared_inventory):
                print(Fore.MAGENTA + "\nThe Silver Key vibrates violently! A portal opens...")
                input(Fore.LIGHTCYAN_EX + "\nPress [Enter] to step into the portal...\n")
                current_room = 26  # Teleport to final boss room
                continue  # Jump to next loop to process Room 26 immediately


        else:
            print(Fore.RED + "\n⚠️ Invalid move. Try again.")
            continue


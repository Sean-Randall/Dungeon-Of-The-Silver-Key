#ui_utils.py
from colorama import Fore, Style
import random
from spells import spell_lookup
from status_effects import try_inflict_status

def render_bar(label, current, maximum, bar_color=Fore.GREEN, bar_width=20):
    if maximum == 0:
        ratio = 0
    else:
        ratio = current / maximum

    filled = "█" * int(ratio * bar_width)
    empty = " " * (bar_width - len(filled))
    bar = f"{bar_color}{label:<10} [{filled}{empty}] {current}/{maximum}{Style.RESET_ALL}"
    return bar

def display_combat_unit(unit, is_enemy=False):
    """Render name, status icons, and HP/MP/SAN bars for a player or enemy."""
    from vivid_battle import get_status_icons  # avoid circular imports

    status = get_status_icons(unit)
    name_display = f"{unit.name} {status}" if status else unit.name
    hp_bar = render_bar("HP", unit.hp, unit.max_hp, Fore.RED if is_enemy else Fore.GREEN, bar_width=25)

    # Show MP bar if applicable
    mp_bar = ""
    if hasattr(unit, "mp"):
        mp_bar = render_bar("MP", unit.mp, unit.max_mp, Fore.BLUE, bar_width=15)

    # Show SAN bar only for players and if flagged
    sanity_bar = ""
    if not is_enemy and getattr(unit, "show_sanity_bar", False):
        sanity_bar = render_bar("SAN", unit.sanity, 100, Fore.MAGENTA, bar_width=15)

    # Final layout
    print(f"{name_display:<25} {hp_bar}   {mp_bar}   {sanity_bar}".strip())
    print()

def sanity_descriptor(sanity):
    if sanity >= 75:
        return "Lucid"
    elif sanity >= 50:
        return "Stressed"
    elif sanity >= 25:
        return "Fraying"
    else:
        return "Unstable"

def hp_descriptor(hp, max_hp):
    ratio = hp / max_hp
    if ratio >= 0.75:
        return "Healthy"
    elif ratio >= 0.5:
        return "Wounded"
    elif ratio >= 0.25:
        return "Critical"
    else:
        return "Near Death"

def mp_descriptor(mp, max_mp):
    ratio = mp / max_mp
    if ratio >= 0.75:
        return "Focused"
    elif ratio >= 0.5:
        return "Drained"
    elif ratio >= 0.25:
        return "Flickering"
    else:
        return "Empty"

def is_mentally_stable(unit):
    return (
        not getattr(unit, 'is_confused', False) and
        not getattr(unit, 'is_feared', False) and
        not getattr(unit, 'is_insane', False) and
        not getattr(unit, 'is_mindfired', False) and
        getattr(unit, 'sanity', 100) >= 75
    )

def cast_healing_spell(spell, caster, target):
    healing_amount = spell.power
    target.hp = min(target.max_hp, target.hp + healing_amount)
    print(Fore.GREEN + f"{caster.name} casts {spell.name} on {target.name}, restoring {healing_amount} HP!" + Style.RESET_ALL)

def cast_defensive_spell(spell, caster):
    if spell.name == "Sentinel's Oath":
        heal_amount = spell.power
        caster.hp = min(caster.max_hp, caster.hp + heal_amount)
        caster.sent_oath_active = True

        print(Fore.GREEN + f"{caster.name} regains {heal_amount} HP while swearing a Sentinel’s Oath!" + Style.RESET_ALL)
        print(Fore.CYAN + f"{caster.name} is now ready to intercept a fatal blow to an ally." + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f"{spell.name} is a defensive spell, but has no defined effect yet." + Style.RESET_ALL)

def choose_healing_target(players):
    injured = [p for p in players if p.hp < p.max_hp and p.hp > 0]
    if not injured:
        print(Fore.YELLOW + "⚠️ No injured allies to heal." + Style.RESET_ALL)
        return None
    if len(injured) == 1:
        return injured[0]

    print(Fore.LIGHTWHITE_EX + "\nChoose someone to heal:" + Style.RESET_ALL)
    for i, p in enumerate(injured, 1):
        print(f"  {i}. {p.name} ({p.hp}/{p.max_hp} HP)")
    choice = input("> ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(injured):
            return injured[idx]
    print(Fore.YELLOW + "⚠️ Invalid selection." + Style.RESET_ALL)
    return None

def post_loot_menu(players, shared_inventory, current_room):

    while True:
        print("\n[i]nspect inventory, [u]se item, [h]eal with magic, [v]iew map, or [c]ontinue?")
        action = input("> ").strip().lower()

        if action == "i":
            print(Fore.YELLOW + "\n📦 Party Inventory:" + Style.RESET_ALL)
            if not shared_inventory:
                print(Fore.LIGHTBLACK_EX + "👜 Inventory is empty." + Style.RESET_ALL)
            else:
                for idx, entry in enumerate(shared_inventory, 1):
                    print(f"  {idx}. {entry['item'].name} x{entry['qty']} – {entry['item'].description}")

        elif action == "u":
            if not shared_inventory:
                print("The party has no items.")
                continue

            if len(players) == 1:
                user = players[0]
            else:
                print("\nChoose a character to use an item:")
                for i, player in enumerate(players, 1):
                    print(f"  {i}. {player.name}")
                try:
                    choice = int(input("> "))
                    if 1 <= choice <= len(players):
                        user = players[choice - 1]
                    else:
                        print("Invalid choice.")
                        continue
                except ValueError:
                    print("Please enter a number.")
                    continue

            print("\n🎒 Choose an item:")
            for i, entry in enumerate(shared_inventory, 1):
                item = entry["item"]
                qty = entry["qty"]
                print(f"  {i}. {item.name} x{qty} – {item.description}")
            print("  0. Cancel")

            try:
                item_choice = int(input("Select item number: "))
                if item_choice == 0:
                    continue
                selected_entry = shared_inventory[item_choice - 1]
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

            item = selected_entry["item"]
            item_used = False

            if item.item_type == "healing":
                target = choose_healing_target(players)
                if not target:
                    continue
                heal_amount = random.randint(*item.heal_range)
                target.hp = min(target.max_hp, target.hp + heal_amount)
                print(Fore.GREEN + f"{target.name} uses {item.name} and heals for {heal_amount} HP." + Style.RESET_ALL)
                item_used = True


            elif item.item_type == "mana":
                if user.mp >= user.max_mp:
                    print(Fore.YELLOW + f"{user.name} already has full MP. The {item.name} is not used." + Style.RESET_ALL)
                else:
                    if item.mana_restore is None:
                        print(Fore.YELLOW + f"⚠️ {item.name} has no defined MP restore value." + Style.RESET_ALL)
                        return

                    mp_restore = random.randint(*item.mana_restore) if isinstance(item.mana_restore, tuple) else item.mana_restore

                    user.mp = min(user.max_mp, user.mp + mp_restore)
                    print(Fore.BLUE + f"{user.name} recovers {mp_restore} MP!" + Style.RESET_ALL)
                    item_used = True

            elif item.teaches_spell:
                spell = spell_lookup.get(item.teaches_spell)
                if not spell:
                    print(Fore.RED + "⚠️ The scroll is blank or corrupted." + Style.RESET_ALL)
                elif spell in user.spells:
                    print(Fore.YELLOW + f"{user.name} already knows {spell.name}. The scroll crumbles unused." + Style.RESET_ALL)
                elif user.job not in spell.allowed_classes:
                    print(Fore.RED + f"{user.name} cannot learn {spell.name}. The scroll rejects your essence." + Style.RESET_ALL)
                else:
                    confirm = input(f"This will teach {spell.name}. Use it? (Y/N): ").lower()
                    if confirm == "y":
                        user.spells.append(spell)
                        print(Fore.MAGENTA + f"{user.name} learned {spell.name}!" + Style.RESET_ALL)
                        item_used = True
                    else:
                        print("Cancelled.")

            if item_used:
                selected_entry["qty"] -= 1
                if selected_entry["qty"] <= 0:
                    shared_inventory.remove(selected_entry)

            if not item_used:
                print(Fore.LIGHTBLACK_EX + "Nothing happened. You still have the item." + Style.RESET_ALL)

        elif action == "h":
            healers = [p for p in players if any(s.category == "heal" and p.mp >= s.cost for s in p.spells)]
            if not healers:
                print(Fore.YELLOW + "⚠️ No one in your party can currently cast healing spells." + Style.RESET_ALL)
                continue

            print("\nAvailable healers:")
            for i, p in enumerate(healers, 1):
                print(f"  {i}. {p.name} (MP: {p.mp}/{p.max_mp})")
            try:
                h_choice = int(input("Choose a healer: ")) - 1
                caster = healers[h_choice]
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

            healing_spells = [s for s in caster.spells if s.category in ("heal", "defense") and caster.mp >= s.cost]
            if not healing_spells:
                print(Fore.YELLOW + f"{caster.name} has no usable healing spells." + Style.RESET_ALL)
                continue

            print("\nAvailable healing spells:")
            for i, s in enumerate(healing_spells, 1):
                print(f"  {i}. {s.name} (MP: {s.cost}) – {s.cast_description()}")
            try:
                s_choice = int(input("Choose a spell: ")) - 1
                spell = healing_spells[s_choice]
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

            target = choose_healing_target(players)
            if not target:
                continue

            caster.mp -= spell.cost
            if spell.category == "heal":
                cast_healing_spell(spell, caster, target)
            elif spell.category == "defense":
                cast_defensive_spell(spell, caster)
            else:
                print(Fore.YELLOW + f"⚠️ {spell.name} has no defined casting behavior in this context." + Style.RESET_ALL)

        elif action == "v":
            render_map(current_room)


        elif action == "c":
            break

        else:
            print("Invalid input.")

def use_item_in_combat(user, allies, enemies, shared_inventory):
    if not shared_inventory:
        print("You have no items.")
        return

    print("\n🎒 Choose an item:")
    for i, entry in enumerate(shared_inventory, 1):
        item = entry["item"]
        qty = entry["qty"]
        print(f"  {i}. {item.name} x{qty} – {item.description}")
    print("  0. Cancel")

    try:
        choice = int(input("> "))
        if choice == 0:
            return
        selected_entry = shared_inventory[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    item = selected_entry["item"]
    item_used = False

    if item.item_type == "healing":
        target = choose_healing_target(allies)
        if not target:
            return
        heal_amount = random.randint(*item.heal_range)
        target.hp = min(target.max_hp, target.hp + heal_amount)

        if target == user:
            print(Fore.GREEN + f"{user.name} drinks the {item.name} and heals for {heal_amount} HP!" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"{user.name} throws a {item.name} to {target.name}, who heals for {heal_amount} HP!" + Style.RESET_ALL)

        item_used = True



    elif item.item_type == "mana":
        if len(allies) > 1:
            print("\nChoose who to restore MP to:")
            for i, ally in enumerate(allies, 1):
                print(f"  {i}. {ally.name} ({ally.mp}/{ally.max_mp} MP)")
            try:
                t_choice = int(input("> "))
                if 1 <= t_choice <= len(allies):
                    target = allies[t_choice - 1]
                else:
                    print("Invalid selection.")
                    return
            except ValueError:
                print("Invalid input.")
                return
        else:
            target = allies[0]

        if target.mp >= target.max_mp:
            print(Fore.YELLOW + f"{target.name} already has full MP. The {item.name} is not used." + Style.RESET_ALL)
            return

        if item.mana_restore is None:
            print(Fore.YELLOW + f"⚠️ {item.name} has no defined MP restore value." + Style.RESET_ALL)
            return

        mp_restore = random.randint(*item.mana_restore) if isinstance(item.mana_restore, tuple) else item.mana_restore

        target.mp = min(target.max_mp, target.mp + mp_restore)

        if target == user:
            print(Fore.BLUE + f"{user.name} drinks the {item.name} and restores {mp_restore} MP!" + Style.RESET_ALL)
        else:
            print(Fore.BLUE + f"{user.name} throws a {item.name} to {target.name}, restoring {mp_restore} MP!" + Style.RESET_ALL)

        item_used = True


    elif item.item_type == "attack":
        print("\nChoose an enemy to throw the item at:")
        for i, enemy in enumerate(enemies, 1):
            print(f"  {i}. {enemy.name} ({enemy.hp}/{enemy.max_hp})")
        try:
            t_choice = int(input("> "))
            if 1 <= t_choice <= len(enemies):
                target = enemies[t_choice - 1]
            else:
                print("Invalid target.")
                return
        except ValueError:
            print("Invalid input.")
            return

        print(f"{user.name} throws {item.name} at {target.name}!")
        damage = random.randint(*item.damage_range)
        target.hp = max(0, target.hp - damage)
        print(Fore.RED + f"{target.name} takes {damage} damage!" + Style.RESET_ALL)

        if item.effect:
            try_inflict_status(target, item.effect)

        if target.hp <= 0:
            print(Fore.GREEN + f"{target.name} has been defeated!" + Style.RESET_ALL)

        item_used = True


    elif item.item_type == "spellbook":
        if item.spell in user.spells:
            print(Fore.YELLOW + f"{user.name} already knows {item.spell.name}. The scroll crumbles unused." + Style.RESET_ALL)
        else:
            print(f"{user.name} quickly reads the {item.name} scroll mid-battle!")
            user.spells.append(item.spell)
            print(Fore.MAGENTA + f"{user.name} learns the spell {item.spell.name}!" + Style.RESET_ALL)
            item_used = True

    if item_used:
        selected_entry["qty"] -= 1
        if selected_entry["qty"] <= 0:
            shared_inventory.remove(selected_entry)

def render_map(player_position=None):
    print(Fore.GREEN + "\n🗺️ You glance at the map..." + Style.RESET_ALL)
    top_border = "╒════╤════╤════╤════╤════╕"
    mid_border = "├────┼────┼────┼────┼────┤"
    bottom_border = "╘════╧════╧════╧════╧════╛"

    print(top_border)
    for row in range(5):  # Rows: top to bottom
        row_cells = []
        for col in range(5):  # Columns: left to right
            room_num = col * 5 + row + 1  # Column-major numbering
            cell = " @  " if player_position == room_num else f"{room_num:2}".rjust(4)
            row_cells.append(cell)
        print("│" + "│".join(row_cells) + "│")
        if row < 4:
            print(mid_border)
    print(bottom_border)
    print(Fore.LIGHTBLACK_EX + "\n@ = Your position\n" + Style.RESET_ALL)

def cycle_party_inspect(players, shared_inventory=None):
    index = 0
    while True:
        player = players[index]
        print("\n" + "="*60)
        player.inspect_character(shared_inventory)
        print("\n" + "="*60)
        print(f"\nViewing {player.name} ({index + 1}/{len(players)})")
        print("Press [N]ext, [P]revious, or [Q]uit.")

        choice = input("> ").strip().lower()
        if choice == "n":
            index = (index + 1) % len(players)
        elif choice == "p":
            index = (index - 1) % len(players)
        elif choice == "q":
            break
        else:
            print("Invalid input. Try [N], [P], or [Q].")


# vivid_battle.py

import random
import time
from colorama import Fore, Style
from ui_utils import use_item_in_combat
from status_effects import apply_mental_affliction, try_inflict_status, handle_status_effects, handle_sanity_effects
from ui_utils import choose_healing_target, display_combat_unit
from spells import get_class_melee_spell

def get_status_icons(unit):
    icons = []

    # 🩸 Bleeding
    if getattr(unit, 'is_bleeding', False):
        turns = getattr(unit, 'bleeding_turns', 0)
        icons.append(f"🩸({turns})" if turns > 0 else "🩸")

    # 🔥 Mindfire
    if getattr(unit, 'is_mindfired', False):
        turns = getattr(unit, 'mindfire_turns', 0)
        icons.append(f"🔥({turns})" if turns > 0 else "🔥")

    # ❓ Confusion
    if getattr(unit, 'is_confused', False):
        turns = getattr(unit, 'confusion_turns', 0)
        icons.append(f"❓({turns})" if turns > 0 else "❓")

    # 😨 Fear
    if getattr(unit, 'is_feared', False):
        turns = getattr(unit, 'fear_turns', 0)
        icons.append(f"😨({turns})" if turns > 0 else "😨")

    # 🧠 Madness
    if getattr(unit, 'is_insane', False):
        turns = getattr(unit, 'madness_turns', 0)
        icons.append(f"🧠({turns})" if turns > 0 else "🧠")

    # 💫 Stunned
    if getattr(unit, 'is_stunned', False):
        turns = getattr(unit, 'stun_turns', 1)
        icons.append(f"💫({turns})" if turns > 0 else "💫")

    # 🔰 Mental Resistance
    if getattr(unit, 'mental_resistance_turns', 0) > 0:
        icons.append(f"🔰({unit.mental_resistance_turns})")

    return " ".join(icons)


def enemy_spell_cast_text(enemy_name, spell_name):
    lore_lines = {
        "Void Bolt": [
            f"{enemy_name} chants in a forgotten tongue and hurls a bolt from the void!",
            f"Space distorts around {enemy_name} as {spell_name} tears toward its prey!",
            f"A whisper from the Outer Dark rides the {spell_name} released by {enemy_name}!"
        ],
        "Eldritch Flame": [
            f"{enemy_name} ignites a flame that screams with the voices of dead stars!",
            f"{spell_name} writhes unnaturally in {enemy_name}'s grasp before lashing out!",
            f"An inferno born of madness erupts as {enemy_name} casts {spell_name}!"
        ],
        "Fireball": [
            f"{enemy_name}'s eyes burn red as a blazing sphere engulfs the air!",
            f"With an inhuman roar, {enemy_name} hurls {spell_name} from a burning sigil!",
            f"The heat of ancient suns answers {enemy_name}'s call through {spell_name}!"
        ],
        "Arcane Cataclysm": [
            f"The veil of reality rends as {enemy_name} unleashes {spell_name}!",
            f"{spell_name} swirls with impossible geometry as {enemy_name} calls upon it!",
            f"The dungeon trembles — {enemy_name} channels the will of Nyarlathotep!"
        ]
    }

    return random.choice(lore_lines.get(spell_name, [f"{enemy_name} casts {spell_name} with unsettling calm..."]))

fizzle_flavor_texts = [
    "⛧ The air twists violently, whispering in tongues no one understands...",
    "☍ An eye blinks open in the void, then vanishes without a trace...",
    "✦ The runes shimmer briefly before crumbling into black ash...",
    "☉ {name} hears laughter — it echoes from somewhere beneath the floor.",
    "⟁ The veil wavers. Something watches — but chooses not to act.",
    "✣ A stifling silence falls, as if the dungeon holds its breath.",
    "☌ A chorus of unseen voices hums dissonantly around {name}...",
    "⯎ The sigils sputter and flare, then collapse into themselves."
]

def all_enemies_defeated(enemies):
    return all(e.hp <= 0 for e in enemies)

def handle_spell_miscast(caster, spell, players, enemies):
    outcome = random.choice(["self_hit", "random_target", "mental_backlash"])

    if spell.category == "heal":
        # Twisted healing: partial heal, partial enemy benefit, and backlash
        heal_amount = random.randint(*spell.damage_range) + caster.magic_power
        heal_ally = int(heal_amount * 0.6)
        enemy_heal = int(heal_amount * 0.4)
        backlash = random.randint(3, 10)

        caster.hp = max(0, caster.hp - backlash)
        caster.hp = min(caster.max_hp, caster.hp + heal_ally)

        print(Fore.YELLOW + f"{caster.name} miscasts {spell.name} — distorted energies ripple outward!" + Style.RESET_ALL)
        print(Fore.GREEN + f"{caster.name} heals for {heal_ally} HP..." + Style.RESET_ALL)

        # Pick a random living enemy to receive the healing spill
        living_enemies = [e for e in enemies if e.hp > 0]
        if living_enemies:
            target_enemy = random.choice(living_enemies)
            target_enemy.hp = min(target_enemy.max_hp, target_enemy.hp + enemy_heal)
            print(Fore.LIGHTRED_EX + f"💢 The remaining {enemy_heal} healing energy is absorbed by {target_enemy.name}!" + Style.RESET_ALL)

        print(Fore.RED + f"{caster.name} suffers {backlash} backlash damage!" + Style.RESET_ALL)

    else:
        if outcome == "self_hit":
            dmg = random.randint(5, 15)
            caster.hp = max(0, caster.hp - dmg)
            print(Fore.RED + f"{caster.name}'s {spell.name} explodes in their hands, dealing {dmg} self-inflicted damage!" + Style.RESET_ALL)

        elif outcome == "random_target":
            possible_targets = [c for c in players + enemies if c.hp > 0]
            if possible_targets:
                target = random.choice(possible_targets)
                dmg = random.randint(*spell.damage_range) + caster.magic_power
                actual_dmg = max(0, dmg - target.resistance)
                target.hp = max(0, target.hp - actual_dmg)
                print(Fore.YELLOW + f"{caster.name}'s {spell.name} wildly fires at {target.name}, dealing {actual_dmg} damage!" + Style.RESET_ALL)

                if spell.effect:
                    effects = spell.effect if isinstance(spell.effect, list) else [spell.effect]
                    for effect in effects:
                        try_inflict_status(target, effect, spell_name=spell.name)

        elif outcome == "mental_backlash":
            affliction = random.choice(["confusion", "fear", "madness"])
            apply_mental_affliction(caster, affliction)
            print(Fore.LIGHTMAGENTA_EX + f"The miscast {spell.name} echoes back into {caster.name}'s mind, inducing {affliction}!" + Style.RESET_ALL)

def cast_pure_of_mind(caster, target):
    target.is_confused = False
    target.is_feared = False
    target.is_insane = False
    target.mental_resistance_turns = 3
    print(Fore.CYAN + f"{caster.name} casts Pure of Mind!" + Style.RESET_ALL)
    print(Fore.LIGHTWHITE_EX + f"A calming glow surrounds {target.name}, clearing their mind and bolstering it against future corruption." + Style.RESET_ALL)

def cast_veil_of_silence(caster, target):
    target.mental_resistance_turns = 2  # Lasts 2 turns
    print(Fore.CYAN + f"{caster.name} invokes the Veil of Silence!" + Style.RESET_ALL)
    print(Fore.LIGHTWHITE_EX + f"An intangible silence shields {target.name}'s mind from intrusion." + Style.RESET_ALL)

def apply_aoe_spell(spell, caster, targets, is_enemy_cast=False):
    for target in targets:
        if target.hp <= 0:
            continue

        # Determine if target is defending
        defending = getattr(target, "defending", False)

        # Damage type and calculation
        raw_dmg = random.randint(*spell.damage_range)
        if spell.category == "melee":
            total_dmg = raw_dmg + caster.attack_power
            actual_dmg = max(0, total_dmg - target.defense)
            dmg_type = "physical"
        else:
            total_dmg = raw_dmg + caster.magic_power
            actual_dmg = max(0, total_dmg - target.resistance)
            dmg_type = "magical"

        if defending:
            actual_dmg = int(actual_dmg * 0.5)
            print(Fore.CYAN + f"{target.name} defends and takes reduced {dmg_type} damage!" + Style.RESET_ALL)

        apply_spell_damage_and_effect(spell, caster, target, dmg_type, actual_dmg)

        time.sleep(0.4)

def apply_spell_damage_and_effect(spell, caster, target, dmg_type, actual_dmg):
    target.hp = max(0, target.hp - actual_dmg)
    color = Fore.RED if dmg_type == "physical" else Fore.MAGENTA
    print(color + f"{target.name} takes {actual_dmg} {dmg_type} damage from {spell.name} cast by {caster.name}!" + Style.RESET_ALL)

    # 🧛 Drain for Cosmic Vampirism
    if spell.name == "Cosmic Vampirism" and actual_dmg > 0:
        drain = actual_dmg // 2
        caster.hp = min(caster.max_hp, caster.hp + drain)
        print(Fore.MAGENTA + f"{caster.name} drains {drain} HP from {target.name}!" + Style.RESET_ALL)

    # Always treat spell.effect as list
    if spell.effect:
        effects = spell.effect if isinstance(spell.effect, list) else [spell.effect]
        for effect in effects:
            try_inflict_status(target, effect, spell_name=spell.name)

def start_battle(players, enemies, shared_inventory, overlay=None):
    print(Fore.RED + Style.BRIGHT + "\n⚔️  The battle begins!\n" + Style.RESET_ALL)

    if overlay:
        overlay.party_ref = players
        overlay.enemies_ref = enemies
        try:
            overlay.update_display()
        except Exception as e:
            print(f"(Overlay display error: {e})")

    all_combatants = players + enemies
    all_combatants.sort(key=lambda x: x.speed, reverse=True)

    class_icons = {
        "White Mage": "✨",
        "Black Mage": "🧙",
        "Tank": "🛡️",
        "Occultist": "🔮"
    }

    guarding_tank = None
    sentinel_instinct_used = False
    protected_ally = None  # Holds the player the Tank is watching over
    sentinel_successful = False

    while True:
        if sentinel_instinct_used and sentinel_successful:
                sentinel_instinct_used = False  # 🔁 Reset passive each round if successfully used
                protected_ally = None

        
        print(Fore.LIGHTWHITE_EX + "\n👥 Party Status:" + Style.RESET_ALL)
        for player in players:
            if player.hp > 0:
                display_combat_unit(player)

        print(Fore.LIGHTWHITE_EX + "\n👹 Enemy Status:" + Style.RESET_ALL)
        for enemy in enemies:
            if enemy.hp > 0:
                display_combat_unit(enemy, is_enemy=True)

        time.sleep(1.5)

        for unit in all_combatants:
            if unit.hp <= 0:
                continue

            if unit in players:
                while True:
                    for player in players:
                        player.defending = False # Reset for previously defending
                    icon = class_icons.get(unit.job, "🎭")
                    print(Fore.CYAN + f"\n{icon}  {unit.name}'s Turn {icon}" + Style.RESET_ALL)
                    status_result = handle_status_effects(unit)
                    if status_result == "skip":
                        continue
                    elif status_result == "chaos":
                        random_action = random.choice(["attack_ally", "defend", "scream"])
                        if random_action == "attack_ally":
                            ally = random.choice([p for p in players if p.hp > 0 and p != unit])
                            if ally:
                                base_dmg = unit.attack_power + random.randint(2, 8)
                                actual_dmg = max(0, base_dmg - ally.defense)
                                if getattr(ally, "defending", False):
                                    actual_dmg = int(actual_dmg * 0.5)
                                    print(Fore.CYAN + f"{ally.name} defends instinctively against the blow!" + Style.RESET_ALL)
                                ally.hp = max(0, ally.hp - actual_dmg)
                                print(Fore.RED + f"{unit.name} attacks {ally.name} in a fit of madness for {actual_dmg} damage!" + Style.RESET_ALL)
                        elif random_action == "defend":
                            unit.defending = True  # You can check for this elsewhere to reduce damage taken this round
                            print(Fore.LIGHTYELLOW_EX + f"{unit.name} curls into a ball defensively, whispering to unseen forces..." + Style.RESET_ALL)
                        elif random_action == "scream":
                            print(Fore.LIGHTMAGENTA_EX + f"{unit.name} screams at the darkness, hands clutching their skull — doing nothing useful!" + Style.RESET_ALL)

                    if unit.sanity < 25:
                        print(Fore.MAGENTA + f"😱 {unit.name} is on the edge of madness, whispering to unseen horrors..." + Style.RESET_ALL)
                    elif unit.sanity < 50:
                        print(Fore.MAGENTA + f"🌀 {unit.name}'s hands shake as visions cloud their eyes..." + Style.RESET_ALL)
                    elif unit.sanity < 75:
                        print(Fore.MAGENTA + f"😧 {unit.name} breathes heavily, shadows swirling in the corners of their vision." + Style.RESET_ALL)

                    available_actions = ["Attack", "Cast Spell", "Use Item", "Inspect", "Defend"]

                    for idx, action in enumerate(available_actions, 1):
                        print(f"  {idx}. {action}")

                    choice = input(Fore.LIGHTWHITE_EX + "> " + Style.RESET_ALL).strip()

                    if choice == "1":
                        melee_spell = get_class_melee_spell(unit.job)
                        target = choose_target(enemies)
                        if target:
                            base_dmg = random.randint(*melee_spell.damage_range)
                            total_dmg = base_dmg + unit.attack_power
                            actual_dmg = max(0, total_dmg - target.defense)
                            target.hp = max(0, target.hp - actual_dmg)

                            print(Fore.CYAN + melee_spell.cast_description() + Style.RESET_ALL)

                            if actual_dmg == 0:
                                print(random.choice([
                                    f"{unit.name}'s strike glances off {target.name}, dealing no damage.",
                                    f"{target.name} shrugs off the attack — unscathed.",
                                    f"{unit.name} fails to penetrate {target.name}'s defense."
                                ]))
                            elif actual_dmg <= 3:
                                print(f"A light hit — {unit.name} deals just {actual_dmg} damage.")
                            else:
                                print(Fore.GREEN + f"\n🗡️ {unit.name} hits {target.name} for {actual_dmg} damage!" + Style.RESET_ALL)

                            if target.hp == 1:
                                print(Fore.YELLOW + f"{target.name} clings to life with a sliver of strength!" + Style.RESET_ALL)

                            time.sleep(1.2)
                            if all_enemies_defeated(enemies):
                                print(Fore.GREEN + Style.BRIGHT + "\n🎉 Victory! The enemies have been defeated!" + Style.RESET_ALL)
                                return "win"
                        break

                    elif choice == "2":
                        spell = unit.choose_spell()
                        if not spell:
                            continue

                        if spell.cost > unit.mp:
                            print(Fore.RED + "⚠️ Not enough MP!" + Style.RESET_ALL)
                            continue

                        # Sanity effects happen now, after the player *chooses* to cast a spell
                        sanity_check = handle_sanity_effects(unit)
                        if sanity_check == "miscast":
                            # Miscast: spell backfires or hits wrong target
                            print(Fore.YELLOW + f"{unit.name}'s concentration wavers — the spell misfires!" + Style.RESET_ALL)
                            handle_spell_miscast(unit, spell, players, enemies)
                            continue

                        elif sanity_check == "fizzle":
                            print(Fore.YELLOW + f"{unit.name} loses focus — the spell fizzles before it forms!" + Style.RESET_ALL)

                            # 🎭 Add eerie flavor text
                            fizzle_line = random.choice(fizzle_flavor_texts)
                            if "{name}" in fizzle_line:
                                fizzle_line = fizzle_line.format(name=unit.name)
                            print(Fore.LIGHTBLACK_EX + fizzle_line + Style.RESET_ALL)

                            # Fizzle recovery phase: only allow Inspect or Defend
                            while True:
                                print(Fore.LIGHTWHITE_EX + f"\n🔄 {unit.name} may still inspect or defend:" + Style.RESET_ALL)
                                print("  1. Inspect Self")
                                print("  2. Defend")
                                fizzle_choice = input(Fore.LIGHTWHITE_EX + "> " + Style.RESET_ALL).strip()

                                if fizzle_choice == "1":
                                    print(Fore.LIGHTCYAN_EX + f"\n📖 Inspecting {unit.name} the {unit.job}..." + Style.RESET_ALL)
                                    unit.inspect_character()
                                    input(Fore.YELLOW + "\nPress Enter to return to battle..." + Style.RESET_ALL)
                                    continue

                                elif fizzle_choice == "2":
                                    unit.defending = True
                                    print(Fore.LIGHTYELLOW_EX + f"{unit.name} steadies their stance after the failed casting attempt." + Style.RESET_ALL)
                                    time.sleep(1.2)
                                    break

                                else:
                                    print(Fore.YELLOW + "Invalid choice. Choose 1 or 2." + Style.RESET_ALL)
                            break  # Ends the player's turn after fallback

                        if spell.name == "Guardian Shield":
                            unit.is_guarding = True
                            print(Fore.YELLOW + f"\n🛡️ {unit.name} activates Guardian Shield, ready to protect allies!" + Style.RESET_ALL)
                            print(Fore.YELLOW + f"\n🛡️ {unit.name} braces to intercept incoming attacks!" + Style.RESET_ALL)
                            time.sleep(1.2)
                            break

                        elif spell.name == "Sentinel's Oath":
                            # Choose target to heal and protect
                            valid_targets = [a for a in players if a.hp > 0 and a != unit]
                            if not valid_targets:
                                print(Fore.YELLOW + f"No valid allies to protect with {spell.name}." + Style.RESET_ALL)
                                break

                            print("\nWho will you heal and protect?")
                            for i, ally in enumerate(valid_targets, 1):
                                print(f"  {i}. {ally.name} ({ally.hp}/{ally.max_hp} HP)")
                            try:
                                choice = int(input("> ")) - 1
                                target = valid_targets[choice]
                            except (ValueError, IndexError):
                                print(Fore.YELLOW + "Invalid choice." + Style.RESET_ALL)
                                break

                            heal_amount = random.randint(*spell.damage_range)
                            target.hp = min(target.max_hp, target.hp + heal_amount)
                            target.is_guarded = True         # Mark this ally to be intercepted
                            guarding_tank = unit             # The one who casted the spell

                            print(Fore.GREEN + f"\n✨ {unit.name} casts {spell.name}, healing {target.name} for {heal_amount} HP!" + Style.RESET_ALL)
                            print(Fore.LIGHTCYAN_EX + f"🛡️ {unit.name} prepares to intercept any attack against {target.name}!" + Style.RESET_ALL)
                            time.sleep(1.2)
                            break
                        
                        elif spell.name == "Pure of Mind":
                            target = unit  # Self-targeting
                            cast_pure_of_mind(unit, target)
                            break

                        elif spell.name == "Veil of Silence":
                            cast_veil_of_silence(unit, unit)  # Self-targeting
                            time.sleep(1.2)
                            break

                        # Healing spells with targeting
                        elif spell.category == "heal":
                            target = choose_healing_target(players)
                            if not target:
                                print(Fore.YELLOW + "Spell cancelled." + Style.RESET_ALL)
                                unit.mp += spell.cost  # Refund MP if cancelled
                                break
                            heal = random.randint(*spell.damage_range) + unit.magic_power
                            target.hp = min(target.max_hp, target.hp + heal)
                            print(Fore.GREEN + f"\n✨ {unit.name} casts {spell.name} and heals {target.name} for {heal} HP!" + Style.RESET_ALL)
                            time.sleep(1.2)
                            break

                        elif spell.is_aoe:
                            print(Fore.MAGENTA + f"\n✨ {unit.name} unleashes {spell.name}, targeting all enemies!" + Style.RESET_ALL)
                            unit.mp -= spell.cost  # MP deducted before applying AOE spell
                            apply_aoe_spell(spell, unit, enemies, is_enemy_cast=False)
                            time.sleep(0.4)
                        else:
                            target = choose_target(enemies)
                            if target:

                                unit.mp -= spell.cost  # MP deducted only after successful target confirmation
                                base_dmg = random.randint(*spell.damage_range)
                                total_dmg = base_dmg + unit.magic_power
                                final_dmg = max(0, total_dmg - target.resistance)
                                target.hp = max(0, target.hp - final_dmg)
                                print(Fore.MAGENTA + f"\n🔥 {unit.name} successfully casts {spell.name} and hits {target.name} for {final_dmg} damage!" + Style.RESET_ALL)
                                # Always treat spell.effect as list if it's not None
                                if spell.effect:
                                    effects = spell.effect if isinstance(spell.effect, list) else [spell.effect]
                                    for effect in effects:
                                        try_inflict_status(target, effect, spell_name=spell.name)

                                if target.hp == 1:
                                    print(Fore.YELLOW + f"{target.name}'s form flickers—barely hanging on!" + Style.RESET_ALL)
                                time.sleep(1.2)
                                if all_enemies_defeated(enemies):
                                    print(Fore.GREEN + Style.BRIGHT + "\n🎉 Victory! The enemies have been defeated!" + Style.RESET_ALL)
                                    return "win"
                            break

                    elif choice == "3":
                        use_item_in_combat(unit, players, enemies, shared_inventory)
                        time.sleep(1.2)
                        if all_enemies_defeated(enemies):
                            print(Fore.GREEN + Style.BRIGHT + "\n🎉 Victory! The enemies have been defeated!" + Style.RESET_ALL)
                            return "win"
                        break

                    elif choice == "4":
                        print(Fore.LIGHTCYAN_EX + f"\n📖 Inspecting {unit.name} the {unit.job}..." + Style.RESET_ALL)
                        unit.inspect_character()
                        input(Fore.YELLOW + "\nPress Enter to return to combat..." + Style.RESET_ALL)
                        continue  # loop back to same player

                    elif choice == "5":
                        unit.defending = True
                        print(Fore.LIGHTYELLOW_EX + f"{unit.name} raises their guard and prepares for the next attack." + Style.RESET_ALL)
                        time.sleep(1.2)
                        break

                    else:
                        print(Fore.YELLOW + "Invalid action." + Style.RESET_ALL)
                        continue

            else:
                alive_players = [p for p in players if p.hp > 0]
                if not alive_players:
                    break

                target = random.choice(alive_players)
                action, spell = unit.choose_action()

                if action == "spell":
                    print(Fore.RED + f"\n👹 {enemy_spell_cast_text(unit.name, spell.name)}" + Style.RESET_ALL)

                    if spell.is_aoe:
                        apply_aoe_spell(spell, unit, players, is_enemy_cast=True)

                        if spell.name == "Curse of the Stars":
                            for player in players:
                                if player.hp <= 0:
                                    continue
                                sanity_loss = random.randint(6, 12)
                                player.sanity = max(0, player.sanity - sanity_loss)
                                print(Fore.MAGENTA + f"{player.name} loses {sanity_loss} sanity under the Curse of the Stars!" + Style.RESET_ALL)

                        if spell.name == "Arcane Cataclysm":
                            if random.random() < 0.6:
                                effect = random.choice(["confusion", "fear", "madness"])
                                apply_mental_affliction(player, effect)

                            if random.random() < 0.3:
                                burn = random.randint(6, 12)
                                sanity_burn = random.randint(6, 12)
                                player.hp = max(0, player.hp - burn)
                                player.sanity = max(0, player.sanity - sanity_burn)
                                print(Fore.LIGHTRED_EX + f"🔥 {player.name} is seared for {burn} HP and {sanity_burn} sanity!" + Style.RESET_ALL)

                        if player.hp == 1 and not sentinel_instinct_used:
                            protected_ally = player
                            print(Fore.YELLOW + f"⚠️ {player.name} clings to life... something in the air shifts protectively." + Style.RESET_ALL)

                        continue  # Skip rest for AOE
                    
                    if spell.name == "Sanguine Pounce" and not getattr(target, "is_bleeding", False):
                        print(Fore.YELLOW + f"{unit.name} lunges with {spell.name}, but {target.name} isn't bleeding — the spell fizzles!" + Style.RESET_ALL)
                        unit.mp += spell.cost  # Refund MP
                        time.sleep(1.2)
                        break  # End player's turn
                    elif spell.name == "Sanguine Pounce":
                        print(Fore.RED + f"{spell.name} locks onto the scent of blood — {unit.name} strikes with savage precision!" + Style.RESET_ALL)

                    # 🩸 Eviscerate does bonus damage to already bleeding targets
                    if spell.name == "Eviscerate" and getattr(target, "is_bleeding", False):
                        print(Fore.RED + f"{spell.name} carves into open wounds — the bleeding makes it worse!" + Style.RESET_ALL)
                        bonus = random.randint(5, 10)
                        actual_dmg += bonus
                        print(Fore.LIGHTRED_EX + f"{target.name} takes an extra {bonus} damage due to bleeding!" + Style.RESET_ALL)

                    if spell.name == "Fireball":
                        if random.random() < 0.5:
                            splash_targets = [p for p in players if p.hp > 0 and p != target]
                            if splash_targets:
                                splash_target = random.choice(splash_targets)
                                splash_dmg = random.randint(5, 10)
                                splash_target.hp = max(0, splash_target.hp - splash_dmg)
                                print(Fore.LIGHTRED_EX + f"🔥 Splash damage from Fireball scorches {splash_target.name} for {splash_dmg} HP!" + Style.RESET_ALL)

                    if spell.name == "Gaze of the Abyss" and target.sanity < 40:
                        target.is_stunned = True
                        target.stun_turns = 1
                        print(Fore.MAGENTA + f"{target.name} stares into the abyss and is frozen in terror!" + Style.RESET_ALL)

                    # --- Handle Single Target Spells (including melee)
                    raw_dmg = random.randint(*spell.damage_range)
                    if spell.category == "melee":
                        total_dmg = raw_dmg + unit.attack_power
                        actual_dmg = max(0, total_dmg - target.defense)
                        dmg_type = "physical"
                    else:
                        total_dmg = raw_dmg + unit.magic_power
                        actual_dmg = max(0, total_dmg - target.resistance)
                        dmg_type = "magical"

                    if getattr(target, "defending", False):
                        actual_dmg = int(actual_dmg * 0.5)
                        print(Fore.CYAN + f"{target.name} defends and takes reduced {dmg_type} damage!" + Style.RESET_ALL)

                    # 🛡️ Guardian Shield Interception
                    guardian_candidates = [p for p in players if p.job == "Tank" and getattr(p, "is_guarding", False) and p.hp > 0]
                    if guardian_candidates and target != guardian_candidates[0]:
                        guardian = guardian_candidates[0]
                        redirected_dmg = int(actual_dmg * 0.5)
                        guardian.hp = max(0, guardian.hp - redirected_dmg)
                        print(Fore.CYAN + f"{guardian.name} intercepts the blow from {spell.name}, taking {redirected_dmg} damage for {target.name}!" + Style.RESET_ALL)
                        continue  # Skip applying damage to the original target

                    # 🛡️ Sentinel Passive
                    if protected_ally == target and target.hp == 1 and not sentinel_instinct_used:
                        sentinel_instinct_used = True
                        sentinel_successful = True

                        if guarding_tank and guarding_tank.hp > 0:
                            print(Fore.CYAN + f"\n🛡️ {guarding_tank.name} senses danger and intercepts the {spell.name} meant for {target.name}!" + Style.RESET_ALL)

                            reduced_dmg = int(actual_dmg * 0.1)
                            reduced_dmg = max(0, reduced_dmg - guarding_tank.resistance)
                            apply_spell_damage_and_effect(spell, unit, guarding_tank, dmg_type, reduced_dmg)

                            guarding_tank = None
                            time.sleep(1.0)

                            heal_amount = random.randint(15, 30)
                            target.hp = min(target.max_hp, target.hp + heal_amount)
                            print(Fore.GREEN + f"{target.name} is enveloped in protective light and recovers {heal_amount} HP!" + Style.RESET_ALL)
                            time.sleep(1.2)

                        else:
                            apply_spell_damage_and_effect(spell, unit, target, dmg_type, actual_dmg)

                    else:
                        apply_spell_damage_and_effect(spell, unit, target, dmg_type, actual_dmg)

                    if target.hp == 1 and not sentinel_instinct_used:
                        protected_ally = target
                        print(Fore.YELLOW + f"⚠️ {target.name} clings to life... something in the air shifts protectively." + Style.RESET_ALL)

                time.sleep(1.2)

                for player in players:
                    if player.is_guarding and not getattr(player, 'is_guarded', False):
                        player.is_guarding = False
                        print(Fore.LIGHTWHITE_EX + f"{player.name}'s Guardian Shield fades." + Style.RESET_ALL)

        if all_enemies_defeated(enemies):
            print(Fore.GREEN + Style.BRIGHT + "\n🎉 Victory! The enemies have been defeated!" + Style.RESET_ALL)
            enemies.clear()
            if overlay:
                overlay.update_display()
            return "win"

        if all(player.hp <= 0 for player in players):
            print(Fore.RED + Style.BRIGHT + "\n💀 Your party has fallen to the dungeon..." + Style.RESET_ALL)
            if overlay:
                overlay.update_display()
            return "lose"

def choose_target(units):
    alive_units = [u for u in units if u.hp > 0]
    if not alive_units:
        return None

    while True:
        print(Fore.LIGHTWHITE_EX + "\nSelect a target:" + Style.RESET_ALL)
        for idx, unit in enumerate(alive_units, 1):
            print(f"  {idx}. {unit.name} ({unit.hp} HP)")

        choice = input(Fore.LIGHTWHITE_EX + "> " + Style.RESET_ALL).strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(alive_units):
                return alive_units[idx]

        print(Fore.YELLOW + "⚠️ Invalid target. Please try again." + Style.RESET_ALL)


# =============================
# 🧠 TODO: Enhanced Enemy Spell Logic
# =============================

# =============================
# 🔧 TODO: Structural Enhancements & Logic Cleanup
# =============================

# A. Consider moving enemy spell flavor text to spells.py for easier management.
# B. Expand enemy_spell_cast_text() for other spells beyond Fireball, Eldritch Flame, etc.
# C. Refactor spell.effect to support multiple concurrent effects or stacking logic.

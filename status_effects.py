# status_effects.py
from colorama import Fore, Style
import random

# 🎯 Custom status effect chances for specific spells
special_status_chances = {
    "Unsettling Gaze": ("bleed", 1.0),        # 100% chance
    "Eldritch Flame": ("mindfire", 0.75),     # 75% chance
    "Void Flame": ("mindfire", 0.5),          # 50% chance
    "Fireball": ("mindfire", 0.4),            # 40% chance
    "Void Bolt": ("random_mental", 0.5),      # 50% chance
    "Cursed Blow": ("mindfire", 0.4),         # 40% chance
    "Claw": ("bleed", 0.6),                   # 60% chance
    "Bite": ("bleed", 0.6),                   # 60% chance
    "Eviscerate": ("bleed", 0.8),             # 80% chance
    "Tear": ("bleed", 0.7),                   # 70% chance
    "Mutilate": ("bleed", 0.9),               # 90% chance
    "Dread Aura": ("fear", 1.0),              # 100% chance
    "Gaze of the Abyss": ("madness", 1.0),    # 100% chance
    "Hypnotic Gaze": ("confusion", 1.0),      # 100% chance
    "Unnerving Aura": ("fear", 0.6),          # 60% chance
    "Foul Affliction": ("madness", 0.6),      # 60% chance
    "Horrific Wail": ("madness", 0.7),        # 70% chance
    "Call of Madness": ("madness", 0.6),      # 60% chance
    "Curse of the Stars": ("madness", 0.5),   # 50% chance
    "Cosmic Vampirism": ("madness", 0.3),     # 30% chance
}

# === Apply a mental affliction or physical effect if not protected ===
def apply_mental_affliction(target, effect, spell_name=None):
    if getattr(target, 'mental_resistance_turns', 0) > 0:
        print(Fore.YELLOW + f"{target.name} resists the {effect} due to mental clarity!" + Style.RESET_ALL)
        return

    if effect == "confusion":
        if target.is_confused:
            return
        target.is_confused = True
        target.confusion_turns = 3  # default
        if spell_name == "Hypnotic Gaze":
            target.confusion_turns = max(target.confusion_turns, 2)
            if hasattr(target, 'mp'):
                target.mp = max(0, target.mp - 5)
                print(Fore.BLUE + f"{target.name} loses 5 MP to Hypnotic Gaze!" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"{target.name} is confused by the horrors they perceive!" + Style.RESET_ALL)

    elif effect == "fear":
        if target.is_feared:
            return
        target.is_feared = True
        target.fear_turns = 3
        print(Fore.MAGENTA + f"{target.name} trembles in fear, heart pounding!" + Style.RESET_ALL)

    elif effect == "madness":
        if target.is_insane:
            return
        target.is_insane = True
        target.madness_turns = 3
        print(Fore.MAGENTA + f"{target.name}'s eyes glaze with madness!" + Style.RESET_ALL)

    elif effect == "mindfire":
        if target.is_mindfired:
            return
        target.is_mindfired = True
        target.mindfire_turns = 3
        print(Fore.LIGHTRED_EX + f"{target.name} is engulfed in a burning Mindfire!" + Style.RESET_ALL)

    elif effect == "bleed":
        if target.is_bleeding:
            return
        target.is_bleeding = True
        target.bleeding_turns = 3
        if spell_name == "Unsettling Gaze":
            print(Fore.RED + f"{target.name} begins to bleed profusely from an unseen wound!" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"{target.name} starts bleeding!" + Style.RESET_ALL)

# === Apply effects based on spell or item ===
def try_inflict_status(target, effect: str, chance: float = 0.4, spell_name=None):
    if not effect or target.hp <= 0:
        return

    # 🎯 Override chance if a special spell rule is defined
    if spell_name and spell_name in special_status_chances:
        special_effect, special_chance = special_status_chances[spell_name]
        if effect == special_effect:
            chance = special_chance

    # 🧠 Apply mental resistance if applicable
    resistance = getattr(target, 'mental_resistance', 0)
    if resistance and effect in special_status_chances.values():
        chance *= (1 - resistance)

    # 🎲 Random mental affliction handler
    if effect == "random_mental":
        if random.random() < chance:
            affliction = random.choice(["confusion", "fear", "madness"])
            apply_mental_affliction(target, affliction)
        else:
            print(Fore.YELLOW + f"{target.name} resists the creeping madness!" + Style.RESET_ALL)
        return

    if random.random() < chance:
        apply_mental_affliction(target, effect, spell_name=spell_name)
    else:
        print(Fore.YELLOW + f"{target.name} resists the {effect}!" + Style.RESET_ALL)


# === Called each turn to apply status logic ===
def handle_status_effects(unit):
    if getattr(unit, 'is_mindfired', False):
        burn = random.randint(5, 10)
        sanity_burn = random.randint(3, 6)
        unit.hp = max(0, unit.hp - burn)
        unit.sanity = max(0, unit.sanity - sanity_burn)
        unit.mindfire_turns -= 1
        print(Fore.RED + f"🔥 {unit.name} suffers {burn} HP and {sanity_burn} sanity from Mindfire!" + Style.RESET_ALL)
        if unit.mindfire_turns <= 0:
            unit.is_mindfired = False
            print(Fore.YELLOW + f"{unit.name}'s Mindfire has burned out." + Style.RESET_ALL)

    if getattr(unit, 'is_bleeding', False):
        bleed = random.randint(3, 6)
        unit.hp = max(0, unit.hp - bleed)
        unit.bleeding_turns -= 1
        print(Fore.LIGHTRED_EX + f"🩸 {unit.name} bleeds for {bleed} damage!" + Style.RESET_ALL)
        
        if unit.hp == 0:
            print(Fore.RED + f"{unit.name} succumbs to blood loss..." + Style.RESET_ALL)

        if unit.bleeding_turns <= 0:
            unit.is_bleeding = False
            print(Fore.YELLOW + f"{unit.name}'s wounds stop bleeding." + Style.RESET_ALL)


    if getattr(unit, 'mental_resistance_turns', 0) > 0:
        unit.mental_resistance_turns -= 1

    if getattr(unit, 'is_confused', False):
        unit.confusion_turns -= 1
        if unit.confusion_turns <= 0:
            unit.is_confused = False
            print(Fore.YELLOW + f"{unit.name}'s confusion fades." + Style.RESET_ALL)
        elif random.random() < 0.4:
            print(Fore.LIGHTMAGENTA_EX + f"{unit.name} is confused and skips their turn..." + Style.RESET_ALL)
            return "skip"

    if getattr(unit, 'is_feared', False):
        unit.fear_turns -= 1
        if unit.fear_turns <= 0:
            unit.is_feared = False
            print(Fore.YELLOW + f"{unit.name}'s fear subsides." + Style.RESET_ALL)
        elif random.random() < 0.3:
            print(Fore.LIGHTBLUE_EX + f"{unit.name} hesitates in fear and cannot act!" + Style.RESET_ALL)
            return "skip"

    if getattr(unit, 'is_insane', False):
        unit.madness_turns -= 1
        if unit.madness_turns <= 0:
            unit.is_insane = False
            print(Fore.YELLOW + f"{unit.name} regains their sanity." + Style.RESET_ALL)
        elif random.random() < 0.2:
            print(Fore.LIGHTRED_EX + f"{unit.name} is overtaken by madness and lashes out randomly!" + Style.RESET_ALL)
            return "chaos"
        
    if getattr(unit, 'is_stunned', False):
        unit.stun_turns -= 1
        if unit.stun_turns <= 0:
            unit.is_stunned = False
            print(Fore.YELLOW + f"{unit.name} shakes off the abyssal stupor." + Style.RESET_ALL)
        else:
            print(Fore.LIGHTBLACK_EX + f"{unit.name} is stunned and cannot act!" + Style.RESET_ALL)
        return "skip"

    return "normal"


def handle_sanity_effects(player):
    """Applies sanity-based behavior and consequences."""
    if player.hp <= 0:
        return "skip"

    if player.sanity <= 0:
        if not getattr(player, "is_insane", False):
            player.is_insane = True
            print(Fore.RED + f"💀 {player.name} has gone completely insane!" + Style.RESET_ALL)
        return "chaos"

    if 1 <= player.sanity <= 25:
        print(Fore.MAGENTA + f"😱 {player.name} is on the brink of madness!" + Style.RESET_ALL)
        if random.random() < 0.25:
            action = random.choice(["skip", "self_hit", "hallucinate"])
            if action == "skip":
                print(Fore.RED + f"{player.name} is frozen by terror and does nothing!" + Style.RESET_ALL)
                return "skip"
            elif action == "self_hit":
                dmg = random.randint(5, 12)
                player.hp = max(0, player.hp - dmg)
                print(Fore.RED + f"{player.name} lashes out at unseen horrors, taking {dmg} self-inflicted damage!" + Style.RESET_ALL)
            elif action == "hallucinate":
                print(Fore.LIGHTMAGENTA_EX + random.choice([
                    f"{player.name} whispers about the eyes in the floor...",
                    f"{player.name} sees something reaching from the walls...",
                    f"{player.name} claws at their skin, muttering eldritch syllables..."
                ]) + Style.RESET_ALL)

    elif 26 <= player.sanity <= 50:
        print(Fore.LIGHTMAGENTA_EX + f"🌀 {player.name} struggles to maintain clarity..." + Style.RESET_ALL)
        player.sanity = max(0, player.sanity - random.randint(1, 2))
        if random.random() < 0.15:
            print(Fore.YELLOW + f"{player.name}'s spell goes awry!" + Style.RESET_ALL)
            return "miscast"

    elif 51 <= player.sanity <= 74:
        if random.random() < 0.05:
            print(Fore.YELLOW + f"{player.name}'s concentration falters..." + Style.RESET_ALL)
            return "fizzle"

    return "normal"

# ========================== TODO: Add Mental Resistance System ==========================
# ✔ Purpose: Introduce a dedicated stat that reduces the chance of mental or bleed afflictions.
# ✔ Thematic fit: Willpower or Mental Resistance reflects Lovecraftian fragility of the mind.
#
# --- Core Tasks ---
# [ ] 1. Add a `mental_resistance` attribute to both Player and Enemy classes (start at ~0.1–0.3).
#     • Suggested default: self.mental_resistance = 0.2  # (20% resistance)
#     • Place this in party_setup.py, enemy_classes.py, or wherever your character classes are defined.
#
# [ ] 2. Update `try_inflict_status()` in status_effects.py to apply resistance:
#     • final_chance = base_chance * (1 - target.mental_resistance)
#     • Ensure fallback to 0 if the attribute doesn’t exist (use getattr).
#
# [ ] 3. Add resistance-based flavor message:
#     • Print something like: "[Name] resists the creeping madness!" when status fails.
#
# [ ] 4. (Optional) Make resistance *weaken* at lower sanity levels:
#     • If target.sanity < 50, reduce mental_resistance or increase final_chance.
#
# [ ] 5. (Optional) Consider naming the stat: `willpower`, `resolve`, `lucidity`, or keep `mental_resistance`.
#
# [ ] 6. Reflect stat in UI/inspection (if applicable).
#
# --- Update Reminder ---
# [ ] ✅ Be sure to update:
#     → Player class in party_setup.py
#     → Enemy class in enemy_classes.py or where you define monsters
#     → Combat logic in vivid_battle.py (calls try_inflict_status)

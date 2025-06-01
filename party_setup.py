# party_setup.py
from colorama import Fore, Style
import random
from spells import spell_lookup
from ui_utils import render_bar, sanity_descriptor, hp_descriptor, mp_descriptor

class Player:
    def __init__(self, name, job, max_hp, max_mp, speed, spells,
                 attack_power=0, magic_power=0, defense=0, resistance=0):
        self.name = name
        self.job = job
        self.max_hp = max_hp
        self.hp = max_hp
        self.max_mp = max_mp
        self.mp = max_mp
        self.speed = speed
        self.attack_power = attack_power
        self.magic_power = magic_power
        self.defense = defense
        self.resistance = resistance
        self.sanity = 100
        self.spells = spells
        self.is_guarding = False
        self.sentinel_ready = False
        self.defending = False
        self.items = []
        # Mental status effects
        self.is_confused = False
        self.is_feared = False
        self.is_insane = False
        self.is_mindfired = False
        self.is_bleeding = False
        self.is_stunned = False
        self.mindfire_turns = 0
        self.mental_resistance_turns = 0
        self.confusion_turns = 0
        self.fear_turns = 0
        self.madness_turns = 0
        self.bleeding_turns = 0

    def is_alive(self):
        return self.hp > 0 and self.sanity > 0
    
    def has_status_effects(self):
        return any([
            self.is_confused,
            self.is_feared,
            self.is_insane,
            self.is_mindfired,
            self.is_bleeding,
            self.mental_resistance_turns > 0
        ])

    def describe_status_effects(self):
        def pluralize_turns(n):
            return f"{n} turn" if n == 1 else f"{n} turns"

        if self.has_status_effects():
            print(Fore.LIGHTRED_EX + "\n🧠 Mental & Physical Status Effects:" + Style.RESET_ALL)
            if self.is_confused:
                print(f"  🤯 Confused – Struggles to discern friend from foe ({pluralize_turns(self.confusion_turns)} remaining)")
            if self.is_feared:
                print(f"  😨 Feared – Frozen by terror ({pluralize_turns(self.fear_turns)} remaining)")
            if self.is_insane:
                print(f"  🧠 Madness – Lost in hallucination and chaos ({pluralize_turns(self.madness_turns)} remaining)")
            if self.is_mindfired:
                print(f"  🔥 Mindfire – Tormented by burning psychic flames ({pluralize_turns(self.mindfire_turns)} remaining)")
            if self.is_bleeding:
                print(f"  🩸 Bleeding – Losing HP each turn ({pluralize_turns(self.bleeding_turns)} remaining)")
        else:
            print(Fore.LIGHTGREEN_EX + "\n🧠 Status: Stable" + Style.RESET_ALL)

    def display_bars(self):
        class_icons = {
            "White Mage": "✨",
            "Black Mage": "🧙",
            "Tank": "🛡️",
            "Occultist": "🔮"
        }

        icon = class_icons.get(self.job, "")
        label = f"🎭 {self.name} the {self.job} {icon}"

        hp_bar = render_bar("HP", self.hp, self.max_hp, Fore.GREEN, bar_width=25)
        mp_bar = render_bar("MP", self.mp, self.max_mp, Fore.BLUE, bar_width=15)

        # Check for show_sanity_bar flag (set at game start)
        if getattr(self, "show_sanity_bar", False):
            sanity_bar = render_bar("SAN", self.sanity, 100, Fore.MAGENTA, bar_width=15)
            print(f"{label:<28} {hp_bar}   {mp_bar}   {sanity_bar}")
        else:
            print(f"{label:<28} {hp_bar}   {mp_bar}")

        print()  # space between party members

    def generate_damage(self):
        return random.randint(4, 8) + self.attack_power

    def list_inventory(self):
        if not self.items:
            print("👜 Inventory is empty.")
            return
        print(f"\n📦 {self.name}'s Inventory:")
        for i, entry in enumerate(self.items, 1):
            item = entry["item"]
            qty = entry["qty"]
            print(f"  {i}. {item.name} x{qty} – {item.description}")

    def add_item(self, new_item):
        for entry in self.items:
            if entry["item"].name == new_item.name:
                entry["qty"] += 1
                print(f"🎒 {self.name} claimed another {new_item.name}! (x{entry['qty']})")
                return
        self.items.append({"item": new_item, "qty": 1})
        print(f"🎒 {self.name} obtained {new_item.name}!")

    def choose_spell(self):
        if not self.spells:
            print("You don't know any spells yet!")
            return None
        print("\n📖 Forbidden Incantations:")
        for i, spell in enumerate(self.spells, 1):
            print(f"  {i}. {spell.name} (Cost: {spell.cost} MP, Type: {spell.category})")
        print("  0. Cancel")
        while True:
            try:
                choice = int(input("Select spell number: "))
                if choice == 0:
                    return None
                elif 1 <= choice <= len(self.spells):
                    return self.spells[choice - 1]
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")

    def choose_item(self):
        if not self.items:
            print("You have no items.")
            return None, None
        print("\n🎒 Choose an item:")
        for i, entry in enumerate(self.items, 1):
            item = entry["item"]
            qty = entry["qty"]
            print(f"  {i}. {item.name} x{qty} – {item.description}")
        print("  0. Cancel")
        while True:
            try:
                choice = int(input("Select item number: "))
                if choice == 0:
                    return None, None
                elif 1 <= choice <= len(self.items):
                    return self.items[choice - 1]["item"], choice - 1
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")

    def inspect_character(self, shared_inventory=None):
        def pluralize_turns(n):
            return f"{n} turn" if n == 1 else f"{n} turns"

        class_flavor = {
            "White Mage": (
                "✨ A supplicant of dying stars, the White Mage invokes fading celestial echoes\n"
                "   to mend flesh and soul. Their prayers carry warmth — but only just.\n"
                "   They are a fragile bastion of mercy in a world that has none."
            ),
            "Black Mage": (
                "🧙 A scholar of flame and frost, the Black Mage binds elemental fury\n"
                "   into sigils etched from memory and madness. Every incantation risks\n"
                "   unraveling more than their enemies — it may unravel themselves."
            ),
            "Tank": (
                "🛡️ A relic of forgotten wars, the Tank bears the weight of the void\n"
                "   without blinking. Not by choice — but because they have seen worse.\n"
                "   Steel, flesh, and defiance fused into one trembling wall against the dark."
            ),
            "Occultist": (
                "🔮 A seeker who dared to listen when the stars whispered back.\n"
                "   The Occultist’s power comes not from study, but surrender —\n"
                "   to glyphs that shift when unobserved, and truths that curse the knowing."
            )
        }

        print(Fore.LIGHTMAGENTA_EX + f"\n🎭 {self.name} the {self.job}" + Style.RESET_ALL)
        print(class_flavor.get(self.job, ""))
        print()  # Add a blank line
        print(Fore.LIGHTWHITE_EX + "\n📊 Stats:" + Style.RESET_ALL)

        # Health
        hp_state = hp_descriptor(self.hp, self.max_hp)
        hp_ratio = self.hp / self.max_hp
        hp_color = Fore.LIGHTGREEN_EX if hp_ratio >= 0.75 else (
            Fore.YELLOW if hp_ratio >= 0.5 else (
                Fore.LIGHTRED_EX if hp_ratio >= 0.25 else Fore.RED
            )
        )
        print(hp_color + f"  ❤️  HP:         {self.hp}/{self.max_hp} ({hp_state})" + Style.RESET_ALL)

        # Mana
        mp_state = mp_descriptor(self.mp, self.max_mp)
        print(Fore.CYAN + f"  🔵  MP:         {self.mp}/{self.max_mp} ({mp_state})" + Style.RESET_ALL)

        # Sanity
        sanity_state = sanity_descriptor(self.sanity)
        sanity_color = Fore.LIGHTGREEN_EX if self.sanity >= 75 else (
            Fore.YELLOW if self.sanity >= 50 else (
                Fore.LIGHTRED_EX if self.sanity >= 25 else Fore.RED
            )
        )
        print(sanity_color + f"  🧩  Sanity:     {self.sanity}/100 ({sanity_state})" + Style.RESET_ALL)

        # Combat stats
        print(Fore.YELLOW + f"  🗡️  Attack:     {self.attack_power}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"  📘  Magic:      {self.magic_power}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"  🛡️  Defense:    {self.defense}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"  🧠  Resistance: {self.resistance}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"  🌀  Speed:      {self.speed}" + Style.RESET_ALL)


        self.describe_status_effects()

        if self.mental_resistance_turns > 0:
            print(Fore.CYAN + f"🧘 Mental Clarity active – immune to afflictions for {self.mental_resistance_turns} more turn(s)" + Style.RESET_ALL)

        if self.spells:
            print(Fore.LIGHTWHITE_EX + "\n📖 Known Spells:" + Style.RESET_ALL)
            for spell in self.spells:
                print(f"  ✦ {spell.name} – Cost: {spell.cost} MP, Type: {spell.category}")
                if hasattr(spell, "description"):
                    print(f"     {spell.description}")
        else:
            print("\nNo spells known.")

        if self.job.lower() == "tank":
            print(Fore.LIGHTBLUE_EX + "\n🛡️ Passive Ability: Protective Instinct" + Style.RESET_ALL)
            print("  If an ally is reduced to exactly 1 HP, the Tank automatically triggers a one-time Sentinel's Oath")
            print("  (no MP cost) to save them before a follow-up strike can land.")

        if shared_inventory: # Supports both Shared and Personal Inventory (Yet to be implemented)
            print(Fore.LIGHTWHITE_EX + "\n🎒 Shared Inventory:" + Style.RESET_ALL)
            for entry in shared_inventory:
                print(f"  • {entry['item'].name} x{entry['qty']}: {entry['item'].description}")
        elif self.items:
            print(Fore.LIGHTWHITE_EX + "\n🎒 Personal Inventory:" + Style.RESET_ALL)
            for entry in self.items:
                print(f"  • {entry['item'].name} x{entry['qty']}: {entry['item'].description}")
        else:
            print(Fore.LIGHTWHITE_EX + "\n🎒 Inventory: (empty)" + Style.RESET_ALL)

        # Offer the option to study
        study = input(Fore.LIGHTWHITE_EX + "\n📖 Would you like to study your spellbook? (Y/N): " + Style.RESET_ALL).lower()
        if study == "y":
            self.study_spellbook()

        print(Fore.LIGHTBLACK_EX + "🗝️  Madness leaves clues — Inspect often." + Style.RESET_ALL)

    def study_spellbook(self):
        if not self.spells:
            print("\nYou don't know any spells yet.")
            return

        print("\n📚 You unroll the ancient spellbook and begin studying...\n")
        for i, spell in enumerate(self.spells, 1):
            print(f"{i}. {spell.name} (Cost: {spell.cost} MP, Type: {spell.category})")
            if hasattr(spell, "cast_description"):
                print("   Flavor:", spell.cast_description())
            if spell.effect:
                effects = spell.effect if isinstance(spell.effect, list) else [spell.effect]
                print("   Effect:", ", ".join(effects))
            print()

        print("🧠 As you read, forgotten knowledge seems to stir just beyond perception...\n")


# Class Archetypes
class WhiteMage(Player):
    def __init__(self, name):
        super().__init__(name, "White Mage", 200, 120, random.randint(35, 50),
                         [spell_lookup["Healing Light"], spell_lookup["Sacred Rebuke"]],
                         attack_power=2, magic_power=12, defense=5, resistance=10)

class BlackMage(Player):
    def __init__(self, name):
        super().__init__(name, "Black Mage", 170, 140, random.randint(35, 55),
                         [spell_lookup["Fireball"], spell_lookup["Ice Spike"]],
                         attack_power=3, magic_power=14, defense=3, resistance=12)

class Tank(Player):
    def __init__(self, name):
        super().__init__(name, "Tank", 300, 100, random.randint(20, 40),
                         [spell_lookup["Guardian Shield"], spell_lookup["Sentinel's Oath"]],
                         attack_power=6, magic_power=4, defense=15, resistance=5)

class Occultist(Player):
    def __init__(self, name):
        super().__init__(name, "Occultist", 180, 130, random.randint(30, 50),
                         [spell_lookup["Void Bolt"], spell_lookup["Eldritch Flame"]],
                         attack_power=6, magic_power=15, defense=2, resistance=8)

# Party Setup
def setup_party():
    print("\n📜 You stand before the Dungeon of the Silver Key...")
    print("☄️ Choose up to 3 champions to defy the creeping madness.")

    available_classes = ["White Mage", "Black Mage", "Tank", "Occultist"]
    party = []

    while len(party) < 3:
        print("\nSelect your companion:")
        for idx, job in enumerate(available_classes, 1):
            print(f"{idx}. {job}")

        choice = input("\nEnter number or press Enter to proceed: ").strip()
        if choice == "":
            if len(party) >= 1:
                break
            else:
                print("⚠️ You must select at least one brave soul.")
                continue

        if not choice.isdigit() or not (1 <= int(choice) <= len(available_classes)):
            print("⚠️ Invalid choice.")
            continue

        selected_class = available_classes[int(choice) - 1]

        # 🎭 Flavor Text Descriptions
        if selected_class == "White Mage":
            print("✨ The White Mage: A conduit of fading light in a world gripped by madness.")
        elif selected_class == "Black Mage":
            print("🧙 The Black Mage: Master of elemental chaos, a flickering torch in shadow.")
        elif selected_class == "Tank":
            print("🛡️ The Tank: A wall of flesh and steel. The void recoils from its will.")
        elif selected_class == "Occultist":
            print("🔮 The Occultist: Scholar of forgotten truths, cursed with terrible insight.")

        name = input(f"What shall your {selected_class} be called? ").strip()

        if selected_class == "White Mage":
            hero = WhiteMage(name)
        elif selected_class == "Black Mage":
            hero = BlackMage(name)
        elif selected_class == "Tank":
            hero = Tank(name)
        elif selected_class == "Occultist":
            hero = Occultist(name)
        else:
            print("⚠️ That class does not exist.")
            continue

        party.append(hero)
        print(f"✅ {name}, the {selected_class}, has joined your descent.")

    print("\n🧭 Chosen Seekers:")
    for member in party:
        print(f" - {member.name} the {member.job}")
    
    print("🧠 Their minds are intact — for now.")
    return party


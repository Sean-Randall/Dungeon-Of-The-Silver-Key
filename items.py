# items.py

from colorama import Fore, Style
from spells import spell_lookup
from status_effects import try_inflict_status

class Item:
    def __init__(self, name, description, item_type="misc",
                 heal_range=None, mana_restore=0, damage_range=None,
                 stat_boost=None, teaches_spell=None, allowed_classes=None, 
                 pickup_text=None, unique=False, effect=False,):
        self.name = name
        self.description = description
        self.item_type = item_type  # 'healing', 'mana', 'attack', 'boost', 'key', 'scroll'
        self.heal_range = heal_range
        self.mana_restore = mana_restore
        self.damage_range = damage_range
        self.stat_boost = stat_boost
        self.teaches_spell = teaches_spell
        self.allowed_classes = allowed_classes or []
        self.pickup_text = pickup_text
        self.unique = unique
        self.effect = effect
        self.found = False if unique else None

    def inspect_item(self):
        print(Fore.CYAN + f"\n{self.name}: {self.description}" + Style.RESET_ALL)
        if self.heal_range:
            print(Fore.GREEN + f"• Heals: {self.heal_range[0]}-{self.heal_range[1]} HP" + Style.RESET_ALL)
        if self.mana_restore:
            print(Fore.BLUE + f"• Restores: {self.mana_restore} MP" + Style.RESET_ALL)
        if self.damage_range:
            print(Fore.RED + f"• Deals: {self.damage_range[0]}-{self.damage_range[1]} damage" + Style.RESET_ALL)
        if self.stat_boost:
            print(Fore.YELLOW + f"• Boosts stats by {self.stat_boost}" + Style.RESET_ALL)
        if self.teaches_spell:
            print(Fore.MAGENTA + f"• Teaches Spell: {self.teaches_spell}" + Style.RESET_ALL)

# Add these references at the bottom to support lookup
item_lookup = {}

def register_item(item, aliases=None):
    item_lookup[item.name] = item
    if aliases:
        for alias in aliases:
            item_lookup[alias] = item
    return item

def apply_item_effect(player, item):
    """Apply immediate stat boosts or teach a spell (if applicable)."""
    effect_applied = False

    # Stat boosts
    if item.stat_boost:
        for stat, value in item.stat_boost.items():
            if hasattr(player, stat):
                setattr(player, stat, getattr(player, stat) + value)
                print(Fore.YELLOW + f"{player.name}'s {stat} increased by {value}!" + Style.RESET_ALL)
                effect_applied = True

    # Spell-teaching (single target, e.g., outside battle use)
    if item.teaches_spell:
        spell = spell_lookup.get(item.teaches_spell)
        if not spell:
            print(Fore.RED + "⚠️ This scroll seems damaged or incomplete." + Style.RESET_ALL)
            return effect_applied

        if player.job not in spell.allowed_classes:
            print(Fore.RED + f"{player.name} cannot learn {spell.name} (wrong class)." + Style.RESET_ALL)
        elif spell in player.spells:
            print(Fore.LIGHTBLUE_EX + f"{player.name} already knows {spell.name}." + Style.RESET_ALL)
        else:
            player.spells.append(spell)
            print(Fore.YELLOW + f"\n✨ {player.name} has learned the spell: {spell.name}!" + Style.RESET_ALL)
            effect_applied = True

    return effect_applied


def teach_spell_to_party(players, item):
    """Teaches a spell to all eligible party members. Only for unique scrolls."""
    if not item.teaches_spell:
        return False

    spell = spell_lookup.get(item.teaches_spell)
    if not spell:
        print(Fore.RED + f"⚠️ The spell {item.teaches_spell} could not be found." + Style.RESET_ALL)
        return False

    if item.found:
        print(Fore.LIGHTBLACK_EX + "The scroll has already been used." + Style.RESET_ALL)
        return False

    taught_anyone = False
    for player in players:
        if player.job in spell.allowed_classes and spell not in player.spells:
            player.spells.append(spell)
            print(Fore.YELLOW + f"✨ {player.name} learns the spell: {spell.name}!" + Style.RESET_ALL)
            taught_anyone = True
        elif player.job in spell.allowed_classes:
            print(Fore.LIGHTBLUE_EX + f"{player.name} already knows {spell.name}." + Style.RESET_ALL)
        else:
            print(Fore.RED + f"{player.name} cannot learn {spell.name}." + Style.RESET_ALL)

    if not taught_anyone:
        print(Fore.LIGHTBLACK_EX + "No one could learn from the scroll." + Style.RESET_ALL)
    else:
        item.found = True

    return taught_anyone


# Replace your item definitions to register them with item_lookup
standard_health_potion = register_item(Item(
    name="Health Potion",
    description="A red-hued restorative brew mixed by a skilled alchemist.",
    item_type="healing",
    heal_range=(45, 70)
), aliases=["Standard Health Potion", "Regular Health Potion"])

major_health_potion = register_item(Item(
    name="Major Health Potion",
    description="A potent crimson elixir. Greatly restores vitality.",
    item_type="healing",
    heal_range=(80, 120)
), aliases=["Large Health Potion", "Greater Health Potion"])

minor_health_potion = register_item(Item(
    name="Minor Health Potion",
    description="A lightly infused red brew. Restores some vitality.",
    item_type="healing",
    heal_range=(25, 40)
), aliases=["Small Health Potion"])

standard_mana_potion = register_item(Item(
    name="Standard Mana Potion",
    description="A deep blue potion that restores magical energy.",
    item_type="mana",
    mana_restore=40
), aliases=["Mana Potion", "Blue Potion"])

greater_mana_potion = register_item(Item(
    name="Greater Mana Potion",
    description="A potent elixir brimming with arcane power.",
    item_type="mana",
    mana_restore=75
), aliases=["Major Mana Potion", "Large Mana Potion"])

silver_key = register_item(Item(
    name="Silver Key",
    description="A shimmering silver key covered in swirling runes.",
    item_type="key",
    stat_boost={"magic_power": 5},
    unique=True
))


sun_talisman = register_item(Item(
    name="Sun Talisman",
    description="A radiant charm infused with solar energy.",
    item_type="boost",
    stat_boost={"speed": 15, "resistance": 5},
    pickup_text=Fore.YELLOW + "☀️ The talisman glows warmly..." + Style.RESET_ALL,
    unique=True
))

talisman_azrath = register_item(Item(
    name="Talisman of Saint Azrath",
    description="An ancient relic that whispers prayers...",
    item_type="boost",
    stat_boost={"defense": 10, "resistance": 10},
    pickup_text=Fore.BLUE + "🛡️ A hush falls..." + Style.RESET_ALL,
    unique=True
))

ornate_tome = register_item(Item(
    name="Ornate Tome",
    description="A heavy tome bound in sacred gold threads.",
    item_type="scroll",
    teaches_spell="Greater Heal",
    allowed_classes=["White Mage"],
    pickup_text=Fore.GREEN + "📖 The tome glows..." + Style.RESET_ALL,
    unique=True
))

cursed_tome = register_item(Item(
    name="Cursed Tome",
    description="A dark tome bound in cursed flesh.",
    item_type="scroll",
    teaches_spell="Call of Madness",
    allowed_classes=["Occultist"],
    pickup_text=Fore.MAGENTA + "📖 Whispers invade..." + Style.RESET_ALL,
    unique=True
))

ancient_scroll = register_item(Item(
    name="Ancient Scroll",
    description="A tattered scroll inscribed with words of hope.",
    item_type="scroll",
    teaches_spell="Pure of Mind",
    allowed_classes=["White Mage", "Occultist"],
    pickup_text=Fore.CYAN + "📜 You feel a shield..." + Style.RESET_ALL,
    unique=True
))

ancient_spellbook = register_item(Item(
    name="Ancient Spellbook",
    description="A leather-bound book smoldering with abyssal energies.",
    item_type="scroll",
    teaches_spell="Void Flame",
    allowed_classes=["Black Mage", "Occultist"],
    pickup_text=Fore.RED + "📕 Abyssal power..." + Style.RESET_ALL,
    unique=True
))

molotov = register_item(Item(
    name="Molotov of Whispering Flame",
    description="A glass bomb alight with murmuring fire.",
    item_type="attack",
    damage_range=(35, 45),
    effect="mindfire",
    pickup_text=Fore.YELLOW + "🔥 The bottle pulses..." + Style.RESET_ALL
))

black_ichor = register_item(Item(
    name="Phial of Black Ichor",
    description="A sealed vial of shadowy ichor.",
    item_type="attack",
    damage_range=(40, 50),
    effect="madness",
    pickup_text=Fore.MAGENTA + "🩸 The ichor pulses..." + Style.RESET_ALL
))

veil_of_silence_scroll = register_item(Item(
    name="Scroll of Veil of Silence",
    description="A sacred scroll inked in starlight and sealed with wax from beyond time.",
    item_type="scroll",
    teaches_spell="Veil of Silence",
    allowed_classes=["White Mage"],
    pickup_text=Fore.CYAN + "🕯️ A hush descends as you unfurl the scroll..." + Style.RESET_ALL,
    unique=True
))

# Update all_items with reference
all_items = list(item_lookup.values())

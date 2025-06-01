# rooms.py
from colorama import Fore
import random
from items import item_lookup

class Room:
    def __init__(self, room_number, description, contents=None, enemy="none", is_treasure_room=False):
        self.RoomNumber = room_number
        self.RoomDescription = description
        self.contents = contents or []
        self.enemy = enemy
        self.is_treasure_room = is_treasure_room
        self.enemy_defeated = False  # Track enemy defeat


# --- Room Map Layout ---
rooms_map = {
    1: Room(1, "🔥 Blast marks and dark stains litter the walls.", ["Mana Potion"]),
    2: Room(2, "🌺 A bare stone room. A clay golem lumbers silently across the far wall.", [], "Clay Golem"),
    3: Room(3, "💀 Corpses lie strangely positioned...", ["Sun Talisman"], "Hunting Horror"),
    4: Room(4, "🧪 Shattered shelves and ancient glassware clutter this collapsed storeroom.", ["Health Potion"]),
    5: Room(5, "📖 A broken warrior clutches a radiant tome.", ["Ornate Tome"], "Moon-Beast"),
    6: Room(6, "🦴 Bones crunch underfoot."),
    7: Room(7, "📜 A pedestal holds a crimson scroll.", ["Ancient Scroll"], "Shoggoth"),
    8: Room(8, "👹 A Lesser Spawn prowls here.", [], "Lesser Spawn"),
    9: Room(9, "🕯️ Dust and silence reign."),
    10: Room(10, "⚗️ Rusted cauldrons hint at alchemy.", ["Mana Potion"]),
    11: Room(11, "⚙️ A massive golem slumps against a wall.", [], "Clay Golem"),
    12: Room(12, "🧹 An abandoned lab.", ["Health Potion"]),
    13: Room(13, "🍃 This moss-covered hall feels... expectant."),
    14: Room(14, "🛡️ Rubble and broken armor litter this room.", [], "Clay Golem"),
    15: Room(15, "🔑 A brilliant Silver Key rests atop a pedestal.", ["Silver Key"]),
    16: Room(16, "🎨 Ancient murals line the walls."),
    17: Room(17, "👁️ Twisted Spawn pace this tight room.", [], "Lesser Spawn"),
    18: Room(18, "🏛️ A battered golem blocks this crossroads.", ["Health Potion"], "Clay Golem"),
    19: Room(19, "🌌 The silence here feels thick..."),
    20: Room(20, "👹 Another Spawn snarls from a doorway.", [], "Lesser Spawn"),
    21: Room(21, "📖 A cursed tome glows faintly.", ["Cursed Tome"], "Flying Polyp"),
    22: Room(22, "🪦 Dust motes swirl through this burial hall."),
    23: Room(23, "⚡ A rift tears open the floor!", ["Ancient Spellbook"], "Dimensional Shambler"),
    24: Room(24, "⚡ The floor cracks beneath your feet.", [], "Lesser Spawn"),
    25: Room(25, "🧹 A ruined alchemist's lab...", ["Health Potion"]),
    26: Room(26, Fore.RED + "💀 You stumble into the void..." + Fore.RESET, [], "Avatar of Nyarlathotep")
}

# Add dynamic treasure room logic
def spawn_treasure_room(battles_won, previous_room_ids):
    if battles_won < 3:
        return None
    eligible_rooms = [rid for rid in range(1, 26) if rid not in previous_room_ids and not rooms_map[rid].is_treasure_room and not rooms_map[rid].contents]
    if not eligible_rooms:
        return None
    chosen_id = random.choice(eligible_rooms)
    rooms_map[chosen_id].is_treasure_room = True
    loot_pool = [i.name for i in item_lookup.values() if not i.unique and i.item_type in ("healing", "mana", "attack")]
    random.shuffle(loot_pool)
    loot = loot_pool[:random.randint(2, 3)]
    rooms_map[chosen_id].contents = loot
    rooms_map[chosen_id].RoomDescription += "\n🏰 A gleam catches your eye. Something was left behind..."
    return chosen_id

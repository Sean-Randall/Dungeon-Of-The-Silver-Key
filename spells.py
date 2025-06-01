# spells.py

import random

class SimpleStrike:
    def __init__(self, name):
        self.name = name
        self.effect = None

def get_class_melee_spell(player_class):
    class_melee_options = {
        "Tank": [slash, thrust],
        "Occultist": [slash, thrust],
        "White Mage": [staff_tap],
        "Black Mage": [arcane_bash],
    }
    return random.choice(class_melee_options.get(player_class, [slash]))


class Spell:
    def __init__(self, name, cost, damage_range, category, allowed_classes, special=False, effect=None, is_aoe=False):
        self.name = name
        self.cost = cost
        self.damage_range = damage_range
        self.category = category  # 'damage', 'heal', 'special', 'melee', 'defense', 'debuff', 'boost'
        self.allowed_classes = allowed_classes
        self.special = special  # If True, it's a charged spell
        self.effect = effect
        self.is_aoe = is_aoe
        self.description_pool = self.generate_description_pool()

    def generate_description_pool(self):
        """Create vivid randomized descriptions based on type and name."""
        if self.name == "Thrust":
            return [
                f"{self.name} pierces forward with disciplined precision.",
                f"{self.name} is delivered with a knight’s poise and resolve.",
                f"{self.name} drives directly through the target's guard!"
            ]
        elif self.name == "Slash":
            return [
                f"{self.name} cleaves a wide arc across the foe’s defenses.",
                f"{self.name} is executed with force and flourish.",
                f"{self.name} carves through the enemy in a brutal display!"
            ]
        elif self.name == "Staff Tap":
            return [
                f"{self.name} lands with a surprising amount of force.",
                f"The base of the staff strikes true — a humble but effective {self.name}.",
                f"{self.name} thuds against the foe with ceremonial precision."
            ]
        elif self.name == "Arcane Bash":
            return [
                f"{self.name} reverberates with unstable magical force.",
                f"The staff hums as it collides — {self.name} releases a burst of latent energy.",
                f"A flash of eldritch power pulses from the impact of {self.name}."
            ]
        elif self.name == "Fireball":
            return [
                f"{self.name} explodes in a roar that echoes across dimensions.",
                f"Flames flicker with the screams of distant stars as {self.name} erupts.",
                f"A sphere of alien fire bursts forth, singing your mind as well as your flesh!"
            ]
        elif self.name == "Ice Spike":
            return [
                f"{self.name} impales with the chill of an ancient void.",
                f"Crystalline shards scream with forgotten frost as {self.name} strikes.",
                f"A shard of impossible cold rips through space toward its mark!"
            ]
        elif self.name == "Void Bolt":
            return [
                f"{self.name} tears through the air, unraveling reality at its edges.",
                f"A jagged bolt from the void shrieks as it twists toward its prey.",
                f"{self.name} hisses with entropy and shadow-stained memories."
            ]
        elif self.name == "Healing Light":
            return [
                f"{self.name} pours over wounds like light filtered through alien moons.",
                f"Your flesh knits with warmth drawn from ancient cosmic mercy.",
                f"A radiant touch calms both body and mind — though not quite your soul."
            ]
        elif self.name == "Sacred Rebuke":
            return [
                f"{self.name} scorches corruption with searing judgment.",
                f"A celestial outcry thunders through {self.name}, banishing the profane.",
                f"Your body jolts with agony and awe as {self.name} passes judgment!"
            ]
        elif self.name == "Greater Heal":
            return [
                f"A warmth beyond reason seeps into your bones via {self.name}.",
                f"{self.name} wraps you in cosmic grace, smoothing flesh and thought alike.",
                f"Time seems to pause as {self.name} rewinds your wounds."
            ]
        elif self.name == "Pure of Mind":
            return [
                f"A whisper of clarity washes away the madness — {self.name}.",
                f"With {self.name}, unseen fingers pluck the rot from your mind.",
                f"{self.name} silences the screaming void within."
            ]
        elif self.name == "Call of Madness":
            return [
                f"{self.name} floods the air with mind-shattering whispers.",
                f"A litany of the unspoken echoes as {self.name} is invoked.",
                f"Your thoughts twist like smoke as {self.name} takes hold."
            ]
        elif self.name == "Void Flame":
            return [
                f"{self.name} flickers with both heat and hunger.",
                f"A fire from between stars — {self.name} — devours your form and focus.",
                f"Black fire curls around you, whispering secrets as it burns."
            ]
        elif self.name == "Eldritch Flame":
            return [
                f"{self.name} burns with color not seen in this world.",
                f"Unholy fire dances in patterns that defy reason — {self.name} strikes.",
                f"The flames whisper names you were never meant to hear."
            ]
        elif self.name == "Guardian Shield":
            return [
                f"{self.name} wraps you in sigils older than memory.",
                f"A shimmering ward pulses with protective dread as {self.name} activates.",
                f"Alien glyphs spiral around you, forming the barrier known as {self.name}."
            ]
        elif self.name == "Sentinel's Oath":
            return [
                f"{self.name} stirs a forgotten vow buried deep in your soul.",
                f"An ancient voice calls you to guard those weaker — {self.name} is awakened.",
                f"You stand unmoved as reality screams, bound by {self.name}."
            ]
        elif self.name == "Veil of Silence":
            return [
                f"{self.name} cloaks the caster in a ward of absolute quiet.",
                f"An eerie stillness spreads — {self.name} seals thought and sound alike.",
                f"With {self.name}, the whispers of madness fall silent for a time."
            ]
        # ------------------------ Enemy Only Attacks ------------------------
        elif self.name == "Claw":
            return [
                f"{self.name} rips and shreds with feral intensity.",
                f"Claws flash through the air as {self.name} lands.",
                f"A savage {self.name} tears at your flesh!"
            ]
        elif self.name == "Bite":
            return [
                f"{self.name} crunches down with gnashing teeth.",
                f"Fangs sink deep as {self.name} strikes!",
                f"You feel bone crack beneath the {self.name}."
            ]
        elif self.name == "Tentacle Swipe":
            return [
                f"{self.name} lashes out with slick, writhing mass.",
                f"A sickening slap echoes as {self.name} connects.",
                f"You’re battered by the monstrous {self.name}."
            ]
        elif self.name == "Cosmic Wind":
            return [
                f"{self.name} howls with ancient energy.",
                f"Reality bends around the {self.name}.",
                f"The {self.name} tears through your defenses."
            ]
        elif self.name == "Cursed Blow":
            return [
                f"{self.name} lands with an aura of doom.",
                f"You stagger as the {self.name} resonates with evil.",
                f"Dark energies erupt from the {self.name}."
            ]
        elif self.name == "Engulf":
            return [
                f"{self.name} smothers you in viscous horror.",
                f"Slime surrounds your limbs as {self.name} binds you.",
                f"A consuming ooze envelopes you in {self.name}."
            ]
        elif self.name == "Pummel":
            return [
                f"{self.name} lands blow after brutal blow.",
                f"A flurry of strikes drives {self.name} home.",
                f"You’re caught in the storm of {self.name}."
            ]
        elif self.name == "Eviscerate":
            return [
                f"{self.name} tears you open with hideous glee.",
                f"Entrails spill as {self.name} bites deep.",
                f"The {self.name} leaves you gasping in agony."
            ]
        elif self.name == "Strangle":
            return [
                f"{self.name} closes tight around your throat.",
                f"Air flees your lungs as the {self.name} constricts.",
                f"Panic sets in as {self.name} cuts your breath short."
            ]
        elif self.name == "Dread Aura":
            return [
                f"A wave of despair washes over you from {self.name}.",
                f"Your sanity teeters as the {self.name} envelops you.",
                f"The presence of {self.name} gnaws at your mind."
            ]
        elif self.name == "Gaze of the Abyss":
            return [
                f"{self.name} paralyzes your soul with incomprehensible horror.",
                f"You lock eyes with eternity in {self.name}.",
                f"The void reflects your thoughts through {self.name}."
            ]
        elif self.name == "Hypnotic Gaze":
            return [
                f"Your thoughts blur as {self.name} captivates your mind.",
                f"The rhythm of {self.name} dulls your sense of self.",
                f"You drift into madness under {self.name}."
            ]
        elif self.name == "Smash":
            return [
                f"{self.name} crashes down like a meteor of muscle and stone.",
                f"The earth trembles beneath the force of {self.name}.",
                f"A thunderous {self.name} flattens anything in its path."
            ]
        elif self.name == "Stomp":
            return [
                f"{self.name} quakes the ground beneath your feet.",
                f"Dust and bone fly from the force of {self.name}.",
                f"You are knocked off balance by the quake of {self.name}."
            ]
        elif self.name == "Tear":
            return [
                f"{self.name} rends flesh from bone with savage glee.",
                f"A grotesque {self.name} opens wounds that should not be.",
                f"{self.name} leaves a trail of ruin and shrieks."
            ]
        elif self.name == "Snap":
            return [
                f"A jarring {self.name} echoes through the dungeon.",
                f"{self.name} snaps bone and resolve alike.",
                f"You wince as the {self.name} cracks through sinew."
            ]
        elif self.name == "Mutilate":
            return [
                f"{self.name} is a grotesque display of carnage.",
                f"A flurry of {self.name} leaves your body broken.",
                f"Pain blossoms as {self.name} hacks wildly."
            ]
        elif self.name == "Unnerving Aura":
            return [
                f"The {self.name} invades your thoughts with dread.",
                f"Terror clings to your spine under the {self.name}.",
                f"A cold sweat breaks as the {self.name} thickens."
            ]
        elif self.name == "Foul Affliction":
            return [
                f"{self.name} poisons your mind with cursed echoes.",
                f"A sickly haze forms around you from {self.name}.",
                f"{self.name} seeps into your brain like a noxious fog."
            ]
        elif self.name == "Horrific Wail":
            return [
                f"{self.name} shatters your thoughts with shrieking madness.",
                f"A chorus of screaming entities fills your ears — {self.name}!",
                f"Sanity tears asunder under the weight of the {self.name}."
            ]
        elif self.name == "Cosmic Vampirism":
            return [
                f"{self.name} drains life and sanity into the void.",
                f"You feel your essence siphoned by {self.name}.",
                f"A rift opens as {self.name} hungers for your soul."
            ]
        elif self.name == "Curse of the Stars":
            return [
                f"{self.name} pulls the light from your mind.",
                f"Starlight burns black in the wake of {self.name}.",
                f"{self.name} echoes from galaxies long dead."
            ]
        elif self.name == "Unsettling Gaze":
            return [
                f"{self.name} pierces your soul, and your skin begins to tear for no reason at all.",
                f"A malevolent force behind the {self.name} twists your flesh from within.",
                f"Your body recoils as {self.name} cuts without contact — a gaze that wounds."
            ]
        elif self.name == "Sanguine Pounce":
            return [
                f"{self.name} homes in on the scent of blood — a primal leap follows!",
                f"The creature howls and lunges, drawn to the bleeding wound.",
                f"{self.name} strikes savagely at exposed, torn flesh!"
            ]

        elif self.name == "Abyssal Grasp":
            return [
                f"{self.name} slithers through unseen dimensions and tugs at your consciousness.",
                f"You feel invisible fingers pierce your mind — {self.name} tightens with a dreadful will.",
                f"A chilling pressure drags your thoughts toward a yawning blackness — {self.name} has touched you."
            ]

        elif self.name == "Arcane Cataclysm":
            return [
                f"{self.name} rips through space-time with screaming geometry!",
                f"The dungeon cracks under the pressure of {self.name}.",
                f"{self.name} roars with the voice of a forgotten god."
            ]
        else:
            if self.category == "damage":
                return [
                    f"{self.name} pulses with destructive energy...",
                    f"Raw power surges from {self.name}.",
                    f"{self.name} tears through space and flesh alike."
                ]
            elif self.category == "heal":
                return [
                    f"{self.name} radiates a soothing light.",
                    f"Healing energy flows gently from {self.name}.",
                    f"{self.name} knits wounds and calms minds."
                ]
            elif self.category == "melee":
                return [
                    f"{self.name} strikes with raw force.",
                    f"{self.name} lands with a sickening crunch.",
                    f"A devastating blow — {self.name}."
                ]
            elif self.category == "defense":
                return [
                    f"{self.name} warps space around you into a shield.",
                    f"A ghostly ward of protection rises from {self.name}.",
                    f"The world hushes as {self.name} takes hold."
                ]
            elif self.category == "special":
                return [
                    f"{self.name} distorts fate itself with its invocation.",
                    f"Reality screams as {self.name} unfolds!",
                    f"A thousand eyes blink open within {self.name}."
                ]
            else:
                return [f"{self.name} echoes with unknowable power..."]

    def cast_description(self):
        return random.choice(self.description_pool)


# ------------------------ Melee Attacks ------------------------

slash = Spell("Slash", 0, (5, 15), "melee", ["Tank", "Occultist"])
thrust = Spell("Thrust", 0, (10, 20), "melee", ["Tank", "Occultist"])
staff_tap = Spell("Staff Tap", 0, (4, 10), "melee", ["White Mage"])
arcane_bash = Spell("Arcane Bash", 0, (6, 14), "melee", ["Black Mage"])

# ------------------------ Enemy Melee Attacks ------------------------

claw = Spell("Claw", 0, (20, 30), "melee", [], effect="bleed")
bite = Spell("Bite", 0, (20, 30), "melee", [], effect="bleed")
tentacle_swipe = Spell("Tentacle Swipe", 0, (30, 35), "melee", [])
cursed_blow = Spell("Cursed Blow", 0, (35, 40), "melee", [], effect="mindfire")
engulf = Spell("Engulf", 0, (30, 35), "melee", [])
pummel = Spell("Pummel", 0, (30, 35), "melee", [])
eviscerate = Spell("Eviscerate", 0, (30, 35), "melee", [], effect="bleed") # 🩸 Eviscerate — High bleed chance. Deals bonus damage to already bleeding targets.
strangle = Spell("Strangle", 0, (20, 30), "melee", [])
smash = Spell("Smash", 0, (30, 40), "melee", [])
stomp = Spell("Stomp", 0, (25, 35), "melee", [])
tear = Spell("Tear", 0, (25, 30), "melee", [], effect="bleed")
snap = Spell("Snap", 0, (20, 25), "melee", [])
mutilate = Spell("Mutilate", 0, (30, 40), "melee", [], effect="bleed")
abyssal_grasp = Spell("Abyssal Grasp", 0, (12, 18), "damage", [], effect="confusion")

# ------------------------ Enemy Magic/Mental Attacks ------------------------

cosmic_wind = Spell("Cosmic Wind", 0, (20, 30), "damage", [])
dread_aura = Spell("Dread Aura", 0, (10, 10), "debuff", [], effect="fear")
gaze_of_the_abyss = Spell("Gaze of the Abyss", 0, (30, 30), "debuff", [], effect="madness")
hypnotic_gaze = Spell("Hypnotic Gaze", 0, (10, 10), "debuff", [], effect="confusion")
unnerving_aura = Spell("Unnerving Aura", 10, (10, 20), "debuff", [], effect="fear")
foul_affliction = Spell("Foul Affliction", 12, (20, 30), "debuff", [], effect="madness")
horrific_wail = Spell("Horrific Wail", 15, (25, 35), "debuff", [], effect="madness", is_aoe=True)
cosmic_vampirism = Spell("Cosmic Vampirism", 15, (25, 40), "damage", []) # 🧛 Cosmic Vampirism — Drain effect: heals for 50% of damage dealt
curse_of_the_stars = Spell("Curse of the Stars", 20, (30, 45), "debuff", [], effect="madness", is_aoe=True) # Also reduces party's Sanity by 6-12

# ------------------------ Standard Spells ------------------------

fireball = Spell("Fireball", 10, (20, 30), "damage", ["Black Mage", "Occultist"], effect="mindfire")
ice_spike = Spell("Ice Spike", 10, (18, 28), "damage", ["Black Mage", "Occultist"])
void_bolt = Spell("Void Bolt", 12, (25, 35), "damage", ["Black Mage", "Occultist"], effect="random_mental")
healing_light = Spell("Healing Light", 8, (20, 30), "heal", ["White Mage", "Tank"])
sacred_rebuke = Spell("Sacred Rebuke", 20, (25, 40), "damage", ["White Mage"])

# ------------------------ Learned Spells ------------------------

greater_heal = Spell("Greater Heal", 15, (35, 50), "heal", ["White Mage"])
# "Veil of Silence: A ward of unearthly stillness that renders the caster immune to mental afflictions for 2 turns."
veil_of_silence = Spell("Veil of Silence", 12, (0, 0), "defense", ["White Mage"]) 
eldritch_flame = Spell("Eldritch Flame", 18, (30, 45), "damage", ["Occultist"], effect="mindfire")
pure_of_mind = Spell("Pure of Mind", 20, (0, 0), "heal", ["White Mage", "Occultist"])
call_of_madness = Spell("Call of Madness", 12, (25, 35), "debuff", ["Occultist"], effect="madness")
void_flame = Spell("Void Flame", 20, (40, 55), "damage", ["Black Mage", "Occultist"], effect="mindfire")

# ------------------------ Special Spell ------------------------

arcane_cataclysm = Spell("Arcane Cataclysm", 30, (70, 100), "special", [], special=True, is_aoe=True)
unsettling_gaze = Spell("Unsettling Gaze", 0, (30, 35), "damage", [], effect="bleed")
sanguine_pounce = Spell("Sanguine Pounce", 10, (25, 40), "damage", [])

# ------------------------ Defensive Spells ------------------------

guardian_shield = Spell("Guardian Shield", 8, (20, 30), "defense", ["Tank"])
sentinels_oath = Spell("Sentinel's Oath", 12, (0, 0), "defense", ["Tank"], special=True)

# ------------------------ Spell Lookup Registration ------------------------

all_spells = [
    fireball, ice_spike, void_bolt, healing_light, sacred_rebuke, veil_of_silence,
    greater_heal, eldritch_flame, pure_of_mind, call_of_madness, void_flame,
    arcane_cataclysm, guardian_shield, sentinels_oath, 
    slash, thrust, staff_tap, arcane_bash,
    claw, bite, tentacle_swipe, cosmic_wind, cursed_blow, engulf,
    pummel, eviscerate, strangle, dread_aura, gaze_of_the_abyss,
    hypnotic_gaze, smash, stomp, tear, snap, mutilate,
    unnerving_aura, foul_affliction, horrific_wail, abyssal_grasp,
    cosmic_vampirism, curse_of_the_stars, unsettling_gaze, sanguine_pounce
]

spell_lookup = {spell.name: spell for spell in all_spells}


# ======================== Future Spell Additions ========================
# These are planned or optional additions to expand spell variety and mechanics.

# -- Mental Status Spells --
# Delirium Veil: Debuff (confusion) – Creates phantom stimuli that disorient the mind.
# nightmare_pulse = Spell("Nightmare Pulse", 14, (20, 30), "damage", ["Occultist"], effect="fear")

# -- Elemental Horror Spells --
# howling_inferno = Spell("Howling Inferno", 16, (25, 40), "damage", ["Black Mage"], effect="mindfire", is_aoe=True)
# Glimpse Beyond: Debuff (random_mental) – Brief contact with unspeakable truths causes unpredictable affliction.
# glimpse_beyond = Spell("Glimpse Beyond", 14, (0, 0), "debuff", ["Occultist"], effect="random_mental")

# -- Defensive / Mental Resistance --
# Veil of Silence: Defense – Grants 2 turns of mental_resistance_turns to prevent mental afflictions.
# veil_of_silence = Spell("Veil of Silence", 10, (0, 0), "defense", ["White Mage", "Tank"])

# -- Advanced / Hybrid Effects --
# Siphon Sanity: Damage + Madness – Leech sanity and possibly convert it to a buff or heal.
# siphon_sanity = Spell("Siphon Sanity", 18, (20, 35), "damage", ["Occultist"], effect="madness")
# Ritual of Blood: Damage + Bleed – Bursts capillaries beneath the skin causing intense bleeding.
# ritual_of_blood = Spell("Ritual of Blood", 15, (25, 40), "damage", ["Occultist"], effect="bleed")

# Note: Full descriptions and combat logic may be needed before activation.
# 🔮 "Veil of Silence (Mass)" – A powerful, endgame-only AoE version with high MP cost or cooldown.
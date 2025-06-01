# Main.py
from colorama import Fore, Style
from pyfiglet import Figlet
from party_setup import setup_party
from dungeon_traverse import traverse_dungeon

def DisplayTitle():
    CustomTitle = Figlet(font='cyberlarge')
    CustomArt = """

     8 8 8 8                     ,ooo.
     8a8 8a8                    oP   ?b
    d888a888zzzzzzzzzzzzzzzzzzzz8     8b
     `""^""'                    ?o___oP'

    """
    Title = (CustomTitle.renderText("""DUNGEON OF THE SILVER KEY"""))
    print(Fore.YELLOW + Title)
    print(Fore.WHITE + CustomArt)

def intro_text():
    print(Fore.WHITE + """
The entrance to the dungeon is a large, menacing crevice. On the walls, the names and messages of those
who came before you are visible. You decide to leave a simple note, and leave your name among the hundreds
that challenged the dungeon before you.
""")

sanity_intro_text = """
🧠 SANITY SYSTEM ENABLED (Optional)

As you delve into the Dungeon of the Silver Key, your mind will be tested.
Every spell cast, horror faced, and affliction endured may chip away at your grasp on reality.
1
• Low sanity can cause your spells to misfire.
• It can induce hallucinations, confusion, fear, or even madness.
• Sanity loss is not always visible — inspecting often may reveal clues.

Would you like to enable visible SANITY tracking in your status bars?
Note: If you choose not to, you can still view your SANITY status in combat with "Inspect"
"""


def setup_game():
    players = setup_party()

    # 💠 Prompt to show SANITY in status bar
    print(Fore.MAGENTA + sanity_intro_text + Style.RESET_ALL)
    while True:
        track_sanity = input(Fore.LIGHTMAGENTA_EX + "Display sanity in party status bars? (Y/N): " + Style.RESET_ALL).strip().lower()
        if track_sanity in ["y", "n"]:
            show_sanity_bar = (track_sanity == "y")
            break
        else:
            print(Fore.YELLOW + "Please enter Y or N." + Style.RESET_ALL)

    print(Fore.CYAN + "\n🧠 OPTIONAL: Enable real-time overlay UI window?" + Style.RESET_ALL)
    while True:
        enable_overlay_input = input(Fore.LIGHTCYAN_EX + "Enable overlay? (Y/N): " + Style.RESET_ALL).strip().lower()
        if enable_overlay_input in ["y", "n"]:
            enable_overlay = (enable_overlay_input == "y")
            break
        else:
            print("Please enter Y or N.")

    for player in players:
        player.show_sanity_bar = show_sanity_bar  # Dynamically attach to each player

    while True:
        EnterTheDungeon = input(Fore.YELLOW + "\nYour mark has been left. Enter the dungeon? (Y/N): ").strip().lower()
        if EnterTheDungeon == "y":
            print(Fore.GREEN + "You steel your resolve and descend into the abyss.")
            break
        elif EnterTheDungeon == "n":
            print(Fore.RED + "\nYou think back to all those depending on you...")
            AreYouSure = input(Fore.YELLOW + "Let those who are counting on you down? (Y/N): ").strip().lower()
            if AreYouSure == "y":
                print(Fore.RED + "\nThis world has no room for cowards such as you.")
                print(Fore.RED + "You have been deemed unworthy. Perhaps the world will find a more suitable hero.")
                exit()
            elif AreYouSure == "n":
                print(Fore.GREEN + "\nThe thoughts of those who depend on you bolster your courage.")
                continue
        else:
            print(Fore.YELLOW + "\nPlease make a clear choice.")
    return players, enable_overlay, show_sanity_bar

def game_start(players, shared_inventory, overlay=None, enemies=None):
    print(Fore.YELLOW + "\nThe dungeon's cold breath greets you...\n")
    traverse_dungeon(players, shared_inventory, overlay, enemies)  # 🎯 Dungeon crawling system

if __name__ == "__main__":
    DisplayTitle()
    intro_text()
    players, enable_overlay, show_sanity_bar = setup_game()
    shared_inventory = []

    if enable_overlay:
        from overlay_ui import StatOverlay
        enemies = []  # Shared reference
        overlay = StatOverlay(players, enemies, show_sanity=show_sanity_bar)
    else:
        enemies = []
        overlay = None

    game_start(players, shared_inventory, overlay, enemies)

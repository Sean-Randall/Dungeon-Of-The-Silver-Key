# overlay_ui.py
import tkinter as tk

# Exact terminal-style color codes
HP_COLOR_PLAYER = "#00FF00"     # Bright green
HP_COLOR_ENEMY = "#FF0000"      # Bright red
MP_COLOR = "#0000FF"            # Bright blue
SAN_COLOR = "#FF00FF"           # Bright magenta
TEXT_COLOR = "#FFFFFF"          # Default white text

class StatOverlay:
    def __init__(self, party_ref, enemies_ref, show_sanity=False):
        self.party_ref = party_ref
        self.enemies_ref = enemies_ref
        self.show_sanity = show_sanity
        self.root = tk.Tk()
        self.root.title("Combat Status Overlay")
        self.root.configure(bg="black")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.party_labels = []
        self.enemy_labels = []

        # Title frames
        self.party_frame = tk.Frame(self.root, bg="black")
        self.party_frame.pack(padx=10, pady=10, anchor="nw")

        self.enemy_frame = tk.Frame(self.root, bg="black")
        self.enemy_frame.pack(padx=10, pady=10, anchor="nw")

        self.status_texts = {}
        self.schedule_update()
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def close_window(self):
        self.running = False
        self.root.destroy()

    def _render_bar(self, label, current, max_value, color, width=40):
        percent = current / max_value if max_value else 0
        fill_len = int(percent * width)
        bar = "█" * fill_len + "-" * (width - fill_len)
        return f"{label}: [{bar}] {current}/{max_value}"

    def _render_unit_block(self, unit, is_enemy=False):
        if unit.hp <= 0:
            name_color = "gray"
            bar_color = "gray"
        else:
            name_color = "white"
            bar_color = HP_COLOR_ENEMY if is_enemy else HP_COLOR_PLAYER

        job = getattr(unit, "job", "")
        class_icons = {
            "White Mage": "✨",
            "Black Mage": "🧙",
            "Tank": "🛡️",
            "Occultist": "🔮"
        }
        icon = class_icons.get(job, "")
        status = self._get_effect_icons(unit)
        defeated = " (Defeated)" if unit.hp <= 0 else ""
        name_text = f"{unit.name} the {job} {icon} {defeated} {status}".strip()

        output_lines = [
            (name_text, name_color),
            (self._render_bar("HP", unit.hp, unit.max_hp, bar_color, width=40), bar_color),
        ]

        if hasattr(unit, "mp"):
            mp_color = "gray" if unit.hp <= 0 else MP_COLOR
            output_lines.append((self._render_bar("MP", unit.mp, unit.max_mp, mp_color, width=30), mp_color))

        if self.show_sanity and hasattr(unit, "sanity"):
            san_color = "gray" if unit.hp <= 0 else SAN_COLOR
            output_lines.append((self._render_bar("SAN", unit.sanity, 100, san_color, width=30), san_color))

        return output_lines

    def _get_effect_icons(self, unit):
        icons = []

        if getattr(unit, 'is_bleeding', False):
            t = getattr(unit, 'bleeding_turns', 0)
            icons.append(f"🩸({t})" if t > 0 else "🩸")
        if getattr(unit, 'is_mindfired', False):
            t = getattr(unit, 'mindfire_turns', 0)
            icons.append(f"🔥({t})" if t > 0 else "🔥")
        if getattr(unit, 'is_confused', False):
            t = getattr(unit, 'confusion_turns', 0)
            icons.append(f"❓({t})" if t > 0 else "❓")
        if getattr(unit, 'is_feared', False):
            t = getattr(unit, 'fear_turns', 0)
            icons.append(f"😨({t})" if t > 0 else "😨")
        if getattr(unit, 'is_insane', False):
            t = getattr(unit, 'madness_turns', 0)
            icons.append(f"🧠({t})" if t > 0 else "🧠")
        if getattr(unit, 'is_stunned', False):
            t = getattr(unit, 'stun_turns', 0)
            icons.append(f"💫({t})" if t > 0 else "💫")
        if getattr(unit, 'mental_resistance_turns', 0) > 0:
            icons.append(f"🔰({unit.mental_resistance_turns})")

        return " ".join(icons)

    def schedule_update(self):
        self.update_display()
        self.root.after(500, self.schedule_update)

    def update_display(self):
        for widget in self.party_frame.winfo_children():
            widget.destroy()
        for widget in self.enemy_frame.winfo_children():
            widget.destroy()

        # === PARTY ===
        party_title = tk.Label(self.party_frame, text="👥 Party Status:", fg="white", bg="black", font=("Consolas", 14, "bold"))
        party_title.pack(anchor="w")

        for unit in self.party_ref:
            unit_block = self._render_unit_block(unit, is_enemy=False)
            for line, color in unit_block:
                label = tk.Label(self.party_frame, text=line, fg=color, bg="black", font=("Consolas", 14))
                label.pack(anchor="w")

        # === ENEMIES ===
        enemy_title = tk.Label(self.enemy_frame, text="\n👹 Enemy Status:", fg="red", bg="black", font=("Consolas", 14, "bold"))
        enemy_title.pack(anchor="w")

        if self.enemies_ref:
            for unit in self.enemies_ref:
                unit_block = self._render_unit_block(unit, is_enemy=True)
                for line, color in unit_block:
                    label = tk.Label(self.enemy_frame, text=line, fg=color, bg="black", font=("Consolas", 14))
                    label.pack(anchor="w")
        else:
            label = tk.Label(self.enemy_frame, text="(No enemies yet)", fg="gray", bg="black", font=("Consolas", 14, "bold"))
            label.pack(anchor="w")

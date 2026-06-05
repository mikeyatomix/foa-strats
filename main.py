import json
import os
import math
import random
from itertools import product

PRESETS_FILE  = "presets.json"
DRIVERS_FILE  = "drivers.json"

F1_POINTS = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]

DEFAULT_F1_ROSTER = [
    {"name": "Max Verstappen",     "team": "Red Bull",      "skill": 97},
    {"name": "Liam Lawson",        "team": "Red Bull",      "skill": 73},
    {"name": "Lewis Hamilton",     "team": "Ferrari",       "skill": 90},
    {"name": "Charles Leclerc",    "team": "Ferrari",       "skill": 88},
    {"name": "Lando Norris",       "team": "McLaren",       "skill": 89},
    {"name": "Oscar Piastri",      "team": "McLaren",       "skill": 84},
    {"name": "George Russell",     "team": "Mercedes",      "skill": 85},
    {"name": "Kimi Antonelli",     "team": "Mercedes",      "skill": 75},
    {"name": "Fernando Alonso",    "team": "Aston Martin",  "skill": 86},
    {"name": "Lance Stroll",       "team": "Aston Martin",  "skill": 68},
    {"name": "Pierre Gasly",       "team": "Alpine",        "skill": 76},
    {"name": "Jack Doohan",        "team": "Alpine",        "skill": 65},
    {"name": "Alex Albon",         "team": "Williams",      "skill": 78},
    {"name": "Carlos Sainz",       "team": "Williams",      "skill": 85},
    {"name": "Nico Hulkenberg",    "team": "Kick Sauber",   "skill": 77},
    {"name": "Gabriel Bortoleto",  "team": "Kick Sauber",   "skill": 67},
    {"name": "Yuki Tsunoda",       "team": "RB",            "skill": 76},
    {"name": "Isack Hadjar",       "team": "RB",            "skill": 68},
    {"name": "Esteban Ocon",       "team": "Haas",          "skill": 75},
    {"name": "Oliver Bearman",     "team": "Haas",          "skill": 71},
]


def load_presets():
    if os.path.exists(PRESETS_FILE):
        with open(PRESETS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_preset(name, race_laps, pit_loss, tyres, min_compounds, overtaking_difficulty, drs_zones):
    presets = load_presets()
    presets[name] = {
        "race_laps": race_laps,
        "pit_loss": pit_loss,
        "min_compounds": min_compounds,
        "tyres": tyres,
        "overtaking_difficulty": overtaking_difficulty,
        "drs_zones": drs_zones,
    }
    with open(PRESETS_FILE, "w") as f:
        json.dump(presets, f, indent=2)
    print(f"  Saved as '{name}'.")


def delete_preset(name):
    presets = load_presets()
    if name in presets:
        del presets[name]
        with open(PRESETS_FILE, "w") as f:
            json.dump(presets, f, indent=2)
        print(f"  '{name}' deleted.")
    else:
        print(f"  No preset named '{name}'.")


def pick_preset():
    presets = load_presets()
    if not presets:
        return None

    names = list(presets.keys())
    print("\n  Saved tracks:")
    for i, name in enumerate(names, 1):
        p = presets[name]
        tyre_list = ", ".join(p["tyres"].keys())
        ot = p.get("overtaking_difficulty", "medium").upper()
        drs_z = p.get("drs_zones", 1 if p.get("drs_active", True) else 0)
        drs_str = f"DRS ✗" if drs_z == 0 else f"DRS ×{drs_z} ({drs_z * 0.5:.1f}s/lap)"
        print(f"  [{i}] {name}  ({p['race_laps']} laps, {len(p['tyres'])} compounds: {tyre_list})  |  OT: {ot}  {drs_str}")
    print(f"  [{len(names) + 1}] Enter new track")

    choice = get_int(f"Choose [1-{len(names) + 1}]: ", min_val=1, max_val=len(names) + 1)
    if choice == len(names) + 1:
        return None
    return presets[names[choice - 1]]


# ──────────────────────────────────────────────────────────────────────────────
# DRIVER DATABASE  (drivers.json)
# ──────────────────────────────────────────────────────────────────────────────

def load_saved_drivers():
    if os.path.exists(DRIVERS_FILE):
        data = json.load(open(DRIVERS_FILE)) if os.path.getsize(DRIVERS_FILE) > 2 else {}
        return data.get("drivers", [])
    # First run — seed with the default F1 2025 roster
    save_saved_drivers(list(DEFAULT_F1_ROSTER))
    return list(DEFAULT_F1_ROSTER)


def save_saved_drivers(drivers_list):
    with open(DRIVERS_FILE, "w") as f:
        json.dump({"drivers": drivers_list}, f, indent=2)


def manage_driver_database():
    """Interactive menu: view, add (single or bulk), edit skill, remove."""
    while True:
        saved = load_saved_drivers()
        print("\n" + "=" * 60)
        print("              DRIVER DATABASE")
        print("=" * 60)
        if saved:
            print(f"  {'#':<4} {'Driver':<24} {'Team':<20} {'Skill':<7} {'Rating'}")
            print(f"  {'-'*4} {'-'*24} {'-'*20} {'-'*7} {'-'*12}")
            for i, d in enumerate(saved, 1):
                print(f"  {i:<4} {d['name']:<24} {d.get('team','—'):<20} {d['skill']:<7} {skill_label(d['skill'])}")
        else:
            print("  No drivers saved yet.")
        print()
        print("  [1] Add driver")
        print("  [2] Bulk add  (enter many drivers quickly)")
        print("  [3] Edit driver skill")
        print("  [4] Remove driver")
        print("  [5] Reset to default F1 2025 roster")
        print("  [6] Done")

        choice = input("  Choose: ").strip()

        if choice == "1":
            name = input("  Name: ").strip()
            if not name:
                print("  Name cannot be empty.")
                continue
            if any(d["name"].lower() == name.lower() for d in saved):
                print("  Driver already exists.")
                continue
            team  = input("  Team (leave blank = Independent): ").strip() or "Independent"
            skill = get_int("  Skill [0-100]: ", min_val=0, max_val=100)
            saved.append({"name": name, "team": team, "skill": skill})
            save_saved_drivers(saved)
            print(f"  Added {name}  ({skill_label(skill)}).")

        elif choice == "2":
            print("  Enter one driver per line as:  Name, Team, Skill")
            print("  (e.g.  Max Verstappen, Red Bull, 97)")
            print("  Type 'done' when finished.\n")
            added = 0
            existing_names = {d["name"].lower() for d in saved}
            while True:
                line = input("  > ").strip()
                if line.lower() == "done":
                    break
                parts = [p.strip() for p in line.split(",")]
                if len(parts) != 3:
                    print("  Need exactly 3 fields: Name, Team, Skill")
                    continue
                name, team, skill_str = parts
                if not name:
                    print("  Name cannot be empty.")
                    continue
                if name.lower() in existing_names:
                    print(f"  {name} already exists — skipping.")
                    continue
                try:
                    skill = int(skill_str)
                    if not (0 <= skill <= 100):
                        raise ValueError
                except ValueError:
                    print("  Skill must be a number 0–100.")
                    continue
                saved.append({"name": name, "team": team, "skill": skill})
                existing_names.add(name.lower())
                added += 1
                print(f"  ✓ {name}  ({team})  {skill_label(skill)}")
            save_saved_drivers(saved)
            print(f"  Saved {added} new driver(s).")

        elif choice == "3":
            if not saved:
                print("  No drivers to edit.")
                continue
            idx = get_int(f"  Edit driver # [1-{len(saved)}]: ", min_val=1, max_val=len(saved))
            d = saved[idx - 1]
            print(f"  {d['name']}  current skill: {d['skill']}  ({skill_label(d['skill'])})")
            d["skill"] = get_int("  New skill [0-100]: ", min_val=0, max_val=100)
            save_saved_drivers(saved)
            print(f"  Updated to {d['skill']}  ({skill_label(d['skill'])}).")

        elif choice == "4":
            if not saved:
                print("  No drivers to remove.")
                continue
            idx = get_int(f"  Remove driver # [1-{len(saved)}]: ", min_val=1, max_val=len(saved))
            removed = saved.pop(idx - 1)
            save_saved_drivers(saved)
            print(f"  Removed {removed['name']}.")

        elif choice == "5":
            if get_yes_no("  This will replace ALL drivers with the default F1 2025 roster. Continue? [y/n]: "):
                save_saved_drivers(list(DEFAULT_F1_ROSTER))
                print("  Roster reset to F1 2025 defaults (20 drivers).")

        elif choice == "6":
            break


def select_session_drivers(max_drivers=20):
    """
    Build the driver lineup for a session.
    Returns a list of dicts: {name, team, skill}.
    """
    saved = load_saved_drivers()
    session = []
    used_names = []

    print("\n  Driver lineup source:")
    print("  [1] Load ALL saved drivers")
    print("  [2] Pick from saved drivers")
    print("  [3] Enter manually")
    while True:
        c = input("  Choose [1-3]: ").strip()
        if c in ("1", "2", "3"):
            break
        print("  Please enter 1, 2, or 3.")

    if c == "1":
        if not saved:
            print("  No saved drivers — switching to manual.")
            c = "3"
        else:
            for d in saved[:max_drivers]:
                session.append(dict(d))
                used_names.append(d["name"])
            print(f"  Loaded {len(session)} driver(s).")

    if c == "2":
        if not saved:
            print("  No saved drivers — switching to manual.")
            c = "3"
        else:
            print("\n  Saved drivers:")
            for i, d in enumerate(saved, 1):
                print(f"    [{i:>2}] {d['name']:<24} {d.get('team',''):<20} Skill {d['skill']}")
            print("  Enter numbers separated by commas (e.g. 1,3,5):")
            while True:
                raw = input("  > ").strip()
                try:
                    indices = [int(x.strip()) for x in raw.split(",")]
                    if len(indices) < 2 or not all(1 <= i <= len(saved) for i in indices):
                        raise ValueError
                    for i in indices:
                        d = saved[i - 1]
                        if d["name"] not in used_names and len(session) < max_drivers:
                            session.append(dict(d))
                            used_names.append(d["name"])
                    break
                except ValueError:
                    print(f"  Pick at least 2 numbers between 1 and {len(saved)}.")

    if c == "3":
        num = get_int("  How many drivers? [2-20]: ", min_val=2, max_val=max_drivers)
        for i in range(1, num + 1):
            print(f"\n  ── Driver {i} ──")
            while True:
                name = input("  Name: ").strip()
                if not name:
                    print("  Name cannot be empty.")
                elif name in used_names:
                    print("  Name already used.")
                else:
                    break
            used_names.append(name)
            team  = input("  Team (optional): ").strip() or "Independent"
            skill = get_int("  Skill [0-100]: ", min_val=0, max_val=100)
            print(f"  → {skill_label(skill)}  ({-skill_adjustment(skill):+.3f}s/lap vs baseline)")
            session.append({"name": name, "team": team, "skill": skill})

        if get_yes_no("  Save these drivers to the database? [y/n]: "):
            existing = load_saved_drivers()
            ex_names = {d["name"].lower() for d in existing}
            added = 0
            for d in session:
                if d["name"].lower() not in ex_names:
                    existing.append(d)
                    added += 1
            save_saved_drivers(existing)
            print(f"  Saved {added} new driver(s).")

    return session


def get_int(prompt, min_val=1, max_val=None):
    while True:
        try:
            value = int(input(prompt))
            if value < min_val:
                print(f"Please enter a number of at least {min_val}.")
            elif max_val is not None and value > max_val:
                print(f"Please enter a number no greater than {max_val}.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")


def get_float(prompt, min_val=0):
    while True:
        try:
            value = float(input(prompt))
            if value < min_val:
                print(f"Please enter a number of at least {min_val}.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a number.")


PRESET_COMPOUNDS = ["Ultra Soft", "Soft", "Medium", "Hard", "Ultra Hard"]


def select_compounds(num_tyres):
    if num_tyres == len(PRESET_COMPOUNDS):
        selected = PRESET_COMPOUNDS[:]
        print(f"\nCompounds: {', '.join(selected)}")
        return selected

    print("\nAvailable compounds:")
    for i, name in enumerate(PRESET_COMPOUNDS, 1):
        print(f"  [{i}] {name}")

    selected = []
    while len(selected) < num_tyres:
        prompt = f"Select compound {len(selected) + 1} of {num_tyres} [1-{len(PRESET_COMPOUNDS)}]: "
        while True:
            try:
                choice = int(input(prompt))
                if not (1 <= choice <= len(PRESET_COMPOUNDS)):
                    print(f"Please enter a number between 1 and {len(PRESET_COMPOUNDS)}.")
                elif PRESET_COMPOUNDS[choice - 1] in selected:
                    print("That compound is already selected.")
                else:
                    selected.append(PRESET_COMPOUNDS[choice - 1])
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")

    return selected


def get_yes_no(prompt):
    while True:
        choice = input(prompt).strip().lower()
        if choice in ("y", "n"):
            return choice == "y"
        print("Please enter y or n.")


def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs}h {mins:02d}m {secs:05.2f}s"
    return f"{mins}m {secs:05.2f}s"


def format_gap(seconds):
    if seconds == 0:
        return "LEADER"
    return f"+{seconds:.3f}s"


def effective_pit_loss(pit_lap, normal_pit_loss, sc):
    if sc and sc["start"] <= pit_lap <= sc["end"]:
        return sc["pit_loss"]
    return normal_pit_loss


def greedy_split(sub_seq, target_laps, tyres):
    n = len(sub_seq)
    if n == 0 or target_laps < n:
        return None
    max_l = [tyres[t]["max_laps"] for t in sub_seq]
    if sum(max_l) < target_laps:
        return None
    laps = [1] * n
    remaining = target_laps - n
    for idx in sorted(range(n), key=lambda i: tyres[sub_seq[i]]["pace"]):
        add = min(max_l[idx] - 1, remaining)
        laps[idx] += add
        remaining -= add
        if remaining == 0:
            break
    return laps if remaining == 0 else None


def build_strategy(seq, laps_list, pit_loss, sc, tyres):
    pit_laps = []
    cum = 0
    total_time = 0
    for i, (tyre, laps) in enumerate(zip(seq, laps_list)):
        total_time += laps * tyres[tyre]["pace"]
        cum += laps
        if i < len(seq) - 1:
            pit_laps.append(cum)
            total_time += effective_pit_loss(cum, pit_loss, sc)
    return total_time, tuple(laps_list), tuple(pit_laps)


def find_best_strategies(race_laps, pit_loss, tyres, min_compounds, sc=None, top_n=5):
    tyre_names = list(tyres.keys())
    max_stints = min(4, race_laps, len(tyre_names) * 2)
    candidates = []

    for n_stints in range(min_compounds, max_stints + 1):
        for seq in product(tyre_names, repeat=n_stints):
            if len(set(seq)) < min_compounds:
                continue

            laps = greedy_split(seq, race_laps, tyres)
            if laps:
                t, l, pl = build_strategy(seq, laps, pit_loss, sc, tyres)
                candidates.append((t, seq, l, pl))

            if sc:
                for pit_idx in range(n_stints - 1):
                    for sc_lap in range(sc["start"], sc["end"] + 1):
                        pre = greedy_split(seq[:pit_idx + 1], sc_lap, tyres)
                        post = greedy_split(seq[pit_idx + 1:], race_laps - sc_lap, tyres)
                        if pre and post:
                            all_laps = pre + post
                            t, l, pl = build_strategy(seq, all_laps, pit_loss, sc, tyres)
                            candidates.append((t, seq, l, pl))

    seen = set()
    unique = []
    for t, seq, laps, pit_laps in sorted(candidates, key=lambda x: x[0]):
        key = (seq, laps)
        if key not in seen:
            seen.add(key)
            unique.append((t, seq, list(laps), pit_laps))
        if len(unique) == top_n:
            break

    return unique


ABBREV = {
    "Ultra Soft": "US",
    "Soft": "S",
    "Medium": "M",
    "Hard": "H",
    "Ultra Hard": "UH",
}


def strategy_summary(seq, laps):
    parts = [f"{tyre} ({lap_count}L)" for tyre, lap_count in zip(seq, laps)]
    return " → ".join(parts)


def strategy_short(seq, laps):
    parts = [f"{ABBREV.get(tyre, tyre)}({lap_count})" for tyre, lap_count in zip(seq, laps)]
    return " → ".join(parts)


def display_strategies(strategies, tyres, pit_loss, sc=None):
    if not strategies:
        print("\nNo valid strategies found with the given constraints.")
        return

    best_time, best_seq, best_laps, best_pit_laps = strategies[0]
    pit_str = ", ".join(f"lap {pl}" for pl in best_pit_laps) if best_pit_laps else "none"
    n_pits = len(best_pit_laps)

    print("\n" + "=" * 55)
    if sc:
        print(f"  Safety car: laps {sc['start']}–{sc['end']}  |  SC pit loss: {sc['pit_loss']}s")
        print("-" * 55)

    print("  ★  RECOMMENDED STRATEGY")
    print("-" * 55)
    print(f"  Route  :  {strategy_summary(best_seq, best_laps)}")
    print(f"  Time   :  {best_time:.2f}s  ({format_time(best_time)})")
    print(f"  Stops  :  {n_pits}  —  pit on {pit_str}")

    for i, (tyre, lap_count) in enumerate(zip(best_seq, best_laps), 1):
        if i <= n_pits:
            pit_lap = best_pit_laps[i - 1]
            pl = effective_pit_loss(pit_lap, pit_loss, sc)
            sc_tag = " [SC!]" if sc and sc["start"] <= pit_lap <= sc["end"] else ""
            after = f"pit lap {pit_lap}  ({pl:.1f}s loss{sc_tag})"
        else:
            after = "finish"
        print(f"         Stint {i}: {tyre}  {lap_count} laps  →  {after}")

    if len(strategies) > 1:
        print("\n" + "-" * 55)
        print("  Other options:")
        print("-" * 55)
        for rank, (total_time, seq, laps, pit_laps) in enumerate(strategies[1:], 2):
            gap = total_time - best_time
            pl_str = ", ".join(f"lap {pl}" for pl in pit_laps) if pit_laps else "none"
            sc_pits = sum(1 for pl in pit_laps if sc and sc["start"] <= pl <= sc["end"])
            sc_note = f"  ({sc_pits} SC pit{'s' if sc_pits > 1 else ''})" if sc_pits else ""
            print(f"  #{rank}  {strategy_short(seq, laps)}")
            print(f"       {total_time:.2f}s  (+{gap:.2f}s)  |  pits: {pl_str}{sc_note}")

    print("=" * 55)


def compare_drivers(strategies, tyres, pit_loss, sc=None):
    if not strategies:
        print("No strategies available to assign.")
        return

    print("\n" + "=" * 55)
    print("        DRIVER STRATEGY COMPARISON")
    print("=" * 55)

    num_drivers = get_int("Number of drivers to compare: ", min_val=2)
    driver_results = []
    used_names = []

    for i in range(num_drivers):
        print(f"\n--- Driver {i + 1} ---")
        while True:
            name = input("Driver name: ").strip()
            if not name:
                print("Name cannot be empty.")
            elif name in used_names:
                print("That driver name is already used.")
            else:
                break
        used_names.append(name)

        print("Available strategies:")
        for rank, (total_time, seq, laps, pit_laps) in enumerate(strategies, 1):
            sc_note = ""
            if sc:
                sc_pits = sum(1 for pl in pit_laps if sc["start"] <= pl <= sc["end"])
                if sc_pits:
                    sc_note = f"  [{sc_pits} SC pit{'s' if sc_pits > 1 else ''}]"
            print(f"  [{rank}] {strategy_summary(seq, laps)}  —  {format_time(total_time)}{sc_note}")

        while True:
            try:
                choice = int(input(f"Strategy for {name} [1-{len(strategies)}]: "))
                if 1 <= choice <= len(strategies):
                    break
                print(f"Please enter a number between 1 and {len(strategies)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        total_time, seq, laps, pit_laps = strategies[choice - 1]
        driver_results.append({
            "name": name, "strategy_num": choice, "total_time": total_time,
            "seq": seq, "laps": laps, "pit_laps": pit_laps, "pits": len(pit_laps),
        })

    driver_results.sort(key=lambda d: d["total_time"])
    leader_time = driver_results[0]["total_time"]

    print("\n" + "=" * 55)
    print("              RACE RESULT")
    print("=" * 55)
    print(f"  {'Pos':<4} {'Driver':<20} {'Strat':<6} {'Pits':<6} {'Time':<16} {'Gap'}")
    print(f"  {'-'*4} {'-'*20} {'-'*6} {'-'*6} {'-'*16} {'-'*10}")

    for pos, d in enumerate(driver_results, 1):
        gap = d["total_time"] - leader_time
        print(f"  {pos:<4} {d['name']:<20} #{d['strategy_num']:<5} {d['pits']:<6} {format_time(d['total_time']):<16} {format_gap(gap)}")

    print()
    print("  Stint breakdown:")
    for d in driver_results:
        print(f"\n  {d['name']} — Strategy #{d['strategy_num']}")
        n_pits = len(d["pit_laps"])
        for j, (tyre, lap_count) in enumerate(zip(d["seq"], d["laps"]), 1):
            stint_time = lap_count * tyres[tyre]["pace"]
            if j <= n_pits:
                pit_lap = d["pit_laps"][j - 1]
                pl = effective_pit_loss(pit_lap, pit_loss, sc)
                sc_tag = "  ← SC pit!" if sc and sc["start"] <= pit_lap <= sc["end"] else ""
                pit_info = f"  [pit lap {pit_lap}, loss {pl:.1f}s{sc_tag}]"
            else:
                pit_info = ""
            print(f"    Stint {j}: {tyre} — {lap_count} laps ({format_time(stint_time)}){pit_info}")

    print("\n" + "=" * 55)
    print(f"  Winner: {driver_results[0]['name']}!")
    print("=" * 55)


# ──────────────────────────────────────────────────────────────────────────────
# DRIVER SKILL SYSTEM
# ──────────────────────────────────────────────────────────────────────────────
# Skill scale: 0–100.  Baseline is 50 (neutral).
# A skill-100 driver is 0.300 s/lap FASTER than the baseline.
# A skill-0  driver is 0.300 s/lap SLOWER  than the baseline.
# The curve is a power-1.5 so that the penalty for low skill is steeper
# than the reward for high skill (slower drivers bleed more time).
# Formula (returns seconds to ADD to base pace; negative = faster):
#   adjustment = -sign(skill-50) * |skill-50|^1.5 / 50^1.5 * 0.3

def skill_adjustment(skill):
    """
    Returns seconds to add to base lap pace for this skill level.
    Negative  → driver is faster than baseline.
    Positive  → driver is slower  than baseline.
    The power-curve means low-skilled drivers lose disproportionately
    more time compared to what high-skilled drivers gain.
    """
    normalized = (skill - 50) / 50          # -1 at skill=0 … +1 at skill=100
    curved = math.copysign(abs(normalized) ** 1.5, normalized)
    return -curved * 0.3                    # invert: high skill → negative (faster)


def skill_label(skill):
    if skill >= 85:
        return "Elite"
    elif skill >= 70:
        return "Strong"
    elif skill >= 55:
        return "Above avg"
    elif skill >= 45:
        return "Average"
    elif skill >= 30:
        return "Below avg"
    else:
        return "Struggling"


# ──────────────────────────────────────────────────────────────────────────────
# QUALIFYING SIMULATOR
# ──────────────────────────────────────────────────────────────────────────────

def qualifying_lap_time(compound_pace, skill, track_evolution=0.0):
    """
    Simulate a single hot lap.
    track_evolution: cumulative grip improvement from rubber laid down (grows each lap).
    Noise is one-directional (mistakes add time; you can't beat the theoretical limit).
    σ shrinks with skill — elite drivers are near-perfect every lap.
    """
    base  = compound_pace + skill_adjustment(skill) - track_evolution
    sigma = (100 - skill) / 300      # skill=100 → σ≈0, skill=50 → σ≈0.17, skill=0 → σ≈0.33
    noise = abs(random.gauss(0, sigma))
    return max(base, base + noise)   # never faster than theoretical best


def qualifying_sim(tyres, strategies, pre_selected_drivers=None):
    """
    Run a full qualifying session.
    - Each driver gets 3 timed laps and picks any compound per attempt.
    - Track evolves (+0.02 s of grip per lap laid down globally).
    - Grid order = fastest qualifying time.
    - Starting tyre locked to the compound of the driver's personal best lap.
    - Strategies are filtered to those starting on that compound.
    - pre_selected_drivers: if provided, skip driver selection menu.

    Returns a list of dicts sorted P1→Pn:
        {name, team, skill, q_time, q_tyre, valid_strategies}
    """
    W = 60
    EVOLUTION_PER_LAP = 0.02

    print("\n" + "=" * W)
    print("              QUALIFYING SESSION")
    print("=" * W)

    tyre_names  = list(tyres.keys())
    if pre_selected_drivers is not None:
        session_drv = pre_selected_drivers
    else:
        session_drv = select_session_drivers(max_drivers=20)

    print(f"\n  {len(session_drv)} driver(s) — 3 timed laps each.")
    print("  Track rubber improves conditions by 0.02 s per lap laid down.\n")

    track_evolution = 0.0
    results = []

    for d in session_drv:
        print(f"  ── {d['name']:<24} {d.get('team',''):<20} Skill: {d['skill']} "
              f"({skill_label(d['skill'])}) ──")
        best_time = None
        best_tyre = None

        for attempt in range(1, 4):
            print(f"    Attempt {attempt}  (track evo: −{track_evolution:.3f}s)")
            for i, t in enumerate(tyre_names, 1):
                print(f"      [{i}] {t}  (base {tyres[t]['pace']}s/lap)")
            while True:
                try:
                    c = int(input(f"    Compound [1-{len(tyre_names)}]: "))
                    if 1 <= c <= len(tyre_names):
                        break
                    print(f"    Enter 1–{len(tyre_names)}.")
                except ValueError:
                    print("    Enter a number.")
            compound = tyre_names[c - 1]
            lap_t    = qualifying_lap_time(tyres[compound]["pace"], d["skill"], track_evolution)
            track_evolution += EVOLUTION_PER_LAP
            marker = ""
            if best_time is None or lap_t < best_time:
                best_time = lap_t
                best_tyre = compound
                marker = "  ★ personal best"
            print(f"    → {format_time(lap_t)}  [{compound}]{marker}")

        # Strategies valid for this driver = start on their qualifying tyre
        valid = [s for s in strategies if s[1][0] == best_tyre]
        if not valid:
            # No exact match — allow any (happens when qualifying tyre isn't in strategies)
            valid = list(strategies)
            note = "(no strategy starts on qualifying tyre — all strategies available)"
        else:
            note = f"({len(valid)} strateg{'y' if len(valid)==1 else 'ies'} start on {best_tyre})"
        print(f"  Best: {format_time(best_time)} on {best_tyre}  {note}\n")

        results.append({
            "name":              d["name"],
            "team":              d.get("team", ""),
            "skill":             d["skill"],
            "q_time":            best_time,
            "q_tyre":            best_tyre,
            "valid_strategies":  valid,
        })

    # Sort by qualifying time
    results.sort(key=lambda r: r["q_time"])
    pole_time = results[0]["q_time"]

    print("=" * W)
    print("           QUALIFYING CLASSIFICATION")
    print("=" * W)
    print(f"  {'P':<4} {'Driver':<24} {'Team':<18} {'Time':<14} {'Gap':<12} {'Tyre'}")
    print(f"  {'-'*4} {'-'*24} {'-'*18} {'-'*14} {'-'*12} {'-'*12}")
    for pos, r in enumerate(results, 1):
        gap     = r["q_time"] - pole_time
        gap_str = "POLE" if pos == 1 else f"+{gap:.3f}s"
        print(f"  P{pos:<3} {r['name']:<24} {r['team']:<18} "
              f"{format_time(r['q_time']):<14} {gap_str:<12} {r['q_tyre']}")
    print("=" * W)

    return results


# ──────────────────────────────────────────────────────────────────────────────
# OVERTAKE PROBABILITY
# ──────────────────────────────────────────────────────────────────────────────

TYRE_ORDER = {
    "Ultra Soft": 0,
    "Soft":       1,
    "Medium":     2,
    "Hard":       3,
    "Ultra Hard": 4,
}


def current_tyre(seq, laps, lap):
    """Return which compound is on at a given race lap."""
    total = 0
    for tyre, stint_laps in zip(seq, laps):
        total += stint_laps
        if lap <= total:
            return tyre
    return seq[-1]


def overtake_probability(attacker_tyre, defender_tyre, gap,
                         attacker_skill, defender_skill,
                         overtaking_difficulty, drs_zones):
    """
    Single-attempt probability that the attacker makes a clean pass.
    Called up to 3 times per lap (per lap section: early, mid, late).
    Factors:
      - Tyre compound advantage of attacker over defender
      - Raw gap between cars (must be close enough to attempt)
      - DRS boost when gap <= 1.0 s (scales with number of DRS zones)
      - Driver skill delta (positive = attacker is better)
      - Defender skill bonus (a skilled defender resists more)
      - Track overtaking difficulty modifier
    """
    # No realistic attempt if gap is too large
    if gap > 2.0:
        return 0.0

    # Base probability from tyre advantage
    tyre_diff = TYRE_ORDER.get(defender_tyre, 2) - TYRE_ORDER.get(attacker_tyre, 2)
    if tyre_diff <= 0:
        base = 0.20
    elif tyre_diff == 1:
        base = 0.45
    elif tyre_diff == 2:
        base = 0.65
    elif tyre_diff == 3:
        base = 0.80
    else:
        base = 0.92

    # Gap penalty: probability fades as gap grows toward 2.0 s
    gap_factor = 1.0 - (gap / 2.0) * 0.5
    prob = base * gap_factor

    # DRS boost — 0.09 per zone when within 1.0 s (1 zone ≈ +9%, 2 zones ≈ +18%)
    if drs_zones > 0 and gap <= 1.0:
        prob += drs_zones * 0.09

    # Skill delta — each point of skill difference shifts prob by 0.35 %
    skill_delta = attacker_skill - defender_skill
    prob += skill_delta * 0.0035

    # Defender bonus — a skilled defender resists overtakes extra
    # (0.20 % per point by which defender outskills the attacker)
    defend_edge = defender_skill - attacker_skill
    if defend_edge > 0:
        prob -= defend_edge * 0.002

    # Track difficulty modifier
    if overtaking_difficulty == "easy":
        prob *= 1.20
    elif overtaking_difficulty == "hard":
        prob *= 0.70

    return max(0.02, min(0.97, prob))


# ──────────────────────────────────────────────────────────────────────────────
# UNDERCUT / OVERCUT SIMULATOR  (with driver skill + 3-attempt overtaking)
# ──────────────────────────────────────────────────────────────────────────────

def undercut_overcut_sim(strategies, tyres, pit_loss, sc, race_laps,
                         overtaking_difficulty, drs_zones):
    print("\n" + "=" * 55)
    print("      UNDERCUT / OVERCUT SIMULATOR")
    print("=" * 55)
    print("Driver 1 = Leader (ahead), Driver 2 = Chaser (behind)")
    ot_label = overtaking_difficulty.upper()
    if drs_zones == 0:
        drs_label = "OFF"
    else:
        drs_label = f"{drs_zones} zone{'s' if drs_zones > 1 else ''}  (+{drs_zones * 0.5:.1f}s/lap when within 1.0 s)"
    print(f"Track:  Overtaking {ot_label}  |  DRS {drs_label}")
    print()

    tyre_names = list(tyres.keys())

    def _build_custom_strategy():
        """Interactively build a custom stint plan. Returns (seq, laps, pit_laps)."""
        print("\n  Custom strategy builder:")
        print("  Available compounds:")
        for i, t in enumerate(tyre_names, 1):
            print(f"    [{i}] {t}  (pace {tyres[t]['pace']}s/lap, max {tyres[t]['max_laps']} laps)")
        while True:
            num_stints = get_int("  How many stints? ", min_val=1, max_val=race_laps)
            seq, laps_list, total = [], [], 0
            ok = True
            for i in range(num_stints):
                remaining = race_laps - total - (num_stints - i - 1)
                c = get_int(f"  Stint {i+1} compound [1-{len(tyre_names)}]: ",
                            min_val=1, max_val=len(tyre_names))
                tname = tyre_names[c - 1]
                max_this = min(tyres[tname]["max_laps"], remaining)
                if i == num_stints - 1:
                    lap_count = remaining
                    print(f"    Laps: {lap_count} (remaining)")
                else:
                    lap_count = get_int(f"    Laps [1-{max_this}]: ", min_val=1, max_val=max_this)
                seq.append(tname)
                laps_list.append(lap_count)
                total += lap_count
            if total != race_laps:
                print(f"  Stints cover {total}/{race_laps} laps — try again.")
                continue
            pit_laps_out, cum = [], 0
            total_t = 0.0
            for i, (t, lc) in enumerate(zip(seq, laps_list)):
                total_t += lc * tyres[t]["pace"]
                cum += lc
                if i < len(seq) - 1:
                    pit_laps_out.append(cum)
                    total_t += pit_loss
            print(f"  Custom strategy: {strategy_summary(seq, laps_list)}  —  {total_t:.2f}s")
            return seq, laps_list, pit_laps_out

    # ── Strategy selection ──
    print("Available strategies:")
    for rank, (total_time, seq, laps, pit_laps) in enumerate(strategies, 1):
        print(f"  [{rank}] {strategy_summary(seq, laps)}  —  {total_time:.2f}s")
    print(f"  [{len(strategies)+1}] Enter custom strategy")

    def _pick_strategy(label):
        """Let user pick a pre-calculated or custom strategy. Returns (seq, laps, pit_laps)."""
        print(f"  {label} strategy:")
        max_opt = len(strategies) + 1
        while True:
            try:
                choice = int(input(f"  Choice [1-{max_opt}]: "))
                if 1 <= choice <= len(strategies):
                    _, seq, laps, pit_laps = strategies[choice - 1]
                    return seq, laps, pit_laps
                elif choice == max_opt:
                    return _build_custom_strategy()
                else:
                    print(f"  Enter 1–{max_opt}.")
            except ValueError:
                print("  Enter a number.")

    def _pick_one_driver(role, exclude_name=None):
        """Return (name, skill, adj, seq, laps, pit_laps) for one sim driver."""
        saved = load_saved_drivers()
        print(f"\n--- {role} ---")
        if saved:
            print("  [1] Pick from driver database")
            print("  [2] Enter manually")
            while True:
                src = input("  Source [1/2]: ").strip()
                if src in ("1", "2"):
                    break
                print("  Enter 1 or 2.")
        else:
            src = "2"

        if src == "1":
            print("\n  Saved drivers:")
            for i, d in enumerate(saved, 1):
                print(f"    [{i:>2}] {d['name']:<24} {d.get('team',''):<20} Skill {d['skill']}")
            while True:
                try:
                    idx = int(input(f"  Choose [1-{len(saved)}]: "))
                    if 1 <= idx <= len(saved):
                        break
                    print(f"  Enter 1–{len(saved)}.")
                except ValueError:
                    print("  Enter a number.")
            d = saved[idx - 1]
            name  = d["name"]
            skill = d["skill"]
            if exclude_name and name == exclude_name:
                print(f"  {name} is already Driver 1 — pick another.")
                return _pick_one_driver(role, exclude_name)
        else:
            while True:
                name = input("Name: ").strip()
                if not name:
                    print("Name cannot be empty.")
                elif exclude_name and name == exclude_name:
                    print("Name cannot be the same as Driver 1.")
                else:
                    break
            skill = get_int("Skill level [0-100]: ", min_val=0, max_val=100)

        adj = skill_adjustment(skill)
        print(f"  → {skill_label(skill)}  |  pace adj: {-adj:+.3f}s/lap vs baseline")
        seq, laps, pit_laps = _pick_strategy(role)
        return name, skill, adj, seq, laps, pit_laps

    d1_name, d1_skill, d1_adj, d1_seq, d1_laps, d1_pit_laps = _pick_one_driver("Driver 1 (Leader)")
    d2_name, d2_skill, d2_adj, d2_seq, d2_laps, d2_pit_laps = _pick_one_driver("Driver 2 (Chaser)", exclude_name=d1_name)

    initial_gap = get_float(f"\n{d2_name} is how many seconds behind {d1_name}? ", min_val=0)

    # ── Work out tactics ──
    tactic = {}
    for n in range(max(len(d1_pit_laps), len(d2_pit_laps))):
        d1_lap = d1_pit_laps[n] if n < len(d1_pit_laps) else None
        d2_lap = d2_pit_laps[n] if n < len(d2_pit_laps) else None
        if d1_lap is None:
            tactic[("d2", n)] = "overcut"
        elif d2_lap is None:
            tactic[("d2", n)] = "undercut"
        elif d2_lap < d1_lap:
            tactic[("d2", n)] = "undercut"
        elif d2_lap > d1_lap:
            tactic[("d2", n)] = "overcut"
        else:
            tactic[("d2", n)] = "same lap"

    # ── Build skill-adjusted lap-pace arrays ──
    def lap_pace_array(seq, laps, adj):
        arr = []
        for tyre, lap_count in zip(seq, laps):
            arr.extend([tyres[tyre]["pace"] + adj] * lap_count)
        return arr

    d1_paces = lap_pace_array(d1_seq, d1_laps, d1_adj)
    d2_paces = lap_pace_array(d2_seq, d2_laps, d2_adj)

    # ── Simulation ──
    d1_time = 0.0
    d2_time = initial_gap

    d1_pit_set = {pl: i for i, pl in enumerate(d1_pit_laps)}
    d2_pit_set = {pl: i for i, pl in enumerate(d2_pit_laps)}

    print(f"\n  {'Lap':<5} {'Gap (s)':<10} {'Leader':<18} {'Event'}")
    print(f"  {'-'*5} {'-'*10} {'-'*18} {'-'*38}")

    leader = d1_name
    order_changed = False
    last_overtake_lap = None
    overtake_count = 0

    for lap in range(1, race_laps + 1):
        d1_time += d1_paces[lap - 1]
        d2_time += d2_paces[lap - 1]
        events = []

        # ── DRS pace benefit for the chasing car ──
        # 0.5 s per zone shaved off the chasing car's lap when within 1.0 s.
        # Simulates the real straightline speed gain from the open rear wing.
        if drs_zones > 0:
            pre_gap = d2_time - d1_time   # positive → d2 still behind
            if 0 < pre_gap <= 1.0:
                drs_gain = drs_zones * 0.5
                d2_time -= drs_gain
                events.append(f"[DRS ×{drs_zones}: {d2_name} gains {drs_gain:.1f}s]")
            elif pre_gap < 0 and abs(pre_gap) <= 1.0:
                # d2 is leading but d1 is within 1 s — d1 benefits instead
                drs_gain = drs_zones * 0.5
                d1_time -= drs_gain
                events.append(f"[DRS ×{drs_zones}: {d1_name} gains {drs_gain:.1f}s]")

        # ── Pit stops ──
        if lap in d1_pit_set:
            pit_idx = d1_pit_set[lap]
            eff = effective_pit_loss(lap, pit_loss, sc)
            d1_time += eff
            sc_tag = " [SC]" if sc and sc["start"] <= lap <= sc["end"] else ""
            t = tactic.get(("d2", pit_idx), "")
            label = f"  ← {d2_name} OVERCUT attempt" if t == "overcut" else ""
            events.append(f"{d1_name} pits (-{eff:.1f}s){sc_tag}{label}")

        if lap in d2_pit_set:
            pit_idx = d2_pit_set[lap]
            eff = effective_pit_loss(lap, pit_loss, sc)
            d2_time += eff
            sc_tag = " [SC]" if sc and sc["start"] <= lap <= sc["end"] else ""
            t = tactic.get(("d2", pit_idx), "")
            if t == "undercut":
                label = f"  ← {d2_name} UNDERCUT attempt"
            elif t == "same lap":
                label = "  ← same lap pit"
            else:
                label = ""
            events.append(f"{d2_name} pits (-{eff:.1f}s){sc_tag}{label}")

        # ── On-track gap after this lap ──
        gap = d2_time - d1_time   # positive → d2 still behind, negative → d2 ahead

        # ── 3-attempt overtake check (both directions) ──
        # The car that is behind gets 3 chances per lap (early, mid, late sector)
        if gap != 0:
            if gap > 0:
                # d1 leads, d2 is trying to pass
                attacker_name, defender_name = d2_name, d1_name
                attacker_tyre = current_tyre(d2_seq, d2_laps, lap)
                defender_tyre = current_tyre(d1_seq, d1_laps, lap)
                atk_skill, def_skill = d2_skill, d1_skill
                raw_gap = gap
            else:
                # d2 leads, d1 is trying to re-pass
                attacker_name, defender_name = d1_name, d2_name
                attacker_tyre = current_tyre(d1_seq, d1_laps, lap)
                defender_tyre = current_tyre(d2_seq, d2_laps, lap)
                atk_skill, def_skill = d1_skill, d2_skill
                raw_gap = abs(gap)

            prob = overtake_probability(
                attacker_tyre, defender_tyre, raw_gap,
                atk_skill, def_skill,
                overtaking_difficulty, drs_zones
            )

            # Three sector checks — pass if any succeeds
            passed = any(random.random() < prob for _ in range(3))

            if passed:
                overtake_count += 1
                last_overtake_lap = lap
                order_changed = True
                # After overtake the gap is a small buffer
                new_gap = 0.3
                if gap > 0:
                    # d2 overtook d1
                    d2_time = d1_time - new_gap
                    gap = d2_time - d1_time   # now negative
                else:
                    # d1 re-overtook d2
                    d1_time = d2_time - new_gap
                    gap = d2_time - d1_time   # now positive

                new_leader = d1_name if gap >= 0 else d2_name
                margin = abs(gap)
                skill_note = ""
                if def_skill > atk_skill + 10:
                    skill_note = " (upset! lower-rated driver beat the defence)"
                events.append(
                    f">>> {attacker_name} OVERTAKES {defender_name}! "
                    f"gap {margin:.2f}s{skill_note}"
                )
                leader = new_leader

        display_gap = abs(d2_time - d1_time)
        current_leader = d1_name if (d2_time - d1_time) >= 0 else d2_name

        event_str = " | ".join(events)
        if events or lap % 5 == 0 or lap == race_laps:
            print(f"  Lap {lap:<3}  {display_gap:>6.2f}s    {current_leader:<18} {event_str}")

    final_gap = abs(d2_time - d1_time)
    winner = d1_name if (d2_time - d1_time) >= 0 else d2_name

    print("\n" + "=" * 55)
    print(f"  RESULT: {winner} wins by {final_gap:.2f}s")
    if overtake_count:
        print(f"  Total on-track overtakes: {overtake_count}  (last on lap {last_overtake_lap})")
    else:
        print(f"  No on-track overtake — track position held throughout.")
    print("=" * 55)


def full_grid_race_sim(strategies, tyres, pit_loss, sc, race_laps,
                       overtaking_difficulty, drs_zones,
                       qualifying_results=None, pre_built_drivers=None):
    W = 60  # display width

    print("\n" + "=" * W)
    print("           FULL GRID RACE SIMULATOR")
    print("=" * W)
    ot_label = overtaking_difficulty.upper()
    drs_label = ("OFF" if drs_zones == 0
                 else f"{drs_zones} zone{'s' if drs_zones > 1 else ''} (+{drs_zones * 0.5:.1f}s/lap in DRS window)")
    print(f"  Overtaking: {ot_label}  |  DRS: {drs_label}")
    if qualifying_results:
        print(f"  Grid set by qualifying — starting tyre constraints apply.")
    print("=" * W)

    # ── Driver setup ──────────────────────────────────────────────────────────
    drivers = []

    if qualifying_results:
        # Grid order and starting tyres are locked from qualifying.
        # Each driver must pick a strategy that opens on their qualifying tyre.
        print("\nRace strategy selection  (qualifying grid — start tyre locked):")
        for slot, qr in enumerate(qualifying_results, 1):
            adj = skill_adjustment(qr["skill"])
            q_tyre = qr["q_tyre"]
            print(f"\n  ── P{slot}: {qr['name']:<22} Skill: {qr['skill']} "
                  f"({skill_label(qr['skill'])})  Start tyre: {q_tyre} ──")
            valid = qr["valid_strategies"]
            if len(valid) == 1:
                _, seq, laps, pit_laps = valid[0]
                print(f"  Only strategy on {q_tyre}: {strategy_summary(seq, laps)}")
            else:
                for rank, (tt, vseq, vlaps, vpits) in enumerate(valid, 1):
                    print(f"    [{rank}] {strategy_summary(vseq, vlaps)}  — {tt:.2f}s")
                sc_idx = get_int(f"  Strategy [1-{len(valid)}]: ", min_val=1, max_val=len(valid))
                _, seq, laps, pit_laps = valid[sc_idx - 1]

            paces = []
            for tyre, lap_count in zip(seq, laps):
                paces.extend([tyres[tyre]["pace"] + adj] * lap_count)

            drivers.append({
                "name":      qr["name"],
                "skill":     qr["skill"],
                "adj":       adj,
                "seq":       list(seq),
                "laps":      list(laps),
                "pit_laps":  list(pit_laps),
                "pit_set":   {pl: idx for idx, pl in enumerate(pit_laps)},
                "paces":     paces,
                "total_time": (slot - 1) * 0.3,
                "pits_done": 0,
            })
    elif pre_built_drivers is not None:
        # Championship / external caller supplied fully-built driver dicts — use directly.
        drivers = list(pre_built_drivers)
    else:
        # No qualifying — choose drivers from DB or enter manually, then pick strategies.
        session_drv = select_session_drivers(max_drivers=20)
        print("\nPick a race strategy for each driver  (grid P1 first):")
        for slot, d in enumerate(session_drv, 1):
            adj = skill_adjustment(d["skill"])
            print(f"\n  ── P{slot}: {d['name']}  Skill: {d['skill']} ({skill_label(d['skill'])}) ──")
            for rank, (tt, seq, laps, pit_laps) in enumerate(strategies, 1):
                print(f"    [{rank}] {strategy_summary(seq, laps)}  — {tt:.2f}s")
            sc_idx = get_int(f"  Strategy [1-{len(strategies)}]: ", min_val=1, max_val=len(strategies))
            _, seq, laps, pit_laps = strategies[sc_idx - 1]

            paces = []
            for tyre, lap_count in zip(seq, laps):
                paces.extend([tyres[tyre]["pace"] + adj] * lap_count)

            drivers.append({
                "name":      d["name"],
                "skill":     d["skill"],
                "adj":       adj,
                "seq":       list(seq),
                "laps":      list(laps),
                "pit_laps":  list(pit_laps),
                "pit_set":   {pl: idx for idx, pl in enumerate(pit_laps)},
                "paces":     paces,
                "total_time": (slot - 1) * 0.3,
                "pits_done": 0,
            })

    # ── Pre-race grid display ──────────────────────────────────────────────────
    print("\n" + "=" * W)
    print("  STARTING GRID")
    print("-" * W)
    print(f"  {'P':<4} {'Driver':<20} {'Skill':<12} {'Strategy'}")
    print(f"  {'-'*4} {'-'*20} {'-'*12} {'-'*20}")
    for slot, d in enumerate(drivers, 1):
        strat_str = strategy_short(d["seq"], d["laps"])
        print(f"  P{slot:<3} {d['name']:<20} {d['skill']:<3} {skill_label(d['skill']):<8} {strat_str}")
    print("=" * W)

    # ── Race simulation ────────────────────────────────────────────────────────
    overtake_tally = 0

    for lap in range(1, race_laps + 1):
        lap_events = []

        # 1. Sort to know who is ahead at start of this lap
        drivers.sort(key=lambda d: d["total_time"])

        # 2. Compute each driver's lap time, applying DRS benefit where eligible
        for i, d in enumerate(drivers):
            lap_time = d["paces"][lap - 1]

            if drs_zones > 0 and i > 0:
                ahead = drivers[i - 1]
                gap_start = d["total_time"] - ahead["total_time"]
                if 0 < gap_start <= 1.0:
                    lap_time -= drs_zones * 0.5   # open wing straight-line gain

            d["total_time"] += lap_time

        # 3. Pit stops
        for d in drivers:
            if lap in d["pit_set"]:
                eff = effective_pit_loss(lap, pit_loss, sc)
                d["total_time"] += eff
                d["pits_done"] += 1
                sc_tag = " [SC]" if sc and sc["start"] <= lap <= sc["end"] else ""
                lap_events.append(f"Lap {lap:>3}  PIT  {d['name']}  (−{eff:.1f}s{sc_tag})")

        # 4. Sort to get current race order
        drivers.sort(key=lambda d: d["total_time"])

        # 5. Overtake checks — work back-to-front so position swaps propagate cleanly
        for i in range(len(drivers) - 1, 0, -1):
            behind = drivers[i]
            ahead  = drivers[i - 1]
            gap = behind["total_time"] - ahead["total_time"]

            if gap <= 0 or gap > 2.0:
                continue

            atk_tyre = current_tyre(behind["seq"], behind["laps"], lap)
            def_tyre = current_tyre(ahead["seq"],  ahead["laps"],  lap)

            prob = overtake_probability(
                atk_tyre, def_tyre, gap,
                behind["skill"], ahead["skill"],
                overtaking_difficulty, drs_zones
            )

            if any(random.random() < prob for _ in range(3)):
                # Give passer a small margin over the defended car
                behind["total_time"] = ahead["total_time"] - 0.15
                drivers.sort(key=lambda d: d["total_time"])
                overtake_tally += 1
                # Find new positions after sort
                new_pos_behind = next(j + 1 for j, d in enumerate(drivers) if d is behind)
                new_pos_ahead  = next(j + 1 for j, d in enumerate(drivers) if d is ahead)
                lap_events.append(
                    f"Lap {lap:>3}  OVT  P{new_pos_behind} {behind['name']} "
                    f"passes {ahead['name']} → now P{new_pos_ahead}"
                )

        # 6. Print output
        show_full = (lap % 5 == 0 or lap == 1 or lap == race_laps)

        if lap_events:
            for ev in lap_events:
                print(f"  ▸ {ev}")

        if show_full:
            leader_time = drivers[0]["total_time"]
            tyre_col = 10
            print(f"\n  LAP {lap}/{race_laps}" + (" ─ FINISH" if lap == race_laps else ""))
            print(f"  {'P':<4} {'Driver':<20} {'Gap':<13} {'Tyre':<{tyre_col}} {'Pits'}")
            print(f"  {'-'*4} {'-'*20} {'-'*13} {'-'*tyre_col} {'-'*4}")
            for pos, d in enumerate(drivers, 1):
                gap = d["total_time"] - leader_time
                gap_str = "LEADER" if pos == 1 else f"+{gap:.3f}s"
                tyre = current_tyre(d["seq"], d["laps"], min(lap, race_laps))
                print(f"  P{pos:<3} {d['name']:<20} {gap_str:<13} {tyre:<{tyre_col}} {d['pits_done']}")
            print()

    # ── Final classification ───────────────────────────────────────────────────
    drivers.sort(key=lambda d: d["total_time"])
    leader_time = drivers[0]["total_time"]

    print("=" * W)
    print("               FINAL CLASSIFICATION")
    print("=" * W)
    print(f"  {'P':<4} {'Driver':<20} {'Skill':<7} {'Pits':<6} {'Total time':<17} {'Gap'}")
    print(f"  {'-'*4} {'-'*20} {'-'*7} {'-'*6} {'-'*17} {'-'*12}")
    for pos, d in enumerate(drivers, 1):
        gap = d["total_time"] - leader_time
        gap_str = "WINNER" if pos == 1 else f"+{gap:.3f}s"
        print(f"  P{pos:<3} {d['name']:<20} {d['skill']:<7} {d['pits_done']:<6} {format_time(d['total_time']):<17} {gap_str}")

    print("\n" + "=" * W)
    print(f"  WINNER: {drivers[0]['name']}!")
    if len(drivers) >= 3:
        print(f"  PODIUM: {drivers[0]['name']} / {drivers[1]['name']} / {drivers[2]['name']}")
    print(f"  Total on-track overtakes this race: {overtake_tally}")
    print("=" * W)
    return drivers   # finishing order P1 → Pn


def manual_strategy(tyres, pit_loss, sc, race_laps, best_time):
    tyre_names = list(tyres.keys())

    print("\n" + "=" * 55)
    print("         MANUAL STRATEGY TESTER")
    print("=" * 55)
    print("Available compounds:")
    for i, name in enumerate(tyre_names, 1):
        print(f"  [{i}] {name}  (pace {tyres[name]['pace']}s, max {tyres[name]['max_laps']} laps)")

    while True:
        num_stints = get_int("\nHow many stints? ", min_val=1, max_val=race_laps)
        seq = []
        laps = []
        total_laps = 0

        for i in range(num_stints):
            remaining = race_laps - total_laps - (num_stints - i - 1)
            print(f"\n  Stint {i + 1}:")
            compound_choice = get_int(f"    Compound [1-{len(tyre_names)}]: ", min_val=1, max_val=len(tyre_names))
            name = tyre_names[compound_choice - 1]
            max_this = min(tyres[name]["max_laps"], remaining)

            if i == num_stints - 1:
                lap_count = remaining
                print(f"    Laps: {lap_count} (remaining)")
            else:
                lap_count = get_int(f"    Laps (1–{max_this}): ", min_val=1, max_val=max_this)

            seq.append(name)
            laps.append(lap_count)
            total_laps += lap_count

        if total_laps != race_laps:
            print(f"\n  Stints only cover {total_laps} of {race_laps} laps. Try again.")
            continue

        pit_laps = []
        cum = 0
        total_time = 0
        for i, (tyre, lap_count) in enumerate(zip(seq, laps)):
            total_time += lap_count * tyres[tyre]["pace"]
            cum += lap_count
            if i < len(seq) - 1:
                pit_laps.append(cum)
                total_time += effective_pit_loss(cum, pit_loss, sc)

        print("\n" + "=" * 55)
        print(f"  Strategy : {strategy_summary(seq, laps)}")
        print(f"  Total time: {total_time:.2f}s  ({format_time(total_time)})")
        if pit_laps:
            print(f"  Pit on    : {', '.join(f'lap {pl}' for pl in pit_laps)}")
        gap = total_time - best_time
        if gap < 0:
            print(f"  vs best   : {gap:.2f}s  *** FASTER than top strategy! ***")
        elif gap == 0:
            print(f"  vs best   : same time as top strategy")
        else:
            print(f"  vs best   : +{gap:.2f}s slower than top strategy")
        print("=" * 55)

        if not get_yes_no("\nTest another manual strategy? [y/n]: "):
            break


def championship_sim():
    W = 64

    print("\n" + "=" * W)
    print("           CHAMPIONSHIP SEASON SIMULATOR")
    print("=" * W)
    print(f"  Points: {' — '.join(str(p) for p in F1_POINTS)} for P1–P{len(F1_POINTS)}")
    print("=" * W)

    # ── Season roster ─────────────────────────────────────────────────────────
    print("\nSelect your season driver roster (2–20 drivers):")
    season_drivers = select_session_drivers(max_drivers=20)
    driver_map = {d["name"]: d for d in season_drivers}

    num_races = get_int(f"\nHow many races this season? [1-20]: ", min_val=1, max_val=20)

    standings = {d["name"]: 0 for d in season_drivers}
    print(f"\n  {len(season_drivers)} drivers, {num_races} race{'s' if num_races > 1 else ''}. Let's go!\n")

    def show_standings(label):
        sorted_s = sorted(standings.items(), key=lambda x: -x[1])
        print("\n" + "─" * W)
        print(f"  {label}")
        print("─" * W)
        print(f"  {'P':<4} {'Driver':<26} {'Team':<20} {'Pts'}")
        print(f"  {'-'*4} {'-'*26} {'-'*20} {'-'*5}")
        leader_pts = sorted_s[0][1]
        for pos, (name, pts) in enumerate(sorted_s, 1):
            gap = f"  (−{leader_pts - pts})" if pos > 1 and pts > 0 else ""
            team = driver_map.get(name, {}).get("team", "")
            marker = "  ★" if pos == 1 else ""
            print(f"  P{pos:<3} {name:<26} {team:<20} {pts}{gap}{marker}")
        print("─" * W)

    races_completed = 0
    for race_num in range(1, num_races + 1):
        print("\n" + "=" * W)
        print(f"  RACE {race_num} / {num_races}")
        print("=" * W)

        # ── Track ──
        preset = pick_preset()
        if preset:
            race_laps = preset["race_laps"]
            pit_loss  = preset["pit_loss"]
            tyres     = preset["tyres"]
            min_compounds = preset["min_compounds"]
            overtaking_difficulty = preset.get("overtaking_difficulty", "medium")
            drs_zones = preset.get("drs_zones", 1 if preset.get("drs_active", True) else 0)
            ot_label  = overtaking_difficulty.upper()
            drs_label = "OFF" if drs_zones == 0 else f"{drs_zones} zone{'s' if drs_zones > 1 else ''} (+{drs_zones * 0.5:.1f}s/lap)"
            print(f"\n  {race_laps} laps  |  pit loss {pit_loss}s  |  OT: {ot_label}  |  DRS: {drs_label}")
        else:
            race_laps     = get_int("Race laps: ")
            pit_loss      = get_float("Pit loss (seconds): ", min_val=0)
            num_tyres     = get_int("Number of tyre compounds: ", min_val=1, max_val=len(PRESET_COMPOUNDS))
            tyres         = {}
            compound_names = select_compounds(num_tyres)
            for cname in compound_names:
                print(f"\n--- {cname} ---")
                pace     = get_float(f"Average lap time for {cname} (seconds): ", min_val=0.1)
                max_laps = get_int(f"Maximum laps for {cname}: ")
                tyres[cname] = {"pace": pace, "max_laps": max_laps}
            min_compounds = get_int("\nMinimum compounds required: ", min_val=1)
            while min_compounds > len(tyres):
                print(f"Cannot exceed number of available compounds ({len(tyres)}).")
                min_compounds = get_int("Minimum compounds required: ", min_val=1)
            overtaking_difficulty, drs_zones = get_track_params()

        # ── Safety car ──
        sc = None
        if get_yes_no("\nInclude a safety car? [y/n]: "):
            sc = get_sc_params(race_laps)

        # ── Strategies ──
        print("\nCalculating strategies...")
        strategies = find_best_strategies(race_laps, pit_loss, tyres, min_compounds, sc=sc)
        display_strategies(strategies, tyres, pit_loss, sc=sc)

        # ── Grid: qualifying or random ─────────────────────────────────────
        if get_yes_no("Run qualifying to set the grid? [y/n]: "):
            quali_results = qualifying_sim(tyres, strategies,
                                           pre_selected_drivers=season_drivers)
            finishing_order = full_grid_race_sim(
                strategies, tyres, pit_loss, sc, race_laps,
                overtaking_difficulty, drs_zones,
                qualifying_results=quali_results
            )
        else:
            # Random grid — each driver picks a race strategy
            grid = list(season_drivers)
            random.shuffle(grid)
            print("\nGrid order (randomised):")
            for slot, d in enumerate(grid, 1):
                print(f"  P{slot}: {d['name']}")

            pre_built = []
            print("\nStrategy selection:")
            for slot, d in enumerate(grid, 1):
                adj = skill_adjustment(d["skill"])
                print(f"\n  ── P{slot}: {d['name']:<24} {skill_label(d['skill'])} ──")
                for rank, (tt, seq, laps, pit_laps) in enumerate(strategies, 1):
                    print(f"    [{rank}] {strategy_summary(seq, laps)}  — {tt:.2f}s")
                sc_idx = get_int(f"  Strategy [1-{len(strategies)}]: ",
                                 min_val=1, max_val=len(strategies))
                _, seq, laps, pit_laps = strategies[sc_idx - 1]

                paces = []
                for tyre, lap_count in zip(seq, laps):
                    paces.extend([tyres[tyre]["pace"] + adj] * lap_count)

                pre_built.append({
                    "name":       d["name"],
                    "skill":      d["skill"],
                    "adj":        adj,
                    "seq":        list(seq),
                    "laps":       list(laps),
                    "pit_laps":   list(pit_laps),
                    "pit_set":    {pl: i for i, pl in enumerate(pit_laps)},
                    "paces":      paces,
                    "total_time": (slot - 1) * 0.3,
                    "pits_done":  0,
                })

            finishing_order = full_grid_race_sim(
                strategies, tyres, pit_loss, sc, race_laps,
                overtaking_difficulty, drs_zones,
                pre_built_drivers=pre_built
            )

        # ── Points ────────────────────────────────────────────────────────
        print("\n" + "─" * W)
        print(f"  RACE {race_num} POINTS AWARDED")
        print("─" * W)
        for pos, d in enumerate(finishing_order, 1):
            pts = F1_POINTS[pos - 1] if pos <= len(F1_POINTS) else 0
            standings[d["name"]] = standings.get(d["name"], 0) + pts
            bar = "  +" + str(pts) if pts else ""
            print(f"  P{pos:<3} {d['name']:<26} {pts} pts  (total: {standings[d['name']]})")

        races_completed += 1

        # ── Standings after this race ──────────────────────────────────────
        show_standings(f"CHAMPIONSHIP STANDINGS — after Race {race_num}/{num_races}")

        if race_num < num_races:
            if not get_yes_no("\nContinue to next race? [y/n]: "):
                print(f"  Season ended after {race_num} race(s).")
                break

    # ── Final standings ────────────────────────────────────────────────────
    sorted_final = sorted(standings.items(), key=lambda x: -x[1])
    print("\n" + "=" * W)
    print("             FINAL CHAMPIONSHIP STANDINGS")
    print("=" * W)
    print(f"  {'P':<4} {'Driver':<26} {'Team':<20} {'Pts'}")
    print(f"  {'-'*4} {'-'*26} {'-'*20} {'-'*5}")
    for pos, (name, pts) in enumerate(sorted_final, 1):
        team   = driver_map.get(name, {}).get("team", "")
        marker = "  ★ CHAMPION!" if pos == 1 else ""
        print(f"  P{pos:<3} {name:<26} {team:<20} {pts}{marker}")
    print("=" * W)
    if races_completed > 0:
        champion = sorted_final[0][0]
        print(f"\n  🏆  {champion} is the {races_completed}-race champion!")
        print("=" * W)


def get_sc_params(race_laps):
    print("\n--- Safety Car Setup ---")
    sc_start = get_int("Safety car start lap: ", min_val=1, max_val=race_laps - 1)
    sc_dur = get_int("Safety car duration (laps): ", min_val=1, max_val=race_laps - sc_start)
    sc_end = sc_start + sc_dur - 1
    sc_pit_loss = get_float("Pit loss during safety car (seconds): ", min_val=0)
    return {"start": sc_start, "end": sc_end, "pit_loss": sc_pit_loss}


def get_track_params():
    """Ask for overtaking difficulty and DRS zones — stored with presets."""
    print("\n--- Track Characteristics ---")

    print("Overtaking difficulty:")
    print("  [1] Easy    — lots of passing zones, wide track")
    print("  [2] Medium  — balanced opportunity")
    print("  [3] Hard    — tight / technical, very few overtaking spots")
    while True:
        choice = input("Choose [1-3]: ").strip()
        if choice == "1":
            overtaking_difficulty = "easy"
            break
        elif choice == "2":
            overtaking_difficulty = "medium"
            break
        elif choice == "3":
            overtaking_difficulty = "hard"
            break
        else:
            print("Please enter 1, 2, or 3.")

    print("\nDRS zones (each zone = +0.5 s/lap for the car within 1.0 s behind):")
    print("  0 = No DRS  |  1 = one straight  |  2 = two straights  |  3+ = rare")
    drs_zones = get_int("Number of DRS zones [0-4]: ", min_val=0, max_val=4)

    return overtaking_difficulty, drs_zones


def run_race():
    print("\n" + "=" * 55)
    print("         F1 RACE STRATEGY CALCULATOR")
    print("=" * 55)
    print("  [1] Strategy Calculator  — raw tyre pace + undercut/overcut")
    print("  [2] Full Race Weekend    — qualifying, grid race, driver DB")
    while True:
        mode = input("\nSelect mode [1/2]: ").strip()
        if mode in ("1", "2"):
            break
        print("Please enter 1 or 2.")
    full_race_mode = (mode == "2")

    preset = pick_preset()

    if preset:
        race_laps = preset["race_laps"]
        pit_loss = preset["pit_loss"]
        tyres = preset["tyres"]
        min_compounds = preset["min_compounds"]
        overtaking_difficulty = preset.get("overtaking_difficulty", "medium")
        drs_zones = preset.get("drs_zones", 1 if preset.get("drs_active", True) else 0)
        print(f"\n  Loaded: {race_laps} laps, {len(tyres)} compounds, pit loss {pit_loss}s")
        ot_label = overtaking_difficulty.upper()
        drs_label = "OFF" if drs_zones == 0 else f"{drs_zones} zone{'s' if drs_zones > 1 else ''} (+{drs_zones * 0.5:.1f}s/lap)"
        print(f"  Overtaking: {ot_label}  |  DRS: {drs_label}")
        for name, data in tyres.items():
            print(f"    {name}: {data['pace']}s/lap, max {data['max_laps']} laps")
    else:
        race_laps = get_int("Race laps: ")
        pit_loss = get_float("Pit loss (seconds): ", min_val=0)
        num_tyres = get_int("Number of tyre compounds: ", min_val=1, max_val=len(PRESET_COMPOUNDS))
        tyres = {}
        compound_names = select_compounds(num_tyres)

        for name in compound_names:
            print(f"\n--- {name} ---")
            pace = get_float(f"Average lap time for {name} (seconds): ", min_val=0.1)
            max_laps = get_int(f"Maximum laps for {name}: ")
            tyres[name] = {"pace": pace, "max_laps": max_laps}

        min_compounds = get_int("\nMinimum compounds required: ", min_val=1)
        while min_compounds > len(tyres):
            print(f"Cannot exceed number of available compounds ({len(tyres)}).")
            min_compounds = get_int("Minimum compounds required: ", min_val=1)

        overtaking_difficulty, drs_zones = get_track_params()

        if get_yes_no("\nSave this track as a preset? [y/n]: "):
            while True:
                track_name = input("Track name: ").strip()
                if track_name:
                    break
                print("Name cannot be empty.")
            save_preset(track_name, race_laps, pit_loss, tyres, min_compounds,
                        overtaking_difficulty, drs_zones)

    sc = None
    if get_yes_no("\nInclude a safety car scenario? [y/n]: "):
        sc = get_sc_params(race_laps)

    print("\nCalculating strategies...")
    strategies = find_best_strategies(race_laps, pit_loss, tyres, min_compounds, sc=sc)
    display_strategies(strategies, tyres, pit_loss, sc=sc)

    if full_race_mode:
        # ── Full Race Weekend ──────────────────────────────────────────────
        if get_yes_no("Compare drivers? [y/n]: "):
            compare_drivers(strategies, tyres, pit_loss, sc=sc)

        if get_yes_no("Run undercut/overcut simulator? [y/n]: "):
            undercut_overcut_sim(strategies, tyres, pit_loss, sc, race_laps,
                                 overtaking_difficulty, drs_zones)

        if get_yes_no("Run full grid race? [y/n]: "):
            quali_results = None
            if get_yes_no("  Run qualifying first? [y/n]: "):
                quali_results = qualifying_sim(tyres, strategies)
            full_grid_race_sim(strategies, tyres, pit_loss, sc, race_laps,
                               overtaking_difficulty, drs_zones,
                               qualifying_results=quali_results)

        if get_yes_no("Test a manual strategy? [y/n]: "):
            best_time = strategies[0][0] if strategies else 0
            manual_strategy(tyres, pit_loss, sc, race_laps, best_time)

    else:
        # ── Strategy Calculator ────────────────────────────────────────────
        if get_yes_no("Run undercut/overcut simulator? [y/n]: "):
            undercut_overcut_sim(strategies, tyres, pit_loss, sc, race_laps,
                                 overtaking_difficulty, drs_zones)

        if get_yes_no("Test a manual strategy? [y/n]: "):
            best_time = strategies[0][0] if strategies else 0
            manual_strategy(tyres, pit_loss, sc, race_laps, best_time)


def main():
    print("\n" + "=" * 60)
    print("        F1 RACE STRATEGY CALCULATOR")
    print("=" * 60)
    print("  All 20 F1 2025 drivers loaded into the database.")
    print("  Edit ratings anytime via  Manage driver database.")
    print("=" * 60)

    while True:
        print("\n  MAIN MENU")
        print("  [1] Race / Strategy session")
        print("  [2] Championship season  (up to 20 races)")
        print("  [3] Manage driver database")
        print("  [4] Quit")

        while True:
            choice = input("Choose [1-4]: ").strip()
            if choice in ("1", "2", "3", "4"):
                break
            print("Please enter 1, 2, 3, or 4.")

        if choice == "1":
            run_race()
        elif choice == "2":
            championship_sim()
        elif choice == "3":
            manage_driver_database()
        elif choice == "4":
            print("atomix is the goat - made by atomix")
            return
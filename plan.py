"""Check a high-altitude itinerary against acclimatization rules of thumb.

Input: a CSV with one row per night (day, camp, sleep_m, high_m optional).
Output: a day-by-day table with flags, a text profile and a summary.

Run: python plan.py itineraries/aconcagua_normal.csv
Standard library only. Not medical advice.
"""
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

# Rules of thumb, in line with the Wilderness Medical Society practice guidelines
# for the prevention of altitude illness. Edit here to be stricter or looser.
THRESHOLD_M = 3000        # rules apply to nights slept above this altitude
MAX_GAIN_PER_NIGHT = 500  # max increase in sleeping altitude from one night to the next
REST_EVERY_M = 1000       # one night without gain for every 1000 m of sleeping altitude gained
MAX_SUMMIT_GAIN = 1200    # max climb from the high camp on summit day
MIN_NIGHTS_ABOVE_5000 = 2 # nights above 5000 m before a summit above 6000 m


@dataclass
class Night:
    day: int
    camp: str
    sleep: int
    high: int


def load(path):
    nights = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(r for r in fh if not r.startswith("#")):
            sleep = int(row["sleep_m"])
            high = int(row.get("high_m") or sleep)
            nights.append(Night(int(row["day"]), row["camp"].strip(), sleep, max(high, sleep)))
    if not nights:
        sys.exit("empty itinerary")
    return nights


def check(nights):
    """Return {day: [flags]} and the summary figures."""
    flags = {n.day: [] for n in nights}
    since_rest = 0          # sleeping altitude gained since the last night without gain
    highest_sleep = nights[0].sleep
    touched = nights[0].high  # highest point reached on any earlier day
    for prev, cur in zip(nights, nights[1:]):
        gain = cur.sleep - prev.sleep
        touched = max(touched, prev.high)
        if cur.sleep > THRESHOLD_M and gain > MAX_GAIN_PER_NIGHT:
            if touched >= cur.sleep:                # climb high, sleep low: already been there on a carry
                flags[cur.day].append(f"note: sleeps {gain} m higher, altitude already touched on day "
                                      f"{next(n.day for n in nights if n.high >= cur.sleep)}")
            else:
                flags[cur.day].append(f"sleeps {gain} m higher")
        if gain <= 0:
            since_rest = 0
        elif cur.sleep > THRESHOLD_M:
            since_rest += gain
            if since_rest > REST_EVERY_M:
                flags[cur.day].append(f"{since_rest} m gained with no night without gain")
        highest_sleep = max(highest_sleep, cur.sleep)

    summit = max(nights, key=lambda n: n.high)
    i = nights.index(summit)
    start = nights[i - 1].sleep if i else summit.sleep
    summit_gain = summit.high - start
    if summit_gain > MAX_SUMMIT_GAIN:
        flags[summit.day].append(f"summit day climbs {summit_gain} m from the high camp")
    above5 = sum(1 for n in nights[:i] if n.sleep >= 5000)
    if summit.high >= 6000 and above5 < MIN_NIGHTS_ABOVE_5000:
        flags[summit.day].append(f"only {above5} night(s) above 5000 m before the summit")
    return flags, {"summit": summit, "summit_gain": summit_gain, "nights_above_5000": above5,
                   "highest_sleep": highest_sleep}


def profile(nights, width=44):
    lo = min(n.sleep for n in nights)
    hi = max(n.high for n in nights)
    scale = lambda m: round((m - lo) / (hi - lo) * width) if hi > lo else 0
    lines = []
    for n in nights:
        s, h = scale(n.sleep), scale(n.high)
        bar = "█" * s + ("·" * (h - s - 1) + "▲" if h > s else "")
        lines.append(f"{n.day:>3} {n.sleep:>5} {bar}")
    return "\n".join(lines)


def main(path):
    nights = load(path)
    flags, s = check(nights)
    print(f"{Path(path).stem} · {len(nights)} nights · highest point {s['summit'].high} m\n")
    w = max(len(n.camp) for n in nights)
    print(f"{'day':>3} {'camp':<{w}} {'sleep':>6} {'high':>6}  flags")
    for n in nights:
        mark = "; ".join(flags[n.day]) or "ok"
        print(f"{n.day:>3} {n.camp:<{w}} {n.sleep:>6} {n.high:>6}  {mark}")
    print("\nprofile (█ sleeping altitude · ▲ highest point of the day)\n" + profile(nights))
    n_flags = sum(1 for v in flags.values() for f in v if not f.startswith("note"))
    n_notes = sum(1 for v in flags.values() for f in v if f.startswith("note"))
    print(f"\n{n_flags} flag(s), {n_notes} note(s) · highest night {s['highest_sleep']} m · {s['nights_above_5000']} night(s) "
          f"above 5000 m before the summit · summit day +{s['summit_gain']} m")
    return 1 if n_flags else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))

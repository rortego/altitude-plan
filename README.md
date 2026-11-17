# Altitude plan

A small checker for high-altitude itineraries. It reads a plan night by night and flags the days that break the usual acclimatization rules of thumb.

## Why

I have been climbing for 13 years and I plan my own expeditions. An itinerary is a schedule with a hard constraint: the body adapts to altitude at its own pace, and the plan has to leave room for it. Checking that by eye on a spreadsheet is easy to get wrong, so I wrote the rules down as code.

## What it checks

For nights slept above 3,000 m:

- Sleeping altitude should not rise more than 500 m from one night to the next.
- One night without gain for every 1,000 m of sleeping altitude gained.
- Summit day should not climb more than 1,200 m from the high camp.
- At least two nights above 5,000 m before a summit above 6,000 m.

A jump in sleeping altitude becomes a note, not a flag, when the altitude was already reached on an earlier carry day ("climb high, sleep low").

The thresholds follow the Wilderness Medical Society practice guidelines for the prevention of altitude illness and sit at the top of `plan.py`, so they can be changed.

## Run it

```
python plan.py itineraries/aconcagua_normal.csv
```

```
day camp                                sleep   high  flags
  4 Plaza de Mulas                       4300   4300  sleeps 900 m higher
  8 Camp Canada                          5050   5050  note: sleeps 750 m higher, altitude already touched on day 6
  9 Nido de Condores                     5550   5550  1250 m gained with no night without gain
 12 Colera (summit)                      5970   6961  ok

3 flag(s), 1 note(s) · highest night 5970 m · 4 night(s) above 5000 m before the summit · summit day +991 m
```

The standard 14-day plan for Aconcagua still gets three flags. That is the point: the camps are where the terrain allows, not where the rule would put them, and the flags show which days need the rest day or the carry that compensates.

`itineraries/fast_and_wrong.csv` is the same mountain in six days. It gets seven flags.

## Input

A CSV with one row per night. `high_m` is optional: the highest point reached that day, for carries and summit day. Lines starting with `#` are comments.

```
day,camp,sleep_m,high_m
6,Plaza de Mulas (carry to Canada),4300,5050
```

Standard library only. The exit code is 1 when there are flags.

## Limits

Altitudes in the sample files are approximate. The rules are rules of thumb: they do not know the person, the weather or the route. This is a planning aid, not medical advice.

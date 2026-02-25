#!/usr/bin/env python3
"""Display response.txt in terminal with green seed numbers next to teams."""

GREEN = '\033[32m'
PURPLE = '\033[35m'
CYAN = '\033[36m'
RESET = '\033[0m'

# Build team -> seed lookup from SEEDS file
with open('SEEDS') as f:
    seeds = [line.strip() for line in f if line.strip()]
team_seed = {name: i + 1 for i, name in enumerate(seeds)}

ROUND_PREFIXES = ('First Round', 'Second Round', 'Quarterfinals', 'Semifinals', 'Final')

BOX_COL = 55  # column where the box starts in response.txt

with open('response.txt') as f:
    lines = f.read().splitlines()

seen_teams = set()

def add_team_seeds(text):
    for team, seed in sorted(team_seed.items(), key=lambda x: -len(x[0])):
        if team in text and team not in seen_teams:
            text = text.replace(team, f'{GREEN}{seed}{RESET} {team}')
            seen_teams.add(team)
    return text

def visible_len(text):
    return len(text.replace(GREEN, '').replace(PURPLE, '').replace(CYAN, '').replace(RESET, ''))

def has_box(line):
    return len(line) > BOX_COL and any(c in line[BOX_COL:] for c in '│┌└')

def color_box(right):
    if right.startswith('│') and ' - ' in right:
        parts = right.split(' - ', 1)
        num = parts[0].replace('│ ', '│ ' + GREEN, 1)
        return num + RESET + ' - ' + parts[1]
    return right

def color_round(left):
    for rp in ROUND_PREFIXES:
        if left.startswith(rp):
            return f'{CYAN}{rp}{RESET}' + left[len(rp):]
    return left

# First pass: split lines into left/right, add seeds (no vs. color yet),
# and group game lines by round block for alignment
processed = []  # list of (left, right, is_game, block_idx)
block_idx = -1

for line in lines:
    if has_box(line):
        left = line[:BOX_COL].rstrip()
        right = color_box(line[BOX_COL:])
    else:
        left = line
        right = ''

    if left.startswith(ROUND_PREFIXES):
        block_idx += 1
        left = color_round(left)
        processed.append((left, '', right, False, block_idx))
    elif left.startswith('Game'):
        # Split "Game N – " prefix from team content
        dash_pos = left.find('– ')
        prefix = left[:dash_pos + 2]
        rest = left[dash_pos + 2:]
        rest = add_team_seeds(rest)
        rest = rest.replace('/', f'{PURPLE}/{RESET}')
        processed.append((prefix, rest, right, True, block_idx))
    else:
        processed.append((left, '', right, False, block_idx))

# Second pass: within each block, normalize prefix width and align "vs."
from collections import defaultdict
block_games = defaultdict(list)
for i, (prefix, content, box, is_game, bidx) in enumerate(processed):
    if is_game:
        block_games[bidx].append(i)

for bidx, indices in block_games.items():
    # Normalize "Game N – " prefix width within block
    max_prefix = max(len(processed[i][0]) for i in indices)

    # Find max visible width before "vs." (in content part)
    max_before_vs = 0
    for i in indices:
        content = processed[i][1]
        if ' vs. ' in content:
            plain = content.replace(GREEN, '').replace(PURPLE, '').replace(CYAN, '').replace(RESET, '')
            before = plain.split(' vs. ')[0]
            max_before_vs = max(max_before_vs, len(before))

    # Pad prefix and align vs.
    for i in indices:
        prefix, content, box, is_game, bi = processed[i]
        # Right-justify the game number: "Game  9 – " instead of "Game 9 –  "
        dash_idx = prefix.find('– ')
        game_num_part = prefix[:dash_idx]  # e.g. "Game 9 "
        pad_needed_prefix = max_prefix - len(prefix)
        padded_prefix = game_num_part[:5] + ' ' * pad_needed_prefix + game_num_part[5:] + prefix[dash_idx:]
        if ' vs. ' in content:
            vs_pos = content.find(' vs. ')
            before_vs = content[:vs_pos]
            after_vs = content[vs_pos + 5:]
            pad_needed = max_before_vs - visible_len(before_vs)
            new_content = before_vs + ' ' * pad_needed + f' {CYAN}vs.{RESET} ' + after_vs
        else:
            new_content = content
        processed[i] = (padded_prefix + new_content, '', box, is_game, bi)

# Final output: recombine left + box
output = []
for prefix, content, box, is_game, bidx in processed:
    left = prefix + content if not is_game else prefix  # games already combined
    if box:
        padding = BOX_COL - visible_len(left)
        output.append(left + ' ' * max(padding, 2) + box)
    else:
        output.append(left)

print()
print('\n'.join(output))
print()

#!/usr/bin/env python3

from datetime import datetime, timedelta

# Read TOURNAMENT_START_DATE from .env
start_date = None
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line.startswith('TOURNAMENT_START_DATE='):
            start_date = datetime.strptime(line.split('=', 1)[1], '%Y-%m-%d')
            break

if start_date is None:
    raise ValueError("TOURNAMENT_START_DATE not found in .env")

# Compute 6 consecutive days formatted like "Wednesday, March 5"
def format_date(d):
    return d.strftime('%A, %B ') + str(d.day)

days = {f'day{i+1}': format_date(start_date + timedelta(days=i)) for i in range(6)}

# Read and fill the template
with open('TEMPLATE') as f:
    template = f.read()
filled = template.format(**days)

# Build round strings from the filled template
round_names = []
for line in filled.splitlines():
    if line.startswith(('First Round', 'Second Round', 'Quarterfinals', 'Semifinals', 'Final')):
        round_names.append(line)

with open('SEEDS') as f:
    seeds = [line.strip() for line in f.readlines()]

game_definitions = [
    {'number': 1, 'round': round_names[0], 'p1_source': {'seed': 12}, 'p2_source': {'seed': 13}},
    {'number': 2, 'round': round_names[0], 'p1_source': {'seed': 9}, 'p2_source': {'seed': 16}},
    {'number': 3, 'round': round_names[0], 'p1_source': {'seed': 10}, 'p2_source': {'seed': 15}},
    {'number': 4, 'round': round_names[0], 'p1_source': {'seed': 11}, 'p2_source': {'seed': 14}},
    {'number': 5, 'round': round_names[1], 'p1_source': {'seed': 5}, 'p2_source': {'game': 1}},
    {'number': 6, 'round': round_names[1], 'p1_source': {'seed': 8}, 'p2_source': {'game': 2}},
    {'number': 7, 'round': round_names[1], 'p1_source': {'seed': 7}, 'p2_source': {'game': 3}},
    {'number': 8, 'round': round_names[1], 'p1_source': {'seed': 6}, 'p2_source': {'game': 4}},
    {'number': 9, 'round': round_names[2], 'p1_source': {'seed': 4}, 'p2_source': {'game': 5}},
    {'number': 10, 'round': round_names[2], 'p1_source': {'seed': 1}, 'p2_source': {'game': 6}},
    {'number': 11, 'round': round_names[2], 'p1_source': {'seed': 2}, 'p2_source': {'game': 7}},
    {'number': 12, 'round': round_names[2], 'p1_source': {'seed': 3}, 'p2_source': {'game': 8}},
    {'number': 13, 'round': round_names[3], 'p1_source': {'game': 9}, 'p2_source': {'game': 10}},
    {'number': 14, 'round': round_names[3], 'p1_source': {'game': 11}, 'p2_source': {'game': 12}},
    {'number': 15, 'round': round_names[4], 'p1_source': {'game': 13}, 'p2_source': {'game': 14}},
]

# Read TOURNAMENT results (each line = winner of that game number)
winners = {}
try:
    with open('TOURNAMENT') as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if line:
                winners[i] = line
except FileNotFoundError:
    pass

# First pass: build games to determine participants, track eliminated teams
first_pass = {}
eliminated = set()
for gd in game_definitions:
    num = gd['number']
    if 'seed' in gd['p1_source']:
        p1 = [seeds[gd['p1_source']['seed'] - 1]]
    else:
        prev = first_pass[gd['p1_source']['game']]
        p1 = prev['p1'] + prev['p2']
    if 'seed' in gd['p2_source']:
        p2 = [seeds[gd['p2_source']['seed'] - 1]]
    else:
        prev = first_pass[gd['p2_source']['game']]
        p2 = prev['p1'] + prev['p2']
    first_pass[num] = {'p1': p1, 'p2': p2}
    if num in winners:
        winner = winners[num]
        for t in p1 + p2:
            if t != winner:
                eliminated.add(t)

# Second pass: rebuild games with eliminated teams filtered out
games = {}
for gd in game_definitions:
    num = gd['number']
    if 'seed' in gd['p1_source']:
        p1 = [seeds[gd['p1_source']['seed'] - 1]]
    else:
        prev = games[gd['p1_source']['game']]
        p1 = prev['p1'] + prev['p2']
    if 'seed' in gd['p2_source']:
        p2 = [seeds[gd['p2_source']['seed'] - 1]]
    else:
        prev = games[gd['p2_source']['game']]
        p2 = prev['p1'] + prev['p2']
    p1 = [t for t in p1 if t not in eliminated]
    p2 = [t for t in p2 if t not in eliminated]
    games[num] = {'round': gd['round'], 'p1': p1, 'p2': p2}

output = [f'{start_date.year} Phillips 66 Big 12 Women\u2019s Basketball Championship Schedule']
current_round = None
for gd in game_definitions:
    num = gd['number']
    game = games[num]
    if game['round'] != current_round:
        current_round = game['round']
        output.append("\n" + current_round)
    if num in winners:
        # Resolve actual participants (use winner of source game, not all candidates)
        if 'seed' in gd['p1_source']:
            p1 = seeds[gd['p1_source']['seed'] - 1]
        else:
            src = gd['p1_source']['game']
            p1 = winners[src] if src in winners else '/'.join(first_pass[src]['p1'] + first_pass[src]['p2'])
        if 'seed' in gd['p2_source']:
            p2 = seeds[gd['p2_source']['seed'] - 1]
        else:
            src = gd['p2_source']['game']
            p2 = winners[src] if src in winners else '/'.join(first_pass[src]['p1'] + first_pass[src]['p2'])
        output.append(f'Game {num} \u2013 {p1} vs. {p2}')
    else:
        p1 = '/'.join(game['p1']) if game['p1'] else '?'
        p2 = '/'.join(game['p2']) if game['p2'] else '?'
        output.append(f'Game {num} \u2013 {p1} vs. {p2}')

# Append the BYU disclaimer from the filled template
for line in filled.splitlines():
    if line.startswith('*Should BYU'):
        output.append('\n' + line)
        break

# Build seeding lines with box
inner_width = max(len(f'{i} - {s}') for i, s in enumerate(seeds, start=1))
inner_width = max(inner_width, len('Seeding:'))
box_width = inner_width + 4  # 2 padding each side

seed_lines = ['', '']  # blank lines to offset down
seed_lines.append('┌' + '─' * (box_width - 2) + '┐')
for index, value in enumerate(seeds, start=1):
    entry = f' {index} - {value}'
    seed_lines.append('│' + entry.ljust(box_width - 2) + '│')
seed_lines.append('└' + '─' * (box_width - 2) + '┘')

# Merge schedule and seeding side by side
schedule_lines = '\n'.join(output).split('\n')
pad = 55

merged = []
total = max(len(schedule_lines), len(seed_lines))
for i in range(total):
    left = schedule_lines[i] if i < len(schedule_lines) else ''
    right = seed_lines[i] if i < len(seed_lines) else ''
    merged.append(f'{left:<{pad}}{right}')

result = '\n'.join(line.rstrip() for line in merged)

with open('response.txt', 'w') as f:
    f.write(result + '\n')

import subprocess
subprocess.run(['python3', 'show.py'])

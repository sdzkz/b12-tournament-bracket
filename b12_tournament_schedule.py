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
with open('tournament-format.txt') as f:
    template = f.read()
filled = template.format(**days)

# Build round strings from the filled template
round_names = []
for line in filled.splitlines():
    if line.startswith(('First Round', 'Second Round', 'Quarterfinals', 'Semifinals', 'Final')):
        round_names.append(line)

with open('seeds.txt') as f:
    seeds = [line.strip() for line in f.readlines()]

print(f"\nSeeding:\n------------------------")
for index, value in enumerate(seeds, start=1):
    print(f"{index} - {value}")

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

games = {}
for gd in game_definitions:
    num = gd['number']
    p1 = []
    if 'seed' in gd['p1_source']:
        p1 = [seeds[gd['p1_source']['seed'] - 1]]
    else:
        prev = games[gd['p1_source']['game']]
        p1 = prev['p1'] + prev['p2']
    p2 = []
    if 'seed' in gd['p2_source']:
        p2 = [seeds[gd['p2_source']['seed'] - 1]]
    else:
        prev = games[gd['p2_source']['game']]
        p2 = prev['p1'] + prev['p2']
    games[num] = {'round': gd['round'], 'p1': p1, 'p2': p2}

output = [f'{start_date.year} Phillips 66 Big 12 Women\u2019s Basketball Championship Schedule']
current_round = None
for gd in game_definitions:
    num = gd['number']
    game = games[num]
    if game['round'] != current_round:
        current_round = game['round']
        output.append("\n" + current_round)
    p1 = '/'.join(game['p1']) if len(game['p1']) > 1 else game['p1'][0]
    p2 = '/'.join(game['p2']) if len(game['p2']) > 1 else game['p2'][0]
    output.append(f'Game {num} \u2013 {p1} vs. {p2}')

# Append the BYU disclaimer from the filled template
for line in filled.splitlines():
    if line.startswith('*Should BYU'):
        output.append('\n' + line)
        break

result = '\n'.join(output)
print('\n')
print(result)
print("\n")

with open('response.txt', 'w') as f:
    f.write(result + '\n')

#!/usr/bin/env python3

with open('seeds.txt') as f:
    seeds = [line.strip() for line in f.readlines()]

print(f"\nSeeding:\n------------------------")
for index, value in enumerate(seeds, start=1):
    print(f"{index} - {value}")

game_definitions = [
    {'number': 1, 'round': 'First Round – Wednesday, March 5', 'p1_source': {'seed': 12}, 'p2_source': {'seed': 13}},
    {'number': 2, 'round': 'First Round – Wednesday, March 5', 'p1_source': {'seed': 9}, 'p2_source': {'seed': 16}},
    {'number': 3, 'round': 'First Round – Wednesday, March 5', 'p1_source': {'seed': 10}, 'p2_source': {'seed': 15}},
    {'number': 4, 'round': 'First Round – Wednesday, March 5', 'p1_source': {'seed': 11}, 'p2_source': {'seed': 14}},
    {'number': 5, 'round': 'Second Round – Thursday, March 6', 'p1_source': {'seed': 5}, 'p2_source': {'game': 1}},
    {'number': 6, 'round': 'Second Round – Thursday, March 6', 'p1_source': {'seed': 8}, 'p2_source': {'game': 2}},
    {'number': 7, 'round': 'Second Round – Thursday, March 6', 'p1_source': {'seed': 7}, 'p2_source': {'game': 3}},
    {'number': 8, 'round': 'Second Round – Thursday, March 6', 'p1_source': {'seed': 6}, 'p2_source': {'game': 4}},
    {'number': 9, 'round': 'Quarterfinals – Friday, March 7', 'p1_source': {'seed': 4}, 'p2_source': {'game': 5}},
    {'number': 10, 'round': 'Quarterfinals – Friday, March 7', 'p1_source': {'seed': 1}, 'p2_source': {'game': 6}},
    {'number': 11, 'round': 'Quarterfinals – Friday, March 7', 'p1_source': {'seed': 2}, 'p2_source': {'game': 7}},
    {'number': 12, 'round': 'Quarterfinals – Friday, March 7', 'p1_source': {'seed': 3}, 'p2_source': {'game': 8}},
    {'number': 13, 'round': 'Semifinals – Saturday, March 8', 'p1_source': {'game': 9}, 'p2_source': {'game': 10}},
    {'number': 14, 'round': 'Semifinals – Saturday, March 8', 'p1_source': {'game': 11}, 'p2_source': {'game': 12}},
    {'number': 15, 'round': 'Final – Sunday, March 9*', 'p1_source': {'game': 13}, 'p2_source': {'game': 14}},
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

output = ['2025 Phillips 66 Big 12 Women’s Basketball Championship Schedule']
current_round = None
for gd in game_definitions:
    num = gd['number']
    game = games[num]
    if game['round'] != current_round:
        current_round = game['round']
        output.append("\n" + current_round)
    p1 = '/'.join(game['p1']) if len(game['p1']) > 1 else game['p1'][0]
    p2 = '/'.join(game['p2']) if len(game['p2']) > 1 else game['p2'][0]
    output.append(f'Game {num} – {p1} vs. {p2}')

print('\n')
print('\n'.join(output))
print("\n")

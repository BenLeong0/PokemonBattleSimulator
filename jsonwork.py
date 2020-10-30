import json

data = [
  {
    'pokedex_number': 6,
    'level': 100,
    'ivs': [20, 3, 12, 31, 2, 30],
    'evs': [4, 0, 0, 252, 0, 252],
    'nature': 'Modest',
    'moves': ['Pound', 'Flamethrower']
  },
  {
    'pokedex_number': 1,
    'level': 1,
    'ivs': [20, 3, 12, 31, 2, 30],
    'evs': [4, 0, 0, 252, 0, 252],
    'nature': 'Docile',
    'moves': ['Razor Leaf']
  },
  {
    'pokedex_number': 25,
    'level': 100,
    'ivs': [20, 3, 12, 31, 2, 30],
    'evs': [4, 0, 0, 252, 0, 252],
    'nature': 'Modest',
    'moves': ['Thunderbolt']
  }
]

with open('team1.json') as outfile:
    data = json.load(outfile)

print(data)

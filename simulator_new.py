import random
import itertools
import csv
import json

natures = {
    'Hardy': [0, 0],
    'Lonely': [1, 2],
    'Brave': [1, 5],
    'Adamant': [1, 3],
    'Naughty': [1, 4],
    'Bold': [2, 1],
    'Docile': [0, 0],
    'Relaxed': [2, 5],
    'Impish': [2, 3],
    'Lax': [2, 4],
    'Timid': [5, 1],
    'Hasty': [5, 2],
    'Serious': [0, 0],
    'Jolly': [5, 3],
    'Naive': [5, 4],
    'Modest': [3, 1],
    'Mild': [3, 2],
    'Quiet': [3, 5],
    'Bashful': [0, 0],
    'Rash': [3, 4],
    'Calm': [4, 1],
    'Gentle': [4, 2],
    'Sassy': [4, 5],
    'Careful': [4, 3],
    'Quirky': [0, 0],
}


class Player:
    def __init__(self, name, team_path):
        self.name = name
        self.team = []
        with open(team_path) as team_file:
            team_data = json.load(team_file)
            for pkmn_kwargs in team_data:
                self.team.append(Pokemon(**pkmn_kwargs))

    def __repr__(self):
        return self.name

    def __add__(self, other):
        return self.name + other


class Pokemon:
    def __init__(self, **kwargs):
        __kwargs_list = ['pokedex_number', 'level', 'ivs', 'evs', 'nature', 'moves']
        [self.__setattr__(key, kwargs.get(key)) for key in __kwargs_list]

        self.get_stats()

    def __repr__(self):
        return self.name

    def get_stats(self):
        base = {}
        assert 0 < self.pokedex_number < 722, "Pokedex number out of range"
        with open('data/pokemondata.csv', 'r') as f:
            data = next(itertools.islice(csv.reader(f), self.pokedex_number, None))
        _, self.name, self.type1, self.type2, _, base['Hp'], base['Atk'], \
          base['Def'], base['SpA'], base['SpD'], base['Spe'], *_ = data

        self.Hp = int((2 * int(base.pop('Hp')) + self.ivs[0] + \
          int(self.evs[0] / 4)) * self.level / 100) + self.level + 10

        nat_vals = natures[self.nature]
        for i, (stat, val) in enumerate(base.items(), start=1):
            nat_mod = 1.1 if i==nat_vals[0] else 0.9 if i==nat_vals[1] else 1
            self.stat = int(nat_mod * (((2 * int(base[stat]) + self.ivs[i] + \
              int(self.evs[i] / 4)) * self.level / 100) + 5))


def ask_action(player):
    while True:
        action_id = input(player + ', would you like to use a move or switch Pokémon?'
                                  '\n 1: Use a move\n 2: Switch Pokémon\n')
        if action_id in ['1', '2']:
            action = [['move', 'switch'][int(action_id)-1]]
            break
        print('== ERROR: Please select a valid action. ==')
    print(action)



p1 = Player('Steve', 'team1.json')
p2 = Player('Alex', 'team2.json')


while True:
    p1.team = []

    ask_action(p1)





    if not p1.team:
        print(p2, 'wins!')
        break
    if not p2.team:
        print(p1, 'wins!')
        break

import random
import itertools
import csv
import json
import getpass

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
        __kwargs_list = ['pokedex_number', 'level', 'ivs', 'evs', 'nature']
        [self.__setattr__(key, kwargs.get(key)) for key in __kwargs_list]
        self.modifiers = dict([(key, 0) for key in ['Hp','Atk','Def','SpA','SpD','Spe']])
        self.get_stats()
        self.get_move_data(kwargs.get('moves'))
        self.status = ''

    def __repr__(self):
        return self.name

    def __add__(self, other):
        return self.name + other

    def get_stats(self):
        base = {}
        assert 0 < self.pokedex_number < 722, "Pokedex number out of range"
        with open('data/pokemondata.csv', 'r') as f:
            data = next(itertools.islice(csv.reader(f), self.pokedex_number, None))
        _, self.name, self.type1, self.type2, _, base['Hp'], base['Atk'], \
          base['Def'], base['SpA'], base['SpD'], base['Spe'], *_ = data

        self.unmodified_stats = {}

        self.unmodified_stats['Hp'] = int((2 * int(base.pop('Hp')) + self.ivs[0] + \
          int(self.evs[0] / 4)) * self.level / 100) + self.level + 10
        self.Hp = self.unmodified_stats['Hp']

        nat_vals = natures[self.nature]
        for i, (stat, val) in enumerate(base.items(), start=1):
            nat_mod = 1.1 if i==nat_vals[0] else 0.9 if i==nat_vals[1] else 1
            self.unmodified_stats[stat] = int(nat_mod * (((2 * int(base[stat]) + \
              self.ivs[i] + int(self.evs[i] / 4)) * self.level / 100) + 5))
            self.__setattr__(stat, self.unmodified_stats[stat])

    def get_move_data(self, movelist):
        self.moves = ['' for move in movelist]
        while ['' for x in self.moves if x == '']:
            with open('data/movedata.csv', 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for line in csv_reader:
                    if line['name'] in movelist:
                        self.moves[movelist.index(line['name'])] = Move(**line)


class Move:
    def __init__(self, **kwargs):
        __kwargs_list = ['name', 'type', 'category', 'pp', 'power', \
          'accuracy', 'priority']
        [self.__setattr__(key, kwargs.get(key)) for key in __kwargs_list]

    def __repr__(self):
        return self.name

    def __add__(self, other):
        return self.name + other


def ask_action(player, ko=False):
    if not ko:
        if len(player.team) > 1:
        # Option to switch if Pokemon are available
            while True:
                action_id = input(player + ', would you like to use a move or switch Pokémon?'
                                          '\n 1: Use a move\n 2: Switch Pokémon\n')
                if action_id in ['1', '2']:
                    action = [['move', 'switch'][int(action_id)-1]]
                    break
                print('== ERROR: Please select a valid action. ==')
        else:
            action = ['move']
    else:
        action = ['switch']

    if action[0] == 'move':
        while True:
            if len(player.team) > 1:
                print('Which move would you like to use? Enter "0" to cancel.')
            else:
                print(player + ', which move would you like to use?')
            for i, move in enumerate(player.team[0].moves, start=1):
                print(str(i)+':', move)

            move_id = input()
            if move_id == '0' and len(player.team) > 1:
                return ask_action(player)
            elif move_id in [str(x) for x in range(1, len(player.team[0].moves)+1)]:
                return action + [player.team[0].moves[int(move_id) - 1]]
            print('== ERROR: Please select a valid move. ==')

    elif action[0] == 'switch':
        while True:
            if player.team[0].Hp > 0:
                print('Which Pokemon would you like to switch to? Press "0" to cancel')
            else:
                print(player + ', which Pokemon would you like to switch to?')
            for i, pkmn in enumerate(player.team[1:], start=1):
                print(str(i)+':', pkmn)

            pkmn_id = input()
            if pkmn_id == '0':
                return ask_action(player)
            elif pkmn_id in [str(x) for x in range(1, len(player.team))]:
                return action + [int(pkmn_id)]


def prod(d):
    i = 1
    for val in d.values():
        i *= val
    return i


def action_order(player1, player2):
    if player1.action[0] == 'switch':
        return player1, player2
    elif player2.action[0] == 'switch':
        return player2, player1
    else:
    # Both attacking
        p1_priority = player1.action[1].priority
        p2_priority = player2.action[1].priority
        p1_speed = p1.team[0].Spe
        p2_speed = p2.team[0].Spe
        if p1_priority > p2_priority:  # Priority
            return player1, player2
        elif p2_priority > p1_priority:
            return player2, player1
        elif p1_speed > p2_speed:  # Speed
            return player1, player2
        elif p2_speed > p1_speed:
            return player2, player1
        else:  # Random
            r = random.randrange(2)
            return [player1, player2][r], [player2, player1][r]


def type_effectiveness(movetype, type1, type2):
    with open('data/type_effectiveness.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            if line['Attacking'] == movetype:
                return float(line[type1]) * float(line[type2])


def damage(attacker, defender, move, weather=None, other=None, critboost=0):
    if move.category == 'Physical':
        a = attacker.Atk
        d = defender.Def
    elif move.category == 'Special':
        a = attacker.SpA
        d = defender.SpD

    battle_modifiers = {'Random': random.uniform(0.85, 1)}

    # Weather
    if (weather == 'Rain' and move.type == 'Water') or (weather == 'Sunny' and move.type == 'Fire'):
        battle_modifiers['Weather'] = 1.5
    elif (weather == 'Rain' and move.type == 'Fire') or (weather == 'Sunny' and move.type == 'Water'):
        battle_modifiers['Weather'] = 0.5

    # Critical hits
    critchances = [24, 8, 2, 1]
    if int(random.randrange(critchances[min(critboost, 3)])) == 0:
        print('  Scored a critical hit!')
        battle_modifiers['Critical'] = 1.5

    # STAB
    if move.type in [attacker.type1, attacker.type2]:
        battle_modifiers['STAB'] = 1.5

    # Type effectiveness
    battle_modifiers['Type'] = type_effectiveness(move.type, defender.type1, defender.type2)
    if battle_modifiers['Type'] > 1:
        print("  It's super effective!")
    elif battle_modifiers['Type'] < 1:
        print("  It's not very effective...")

    # Burn
    if move.category == 'Physical' and attacker.status == 'Burned':
        battle_modifiers['Burn'] = 0.5

    modifier = prod(battle_modifiers)
    return int((((((2 * int(attacker.level)) / 5) + 2) * int(move.power) * a / d) / 50 + 2) * modifier)


def switch(player):
    player.team[0].modifiers = \
      dict([(key, 0) for key in ['Hp','Atk','Def','SpA','SpD','Spe']])
    player.team[0], player.team[player.action[1]] = \
      player.team[player.action[1]], player.team[0]
    if player.team[player.action[1]].Hp <= 0:
        del player.team[player.action[1]]


def attack(player):
    other = [x for x in [p1,p2] if x != player][0]
    attacker = player.team[0]
    defender = other.team[0]
    move = player.action[1]
    print(player.team[0], 'used', move + '!')

    if random.randrange(100) > int(move.accuracy):
        print('you missed idiot!')
        return False

    dam = damage(attacker, defender, move)
    dam_percent = min(1, dam / defender.Hp)
    dam_str = str(dam)
    if dam_percent == 1:
        dam_str = str(defender.Hp) + ' [' + dam_str + ']'
    defender.Hp -= dam
    print('  It dealt', dam_str, '(' + "{:.2%}".format(dam_percent) + ')', 'damage!')

    if defender.Hp <= 0:
        print('  ' + other.name + "'s " + defender.name + ' was knocked out!')
        if len(other.team) == 1:
            other.team = []
        else:
            other.action = ask_action(other, ko=True)
            switch(other)
        return True
    return False



""" BEGIN BATTLE """

p1 = Player('Steve', 'team1.json')
p2 = Player('Alex', 'team2.json')


while True:
    print('====================')
    p1.action = ask_action(p1)
    p2.action = ask_action(p2)
    order = action_order(p1, p2)

    for player in order:
        if player.action[0] == 'switch':
            switch(player)
        else:
            if attack(player):
                break

    if not p1.team:
        print(p2, 'wins!')
        break
    if not p2.team:
        print(p1, 'wins!')
        break

import csv
import ast
import random
from math import prod

stat_ids = {"Hp": 0, "Atk": 1, "Def": 2, "SpA": 3, "SpD": 4, "Spe": 5, "Crit": 6}
stat_mod_values = [2 / 8, 2 / 7, 2 / 6, 2 / 5, 2 / 4, 2 / 3, 2 / 2, 3 / 2, 4 / 2, 5 / 2, 6 / 2, 7 / 2, 8 / 2]
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
default_values = [('pokedex_number', 1), ('level', 1), ('iv', [0, 0, 0, 0, 0, 0]),
                  ('ev', [0, 0, 0, 0, 0, 0]), ('nature', 'Hardy'), ('moves', ['Tackle'])]


def get_pokemon_data(n):
    if 0 < n < 722:
        with open('data/pokemondata.csv', 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for j in range(n - 1):
                next(csv_reader)
            return next(csv_reader)
    else:
        return 'Invalid ID!'


def import_team(teamfile):
    fullteam = []
    with open(teamfile, 'r') as team:
        end = False
        number_of_pokemon = 0
        while not end:
            d = {}
            number_of_pokemon += 1
            while True:
                line = team.readline()
                if line == '\n':  # End of current pokemon
                    break
                elif line == '':  # End of file
                    end = True
                    break
                (key, val) = line.split(':')
                val = val[1:-1]  # Remove newline info
                if key != 'nature':  # Convert from string unless Nature value
                    val = ast.literal_eval(val)
                d[key] = val

            # Default values: will fill in bulbasaur/lvl1/no ivs/no evs/hardy nature if any are missing
            for (key, val) in default_values:
                if key not in d:
                    d[key] = val

            d['mod'] = [0, 0, 0, 0, 0, 0, 0]
            d['status'] = ''
            fullteam.append(d)
            if number_of_pokemon == 6:
                break
    return fullteam


def list_team(player):
    output = player['Name'] + "'s team is: "
    for pkmn in player['Team']:
        output += dict(get_pokemon_data(pkmn['pokedex_number']))['name'] + '; '
    return output[:-2]


def statcalc(pkmn, stat):
    """Returns the specified stat"""
    data = dict(get_pokemon_data(pkmn["pokedex_number"]))
    stat_id = stat_ids[stat]  # for identifying IVs/EVs
    base = int(data[stat])
    level = pkmn["level"]
    iv = pkmn["iv"][stat_id]
    ev = pkmn["ev"][stat_id]
    nature_values = natures[pkmn["nature"]]
    if stat == "Hp":
        stat_val = int((2 * base + iv + int(ev / 4)) * level / 100) + level + 10
    else:
        raw_val = int((2 * base + iv + int(ev / 4)) * level / 100) + 5
        if stat_id == nature_values[0]:
            nat = 1.1
        elif stat_id == nature_values[1]:
            nat = 0.9
        else:
            nat = 1
        stat_val = int(nat * raw_val)
    return stat_val


def fullstats(pkmn):
    """Returns the full stats list"""
    data = dict(get_pokemon_data(pkmn["pokedex_number"]))
    stats = []
    for stat_id in range(6):
        base = int(data[["Hp", "Atk", "Def", "SpA", "SpD", "Spe"][stat_id]])
        level = pkmn["level"]
        iv = pkmn["iv"][stat_id]
        ev = pkmn["ev"][stat_id]
        nature_values = natures[pkmn["nature"]]
        if stat_id == 0:  # HP calculator
            stat_val = int((2 * base + iv + int(ev / 4)) * level / 100) + level + 10
            stat_val = stat_val - pkmn["mod"][stat_id]
        else:  # Non-HP calculator, inc. modifiers
            raw_val = int(
                (2 * base + iv + int(ev / 4)) * level / 100
            ) + 5
            if stat_id == nature_values[0]:
                nat = 1.1
            elif stat_id == nature_values[1]:
                nat = 0.9
            else:
                nat = 1
            mod = stat_mod_values[pkmn["mod"][stat_id] + 6]
            stat_val = int(nat * raw_val * mod)
        stats.append(stat_val)
    return stats


def import_stats(pkmn):
    for data in ['name', 'type1', 'type2']:
        pkmn[data] = dict(get_pokemon_data(pkmn["pokedex_number"]))[data]
    pkmn['stats'] = fullstats(pkmn)


def getmovedata(pkmn):
    tempmoves = []
    for move in pkmn['moves']:
        with open('data/movedata.csv', 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for line in csv_reader:
                if line['name'] == move:
                    tempmoves.append(line)
                    for key in tempmoves[-1]:
                        if tempmoves[-1][key].isnumeric():
                            tempmoves[-1][key] = int(tempmoves[-1][key])
                    break
        # if len(tempmoves) == 4: break     ### For max 4 moves
    pkmn['moves'] = tempmoves


def type_effectiveness(movetype, d_type1, d_type2):
    with open('data/type_effectiveness.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for line in csv_reader:
            if line['Attacking'] == movetype:
                return float(line[d_type1]) * float(line[d_type2])


# Setup: Importing teams, pokemon data etc

team1 = import_team("team1.txt")
team2 = import_team("team2.txt")

for pkmn in team1:
    import_stats(pkmn)
    getmovedata(pkmn)

for pkmn in team2:
    import_stats(pkmn)
    getmovedata(pkmn)

player1 = {'Name': 'Steve', 'Team': team1, 'Win': False}
player2 = {'Name': 'Alex', 'Team': team2, 'Win': False}

for player in [player1, player2]:
    print(list_team(player))

print(player1['Name'] + ": " + dict(get_pokemon_data(team1[0]["pokedex_number"]))["name"])
print(team1[0]['stats'])

print(player2['Name'] + ": " + dict(get_pokemon_data(team2[0]["pokedex_number"]))["name"])
print(team2[0]['stats'])


# Defining battle functions

def ask_for_action(player):
    cancelled = True
    while cancelled:
        cancelled = False
        noswitch = False
        if len(player['Team']) > 1:
            while True:  # Keep asking until valid choice given
                action_id = input(player['Name'] + ', would you like to use a move or switch Pokémon?'
                                                   '\n 1: Use a move\n 2: Switch Pokémon\n')
                if action_id in ['1', '2']:
                    action_id = int(action_id) - 1
                    action = [['move', 'switch'][action_id]]
                    break
                print('== ERROR: Please select a valid action. ==')
            if action[0] == 'move':
                print('W', end='')
        else:
            print(str(player['Name']) + ', w', end='')
            action = ['move']
            noswitch = True

        if action[0] == 'move':
            moves = player['Team'][0]['moves']
            movelist = ''
            for i in range(len(moves)):
                movelist += '\n ' + str(i+1) + ': ' + str(moves[i]['name'])

            while True:  # Keep asking until valid choice given
                prompt = 'hich move would you like to use?'
                if not noswitch:
                    prompt += ' Enter "0" to cancel.'

                move_id = input(prompt + movelist + '\n')
                if move_id == '0' and not noswitch:
                    move_id = int(move_id)
                    cancelled = True
                    break
                elif move_id in [str(x) for x in range(1, len(moves)+1)]:
                    move_id = int(move_id) - 1
                    break
                print('== ERROR: Please select a valid move. ==')
                print('W', end='')
            action_id = moves[move_id]

        elif action[0] == 'switch':
            team = player['Team']  # Not if hp = 0!
            teamlist = ''
            for i in range(1, len(team)):
                teamlist += '\n ' + str(i) + ': ' + str(team[i]['name'])

            while True:  # Keep asking until valid choice given
                pkmn_id = input('Which pokemon would you like to switch to? Enter "0" to cancel.' + teamlist + '\n')
                if pkmn_id == '0':
                    cancelled = True
                    break
                elif pkmn_id in [str(x) for x in range(1, len(team))]:
                    pkmn_id = int(pkmn_id)
                    break
                print('== ERROR: Please select a valid pokemon. ==')

            action_id = pkmn_id
    action.append(action_id)

    return action


def damage(attacker, defender, move, weather=None, other=None, critboost=0):
    """Calculates the damage dealt from an attack"""
    if move['category'] == 'Physical':
        k = 1
    elif move['category'] == 'Special':
        k = 3
    else:
        return 'ERROR: Bad Category'

    a = attacker['stats'][k]
    d = defender['stats'][k + 1]
    attackerlevel = attacker['level']

    battle_modifiers = {'Random': random.uniform(0.85, 1)}

    # Weather
    if (weather == 'Rain' and move['Type'] == 'Water') or (weather == 'Sunny' and move['Type'] == 'Fire'):
        battle_modifiers['Weather'] = 1.5
    elif (weather == 'Rain' and move['Type'] == 'Fire') or (weather == 'Sunny' and move['Type'] == 'Water'):
        battle_modifiers['Weather'] = 0.5

    # Critical hits
    critchances = [24, 8, 2, 1]
    if int(random.randrange(critchances[min(critboost, 3)])) == 0:
        print('   Scored a critical hit!')
        battle_modifiers['Critical'] = 1.5

    # STAB
    if move['type'] == attacker['type1'] or move['type'] == defender['type2']:
        battle_modifiers['STAB'] = 1.5

    # Type
    battle_modifiers['Type'] = type_effectiveness(move['type'], defender['type1'], defender['type2'])

    # Burn
    if move['category'] == 'Physical' and attacker['status'] == 'Burned':
        battle_modifiers['Burn'] = 0.5

    modifier = prod([battle_modifiers[mod] for mod in battle_modifiers])

    output = int((((((2 * attackerlevel) / 5) + 2) * move['power'] * a / d) / 50 + 2) * modifier)
    return output


def use_move(atk_player, def_player):
    """Executes an attack, using Action data from player hash"""
    movedata = atk_player['Action'][1]
    # print('Move data:', movedata)
    # print('Accuracy:', movedata['accuracy'])
    print(atk_player['Name'] + "'s " + atk_player['Team'][0]['name'] + ' used ' + movedata['name'] + '!')

    # check if hit
    accuracy = movedata['accuracy']
    if random.randrange(100) > accuracy:
        print('you missed idiot!')
        return False

    # deal damage (add modifiers)
    def_hp = def_player['Team'][0]['stats'][0]
    dam = damage(atk_player['Team'][0], def_player['Team'][0], movedata, critboost=atk_player['Team'][0]['mod'][6])
    dam_percent = min(1, dam / def_hp)
    def_player['Team'][0]['stats'][0] -= dam
    if dam_percent == 1:
        dam = str(def_hp) + ' [' + str(dam) + ']'
    print('   It dealt', dam, '(' + "{:.2%}".format(dam_percent) + ')', 'damage!')

    # switch them out if ko'd, with ko=true
    if def_player['Team'][0]['stats'][0] <= 0:
        print('   ' + def_player['Name'] + "'s " + def_player['Team'][0]['name'] + ' was knocked out!')
        if len(def_player['Team']) == 1:  # If out of pokemon, attacker wins
            atk_player['Win'] = True
        else:  # Otherwise force switch
            teamlist = ''
            for i in range(1, len(def_player['Team'])):
                teamlist += '\n ' + str(i) + ': ' + str(def_player['Team'][i]['name'])
            while True:
                pkmn_id = input(def_player['Name'] + ', which pokemon would you like to switch to?' + teamlist + '\n')
                if pkmn_id in [str(x) for x in range(1, len(def_player['Team']))]:
                    def_player['Action'][1] = int(pkmn_id)
                    break
            switch_pkmn(def_player, ko=True)
        return True

    # check for effects
    return False


def switch_pkmn(player, ko=False):
    """Switches pokemon with selected member of party. Removes current lead if KO'd"""
    switch_id = player['Action'][1]
    switch_to = player['Team'][switch_id]
    # print([a['name'] for a in player['Team']])

    for i in range(1, 6):  # Reset stat mods
        player['Team'][0]['mod'][i] = 0

    if ko is True:
        player['Team'][0] = switch_to
        del player['Team'][switch_id]
    else:
        player['Team'][0], player['Team'][switch_id] = player['Team'][switch_id], player['Team'][0]

    # print([a['name'] for a in player['Team']])
    print(player['Name'] + ' switched to ' + player['Team'][0]['name'])


def attack_in_order():
    """Determines the order in which players attack, and executes the attacks"""
    p1_priority = player1['Action'][1]['priority']
    p2_priority = player2['Action'][1]['priority']
    p1_speed = player1['Team'][0]['stats'][5]
    p2_speed = player2['Team'][0]['stats'][5]

    if p1_priority > p2_priority:  # Priority
        first = player1
        second = player2
    elif p2_priority > p1_priority:
        first = player2
        second = player1
    elif p1_speed > p2_speed:  # Speed
        first = player1
        second = player2
    elif p2_speed > p1_speed:
        first = player2
        second = player1
    else:  # Random
        r = random.randrange(2)
        first = [player1, player2][r]
        second = [player2, player1][r]

    ko = use_move(first, second)
    if not ko:
        use_move(second, first)


# Action phase

while not player1['Win'] and not player2['Win']:
    print('====================')
    player1['Action'] = ask_for_action(player1)
    player2['Action'] = ask_for_action(player2)
    actions = [player1['Action'][0], player2['Action'][0]]

    if actions == ['switch', 'switch']:
        switch_pkmn(player1)
        switch_pkmn(player2)
    elif actions == ['switch', 'move']:
        switch_pkmn(player1)
        use_move(player2, player1)
    elif actions == ['move', 'switch']:
        switch_pkmn(player2)
        use_move(player1, player2)
    elif actions == ['move', 'move']:
        attack_in_order()
    else:
        print('uhoh, actions is', actions)

    print('End of turn!')

print('======================')
print('    End of battle!    ')

if player1['Win']:
    print(f"{player1['Name']} wins!".center(22))
elif player2['Win']:
    print(f"{player2['Name']} wins!".center(22))
else:
    print('uhoh, who won??')

print('======================')

# Crit: player['Team'][team_id]['mod'][6]

# player = {'Name': str, 'Team': [{pkmn},...], 'Action': [,], Win': T/F}

# player['Team'][n] = {'pokedex_number', 'level', 'iv', 'ev', 'nature', 'mod',
#                      'status', 'name', 'type1', 'type2', 'stats'}

# player['Team'][n]['moves'][m] = {'index', 'name', 'type', 'category',
#                                  'pp', 'power', 'accuracy', 'priority'}

# player['Action'] = ['move'/'switch', movedata/switch_id]

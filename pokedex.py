import argparse
import configparser
import re
import PyPDF2

# also needs win-unicode-console imported to display unicode characters?
# dumb extra characters present that will need to be fixed in output: ╦ø£Ø
# will need to add legendary/pseudolegendary/fossil tags later

parser = argparse.ArgumentParser(description='Reads and translate a PTU pokedex PDF into datafile format for PTU-trainer-generator')
parser.add_argument('-d', '--debug', action='store_true', help='Outputs more detailed information about page text and extracted data.')

args = parser.parse_args()

debug = args.debug

config = configparser.ConfigParser()
config.read('config.ini')

skipPages = config['pokedex']['pages_to_skip'].split(',')
# converting list of strings into list of ints
# pages in the PDF are indexed from 0 when read by python, rather than 1 as shown in the PDF, so these numbers need to have 1 subtracted
for x in skipPages:
	skipPages[skipPages.index(x)] = int(x)-1

# pages start from 0, rather than 1, but so does range(), so these don't need to be altered
startPage = int(config['pokedex']['start_page'])-1
endPage = int(config['pokedex']['end_page'])

output = configparser.ConfigParser()

# setting up regexes
name_match = re.compile(r'^\d+([\w ╦ø£\-\(\)]+)$', flags=re.M|re.I)
#name_match = re.compile(r'^\d+\s*\n?\s*([\w ╦ø£\-\(\)]+)$', flags=re.M|re.I) # attempting to get this to pick up Wormadam's Grass Cloak Form name, instead of just Wormadam
hp_match = re.compile(r'HP:\s*(\d+)', flags=re.M|re.I)
attack_match = re.compile(r'Attack:\s*(\d+)', flags=re.M|re.I)
defense_match = re.compile(r'Defense:\s*(\d+)', flags=re.M|re.I)
special_attack_match = re.compile(r'Special Attack:\s*(\d+)', flags=re.M|re.I)
special_defense_match = re.compile(r'Special Defense:\s*(\d+)', flags=re.M|re.I)
speed_match = re.compile(r'Speed:\s*(\d+)', flags=re.M|re.I)
# first match the whole line, then match for types on that
type_line_match = re.compile(r'(Type\s*:\s*\w+\s*/*\s*\w*)\s*$', flags=re.M|re.I)
type_match = re.compile(r'(Normal|Fighting|Flying|Poison|Ground|Rock|Bug|Ghost|Steel|Fire|Water|Grass|Electric|Psychic|Ice|Dragon|Dark|Fairy)', flags=re.M|re.I)
# separate abilities are listed on separate lines
basic_abilities_match = re.compile(r'(Basic Ability[\s\d]*:\s([\w\s\(\)\*╦Ø]+$))', flags=re.M|re.I)
advanced_abilities_match = re.compile(r'(Adv Ability[\s\d]*:\s([\w\s\(\)\*╦Ø]+$))', flags=re.M|re.I)
high_ability_match = re.compile(r'(High Ability:\s([\w\s\(\)\*╦Ø]+$))', flags=re.M|re.I)
height_match = re.compile(r'Height\s*:\s*(.+)\(([\w]+)\)', flags=re.M|re.I)
weight_match = re.compile(r'Weight\s*:\s*(.+)\(([\w]+)\)', flags=re.M|re.I)
gender_ratio_match = re.compile(r'Gender Ratio\s*:\s*([\d\.]+%\s*M|No Gender|Genderless)', flags=re.M|re.I)
# first match the whole line, then match for types on that
# notes: Pancham and a few others have Human-Like instead of Humanshape
# Pancham also uses a comma instead of /
egg_groups_line_match = re.compile(r'Egg\s*Group\s*:\s*(.*)', flags=re.M|re.I)
egg_groups_match = re.compile(r'(Field|Bug|Dragon|Fairy|Flying|Ground|Humanshape|Human\-Like|Indeterminate|Mineral|Monster|Plant|Water 1|Water 2|Water 3|Ditto|None)', flags=re.M|re.I)
# first match the whole line, then match for diets on that
# known values: (Ominvore|Omnivore|Nullivore|Carnivore|Herbivore|Phototroph|Terravore|Filter Feeder|Ergovore)
diets_line_match = re.compile(r'Diet\s*:\s*(.*)', flags=re.M|re.I)
diets_match = re.compile(r'(Ominvore|Omnivore|Nullivore|Carnivore|Herbivore|Phototroph|Terravore|Filter Feeder|Ergovore)', flags=re.M|re.I)
# first match the whole line, then match for habitats on that
habitats_line_match = re.compile(r'Habitat\s*:\s*(.*)', flags=re.M|re.I)
habitats_match = re.compile(r'(Forest|Grassland|Rainforest|Marsh|Cave|Mountain|Urban|Beach|Freshwater|Ocean|Taiga|Tundra|Arctic|Desert|\?+)', flags=re.M|re.I)
average_hatch_rate_match = re.compile(r'Average Hatch Rate:\s*(\d+) Days')
#skill_list_line_match = re.compile('Skill List\s*(.*)', flags=re.M|re.I)
#skill_list_match = re.compile('Athl (\dd\d\+*\d*), Acro (\dd\d\+*\d*), Combat (\dd\d\+*\d*), Stealth (\dd\d\+*\d*), Percep (\dd\d\+*\d*), Focus (\dd\d\+*\d*)', flags=re.M|re.I)
athl_match = re.compile(r'Athl\s*(\dd6\+*\d*)', flags=re.M|re.I|re.DOTALL)
acro_match = re.compile(r'Acro\s*(\dd6\+*\d*)', flags=re.M|re.I|re.DOTALL)
combat_match = re.compile(r'Combat\s*(\dd6\+*\d*)', flags=re.M|re.I|re.DOTALL)
stealth_match = re.compile(r'Stealth\s*(\dd6\+*\d*)', flags=re.M|re.I|re.DOTALL)
percep_match = re.compile(r'Percep\s*(\dd6\+*\d*)', flags=re.M|re.I|re.DOTALL)
focus_match = re.compile(r'Focus\s*(\dd6\+*\d*)', flags=re.M|re.I|re.DOTALL)
# again, first get all of the level up moves block, then run another match to extract each move
level_move_block_match = re.compile(r'Level Up Move List(.+?)(?:TM/HM Move List|Tutor Move List)', flags=re.M|re.I|re.DOTALL)
level_move_match = re.compile(r'((\d+)\s*([\w\s]+)\-\s(Normal|Fighting|Flying|Poison|Ground|Rock|Bug|Ghost|Steel|Fire|Water|Grass|Electric|Psychic|Ice|Dragon|Dark|Fairy))', flags=re.M|re.I)
tm_hm_move_block_match = re.compile(r'TM/HM Move List(.+?)(?:Tutor Move List|Egg Move List|Mega Evolution)', flags=re.M|re.I|re.DOTALL)
tm_hm_move_match = re.compile(r'((A?\d+)\s*([\w╦Ø]+(?:\s?\-?[\w╦Ø£]*)*))', flags=re.M|re.I)
egg_move_block_match = re.compile(r'Egg Move List(.+?)(?:Tutor Move List|Mega Evolution|$)', flags=re.I|re.DOTALL)
tutor_move_block_match = re.compile(r'Tutor Move List(.+?)(?:Mega Evolution|$|\*)', flags=re.I|re.DOTALL)
tutor_move_match = re.compile(r'([\w╦Ø]+(?:\s?\-?[\w╦Ø£]*)*\(?N?\)?),?', flags=re.M|re.I)
egg_move_match = re.compile(r'([\w╦Ø]+(?:\s?\-?[\w╦Ø£]*)*),?', flags=re.M|re.I)
evolutions_match = re.compile(r'\s*(\d+)\s\-\s(\w+\s?[FM]?)\b\s*(Fire Stone|Water Stone|Thunderstone|Leaf Stone|Shiny Stone|Dawn Stone|Dusk Stone|Moon Stone)?\s*(Superior Attack|Superior Defense|Equal Attack and Defense)?\s*(?:holding ([\w\W]+?))?,*\s*(?:Interact (?:wiht|with)\s?a?,* (Shelmet|Karrablast|Remoraid))?,*\s*(Male|Female)?\s*(?:(?:Minimum|Min\.) (\d+))?\s*(Male|Female)?\s*(?:learn (\w+\s?\w*))?\s*(in \w+\s?\w*)?\s*(?:at (Night))?\s*(Splits from Nincada)?$', flags=re.M|re.I)

# Pseudo-legendaries, fossils and legendaries; used later to identify pokemon that are in each group
pseudolegendary_pokemon = ['Dratini', 'Dragonair', 'Dragonite', 'Larvitar', 'Pupitar', 'Tyranitar', 'Bagon', 'Shelgon', 'Salamence', 'Beldum', 'Metang', 'Metagross', 'Gible', 'Gabite', 'Garchomp', 'Deino', 'Zweilous', 'Hydreigon', 'Goomy', 'Sliggoo', 'Goodra']
fossil_pokemon = ['Omanyte', 'Omastar', 'Kabuto', 'Kabutops', 'Lileep', 'Cradily', 'Anorith', 'Armaldo', 'Cranidos', 'Rampardos', 'Shieldon', 'Bastiodon', 'Tirtouga', 'Carracosta', 'Archen', 'Archeops', 'Tyrunt', 'Tyrantrum', 'Amaura', 'Aurorus', 'Aerodactyl']
# has an extra entry for Meloetta Step/Aria 'Form', rather than 'Forme', as it's misspelled in 1.05 plus
legendary_pokemon = ['Mew', 'Mewtwo', 'Genesect', 'Heatran', 'Articuno', 'Zapdos', 'Moltres', 'Raikou', 'Entei', 'Suicune', 'Regirock', 'Regice', 'Registeel', 'Regigigas', 'Cobalion', 'Terrakion', 'Virizion', 'Keldeo', 'Uxie', 'Mesprit', 'Azelf', 'Tornadus Incarnate Forme', 'Tornadus Therian Forme', 'Thundurus Incarnate Forme', 'Thundurus Therian Forme', 'Landorus Incarnate Forme', 'Landorus Therian Forme', 'Lugia', 'Ho-Oh', 'Latias', 'Latios', 'Phione', 'Manaphy', 'Celebi', 'Jirachi', 'Victini', 'Shaymin Land Forme', 'Shaymin Sky Forme', 'Diancie', 'Meloetta Aria Form', 'Meloetta Step Form', 'Meloetta Aria Forme', 'Meloetta Step Forme', 'Deoxys Normal Forme', 'Deoxys Attack Forme', 'Deoxys Defense Forme', 'Deoxys Speed Forme', 'Darkrai', 'Cresselia', 'Kyogre', 'Groudon', 'Rayquaza', 'Reshiram', 'Zekrom', 'Kyurem', 'Kyurem Zekrom Fusion Forme', 'Kyurem Reshiram Fusion Forme', 'Dialga', 'Palkia', 'Giratina Origin Forme', 'Giratina Altered Forme', 'Xerneas', 'Yveltal', 'Zygarde', 'Arceus', 'Hoopa Confined', 'Hoopa Unbound']

# open the PDF as an object
pdfFileObject = open(config['pokedex']['input'], 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObject)

for pageNo in range(startPage, endPage):
	if debug:
		print('\n', str(pageNo+1))
	if pageNo not in skipPages:
		pageObj = pdfReader.getPage(pageNo)
		#pageText = pageObj.extractText().encode("utf-8").decode("cp850")
		# the re.sub here gets rid of hyphenated linebreaks mid-word
		pageText = re.sub('\n-', '', pageObj.extractText().encode('utf-8').decode("cp850"))
		if debug:
			print(pageText)
		# Name
		name = ' '.join(name_match.findall(pageText)[0].title().split())
		if debug:
			print(name)
		# Base stats
		base_hp = hp_match.findall(pageText)[0]
		base_attack = attack_match.findall(pageText)[0]
		base_defense = defense_match.findall(pageText)[0]
		base_special_attack = special_attack_match.findall(pageText)[0]
		base_special_defense = special_defense_match.findall(pageText)[0]
		base_speed = speed_match.findall(pageText)[0]
		# Types
		type_line = type_line_match.findall(pageText)[0]
		matched_types = type_match.findall(type_line)
		if debug:
			print(matched_types)
		# Basic Abilities
		matched_basic_abilities = basic_abilities_match.findall(pageText)
		if debug:
			print(matched_basic_abilities)
		# Advanced Abilities
		matched_advanced_abilities = advanced_abilities_match.findall(pageText)
		if debug:
			print(matched_advanced_abilities)
		# High Ability
		matched_high_ability = high_ability_match.findall(pageText)
		if debug:
			print(matched_high_ability)
		# Height
		# need to replace 'Ôäó' with "'"
		# need to replace '´¼é' with '"'
		# height_match.findall(pageText)[0][0].replace('Ôäó', "'").replace('´¼é', '"').replace(' / ', ', ') # prints the height string with fixed symbols
		matched_height = height_match.findall(pageText)
		if debug:
			print(matched_height)
		height = matched_height[0][0].replace('Ôäó', "'").replace('´¼é', '"').replace(' / ', ', ')
		height_class = matched_height[0][1]
		# Weight
		matched_weight = weight_match.findall(pageText)
		if debug:
			print(matched_weight)
		weight = matched_weight[0][0].replace(' / ', ', ')
		weight_class = matched_weight[0][1]
		# Gender Ratio
		matched_gender_ratio = gender_ratio_match.findall(pageText)
		if debug:
			print(matched_gender_ratio)
		# Egg Groups
		egg_groups_line = egg_groups_line_match.findall(pageText)[0]
		matched_egg_groups = egg_groups_match.findall(egg_groups_line)
		if debug:
			print(matched_egg_groups)
		# Diets
		diets_line = diets_line_match.findall(pageText)[0]
		matched_diets = diets_match.findall(diets_line)
		if debug:
			print(matched_diets)
		# Habitats
		habitats_line = habitats_line_match.findall(pageText)[0]
		matched_habitats = habitats_match.findall(habitats_line)
		if debug:
			print(matched_habitats)
		# Average Hatch Rate
		# note: may not be present for all pokemon
		matched_average_hatch_rate = average_hatch_rate_match.findall(pageText)
		# may not actually be in any given entry
		# empty lists/sequences/tuples are False, so this works
		if debug:
			if matched_average_hatch_rate:
				print(matched_average_hatch_rate[0], "Days")
		# Skills
		matched_athl = athl_match.findall(pageText)
		matched_acro = acro_match.findall(pageText)
		matched_combat = combat_match.findall(pageText)
		matched_stealth = stealth_match.findall(pageText)
		matched_percep = percep_match.findall(pageText)
		matched_focus = focus_match.findall(pageText)
		if debug:
			print(matched_athl, matched_acro, matched_combat, matched_stealth, matched_percep, matched_focus)
		# Moves
		# Level Up Moves
		matched_level_move_block = level_move_block_match.findall(pageText)
		matched_level_moves = None
		if matched_level_move_block:
			matched_level_moves = level_move_match.findall(matched_level_move_block[0])
			if debug:
				print(matched_level_move_block)
				print(matched_level_moves)
		# TM/HM Moves
		matched_tm_hm_move_block = tm_hm_move_block_match.findall(pageText)
		matched_tm_hm_moves = None
		if matched_tm_hm_move_block:
			matched_tm_hm_moves = tm_hm_move_match.findall(matched_tm_hm_move_block[0])
			if debug:
				print(matched_tm_hm_move_block)
				print(matched_tm_hm_moves)
		# Egg Moves
		matched_egg_move_block = egg_move_block_match.findall(pageText)
		matched_egg_moves = None
		if matched_egg_move_block:
			matched_egg_moves = egg_move_match.findall(matched_egg_move_block[0])
			if debug:
				print(matched_egg_move_block)
				print(matched_egg_moves)
		# Tutor Moves
		matched_tutor_move_block = tutor_move_block_match.findall(pageText)
		matched_tutor_moves = None
		if matched_tutor_move_block:
			matched_tutor_moves = tutor_move_match.findall(matched_tutor_move_block[0])
			if debug:
				print(matched_tutor_move_block)
				print(matched_tutor_moves)
		# Evolutions and Family
		matched_evolutions = evolutions_match.findall(pageText)
		if debug:
			for evolution in matched_evolutions:
				print(evolution)
		
		# add to output config
		output[name] = {}
		output[name]['page'] = str(pageNo+1)
		if name in fossil_pokemon:
			output[name]['fossil'] = "True"
		else:
			output[name]['fossil'] = "False"
		if name in pseudolegendary_pokemon:
			output[name]['pseudolegendary'] = "True"
		else:
			output[name]['pseudolegendary'] = "False"
		if name in legendary_pokemon:
			output[name]['legendary'] = "True"
		else:
			output[name]['legendary'] = "False"
		output[name]['base_hp'] = base_hp
		output[name]['base_attack'] = base_attack
		output[name]['base_defense'] = base_defense
		output[name]['base_special_attack'] = base_special_attack
		output[name]['base_special_defense'] = base_special_defense
		output[name]['base_speed'] = base_speed
		output[name]['types'] = ', '.join(matched_types)
		basic_abilities = []
		for ability in matched_basic_abilities:
			basic_abilities.append(ability[1].replace('Ôäó', "'"))
		output[name]['basic_abilities'] = ', '.join(basic_abilities)
		advanced_abilities = []
		for ability in matched_advanced_abilities:
			advanced_abilities.append(ability[1].replace('Ôäó', "'"))
		output[name]['advanced_abilities'] = ', '.join(advanced_abilities)
		high_ability = []
		for ability in matched_high_ability:
			high_ability.append(ability[1].replace('Ôäó', "'"))
		output[name]['high_ability'] = ', '.join(high_ability)
		output[name]['height'] = height
		output[name]['height_class'] = height_class
		output[name]['weight'] = weight
		output[name]['weight_class'] = weight_class
		output[name]['egg_groups'] = ', '.join(matched_egg_groups)
		if matched_average_hatch_rate:
			output[name]['average_hatch_rate_days'] = matched_average_hatch_rate[0]
		output[name]['diets'] = ', '.join(matched_diets)
		output[name]['habitats'] = ', '.join(matched_habitats)
		output[name]['skills'] = ", ".join(["Athletics: " + matched_athl[0], "Acrobatics: " + matched_acro[0], "Combat: " + matched_combat[0], "Stealth: " + matched_stealth[0], "Perception: " + matched_percep[0], "Focus: " + matched_focus[0]])
		if matched_level_moves:
			level_moves = []
			for move in matched_level_moves:
				level_moves.append(move[1].strip() + ':' + move[2].strip())
			output[name]['level_moves'] = ', '.join(level_moves)
		if matched_tm_hm_moves:
			tm_moves = []
			hm_moves = []
			for move in matched_tm_hm_moves:
				if move[1][:1] == 'A':
					hm_moves.append(move[2].strip().replace('\n', '').replace('\t', ''))
				else:
					tm_moves.append(move[2].strip().replace('\n', '').replace('\t', ''))
			if len(hm_moves) > 0:
				output[name]['hm_moves'] = ', '.join(hm_moves)
			if len(tm_moves) > 0:
				output[name]['tm_moves'] = ', '.join(tm_moves)
		if matched_egg_moves:
			egg_moves = []
			for move in matched_egg_moves:
				egg_moves.append(move.strip().replace('\n', '').replace('\t', ''))
			if len(egg_moves) > 0:
				output[name]['egg_moves'] = ', '.join(egg_moves)
		if matched_tutor_moves:
			tutor_moves = []
			for move in matched_tutor_moves:
				tutor_moves.append(move.strip().replace('\n', '').replace('\t', ''))
			if len(tutor_moves) > 0:
				output[name]['tutor_moves'] = ', '.join(tutor_moves)
		# Evolution result indexes:
		# 00: Evolutionary tier/stage (eg. 1 for base form, 2 for forms evolving from that, 3 for forms evolving from stage 2 forms)
		# 01: Name of stage
		# 02: Attack/Defense/Equal split from Tyrogue
		# 03: Evolution stone, if required
		# 04: Hold item, if required
		# 05: Interact with other pokemon, if required
		# 06: Gender, if required (Gallade)
		# 07: Minimum level for evolution, if required
		# 08: Gender, if required (Vespiquen)
		# 09: Learned move, if required
		# 10: Weather
		# 11: Night, if required
		# 12: Shedinja special case; splits from Nincada on evolution to Ninjask)
		family = []
		for evolution in matched_evolutions:
			family.append(evolution[1].strip())
		output[name]['family'] = ', '.join(family)
	else:
		if debug:
			print(str(pageNo), 'skipped!')

with open(config['pokedex']['output'], 'w', encoding="utf8") as configfile:
	output.write(configfile)
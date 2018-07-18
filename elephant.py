import os
import sys
import time
import pickle
import click

DATABASE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db.p')

LEVELS_TO_INTERVALS = {
	0: 3600 * 0, 					# 0 hrs
	1: 3600 * 24,					# 24 hrs
	2: 3600 * 48, 					# 48 hrs
	3: 3600 * 24 * 7, 				# 1 week
	4: 3600 * 24 * 7 * 2, 			# 2 weeks
	5: 3600 * 24 * 7 * 4, 			# 1 month
	6: 3600 * 24 * 7 * 4 * 2, 		# 2 months
	7: 3600 * 24 * 7 * 4 * 4, 		# 4 months
	8: 3600 * 24 * 7 * 4 * 8, 		# 8 months
	9: 3600 * 24 * 7 * 4 * 16, 		# 16 months
	10: 3600 * 24 * 7 * 4 * 12 * 2, # 2 years
	11: 3600 * 24 * 7 * 4 * 12 * 4, # 4 years
}

def read_cards(path):
	"""Loads card list from database at 'path'"""
	try:
		with open(path, 'rb') as f:
			cards = pickle.load(f)
	except:
		cards = []
	return cards

def write_cards(cards, path):
	"""Writes card list to database at 'path', overriding previous contents"""
	with open(path, 'wb') as f:
		pickle.dump(cards, f)

@click.group()
def main():
	"""The elephant spaced repetition memory application"""
	pass

@main.command()
@click.argument("question")
@click.argument("answer")
def add(question, answer):
	"""Create a card
	
	Examples:
		$ elephant add "A great question?" "A great answer."
		$ elephant add 'Ultimate answer?' 42
	"""
	cards = read_cards(DATABASE)
	cards.append(
		{	
			'id': len(cards), 
			'question': question,
			'answer': answer,
			'time_created': time.time(),
			'level': 0,
			'last_reviewed': time.time(),
		}
	)
	write_cards(cards, DATABASE)

@main.command()
@click.option("--limit", default=10,
	help="The maximum number of cards to list")
def ls(limit):
	"""List some cards"""
	cards = read_cards(DATABASE)
	if cards:
		for card in cards[:limit]:
			click.echo("{}. {} --> {}".format(card['id'], card['question'], card['answer']))
	else:
		click.echo("No cards available")

@main.command()
@click.option("--limit", default=15,
	help="The maximum number of cards to list")
@click.argument("phrase")
def search(phrase, limit):
	"""Print cards containing phrase (case sensitive)"""
	got_hits = False
	cards = read_cards(DATABASE)
	if cards:
		for card in cards[:limit]:
			if limit <= 0:
				break
			if phrase in card['question'] or phrase in card['answer']:
				got_hits = True
				limit -= 1
				click.echo("{}. {} --> {}".format(card['id'], card['question'], card['answer']))
	else:
		click.echo("No cards available")
		sys.exit()
	if not got_hits:
		click.echo("Found no matches")

@main.command()
def quiz():
	"""Review cards you are at risk of forgetting"""
	cards = read_cards(DATABASE)
	if cards:
		current_time = time.time()
		todays_cards = [card for card in cards \
			if (card['last_reviewed']+LEVELS_TO_INTERVALS[card['level']]) < current_time]
		if not todays_cards:
			click.echo("No cards require reviewing now")
			sys.exit()
		click.echo("Starting review session... Spam Ctrl-C to stop")
		try:
			for card in todays_cards:
				click.echo("\nQUESTION : {} \n".format(card['question']))
				click.pause(info="(Press any key to show answer)")
				click.echo("\nANSWER : {} \n".format(card['answer']))
				mem_status = click.prompt("Did you remember it? yes/meh/no", default='yes')
				if mem_status in ['yes', 'YES', 'y', 'Y']:
					card['level'] += 1
					card['last_reviewed'] = time.time()
				elif mem_status in ['meh', 'MEH', 'm', 'M']:
					card['level'] = int(card['level'] / 1.5)
					card['last_reviewed'] = time.time()
				elif mem_status in ['no', 'NO', 'n', 'N']:
					card['level'] = 0
					card['last_reviewed'] = time.time()
				else:
					click.echo("Unrecognized response. Made no change to card state")
		except:
			click.echo("Ending session...")
		write_cards(cards, DATABASE)
	else:
		click.echo("No cards available")

@main.command()
@click.argument("ids", nargs=-1, type=int)
def rm(ids):
	"""Remove cards with listed ids"""
	number_cards_removed = 0
	cards = read_cards(DATABASE)
	if cards:
		i = 0
		while i < len(cards):
			if cards[i]['id'] in ids:
				cards.pop(i)
				number_cards_removed += 1
			else:
				i += 1
		write_cards(cards, DATABASE)
		click.echo("Removed {} cards".format(number_cards_removed))
	else:
		click.echo("No cards available")
	

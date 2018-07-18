import os
import click
import pickle

DATABASE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db.p')

@click.group()
def main():
	"""The elephant spaced repetition memory application"""
	pass

@main.command()
@click.argument("question")
@click.argument("answer")
def add(question, answer):
	"""Create a card"""
	try:
		with open(DATABASE, 'rb') as f:
			cards = pickle.load(f)
	except:
		with open(DATABASE, 'wb') as f:
			cards = []
	cards.append(
		{	
			'id': len(cards), 
			'question': question,
			'answer': answer,
		}
	)
	with open(DATABASE, 'wb') as f:
		pickle.dump(cards, f)

@main.command()
@click.option("--limit", default=10,
	help="The maximum number of cards to list")
def view(limit):
	"""Print some cards"""
	try:
		with open(DATABASE, 'rb') as f:
			cards = pickle.load(f)
			for card in cards[:limit]:
				click.echo("{}. {} --> {}".format(card['id'], card['question'], card['answer']))
	except:
		click.echo("No cards created yet")

@main.command()
@click.option("--limit", default=15,
	help="The maximum number of cards to list")
@click.argument("phrase")
def search(phrase, limit):
	"""Print cards containing phrase (case sensitive)"""
	got_hits = False
	try:
		with open(DATABASE, 'rb') as f:
			cards = pickle.load(f)
			for card in cards[:limit]:
				if limit <= 0:
					break
				if phrase in card['question'] or phrase in card['answer']:
					got_hits = True
					limit -= 1
					click.echo("{}. {} --> {}".format(card['id'], card['question'], card['answer']))
	except Exception as e:
		click.echo("Error: {}".format(e))
	if not got_hits:
		click.echo("Found no matches")

@main.command()
def quiz():
	"""Print cards one-by-one"""
	try:
		with open(DATABASE, 'rb') as f:
			cards = pickle.load(f)
			for card in cards:
				click.echo("\nQUESTION : {} \n".format(card['question']))
				click.prompt("Reveal?", default="Enter")
				click.echo("\nANSWER : {} \n".format(card['answer']))
				if not click.confirm("Continue?", default=True):
					break
	except:
		click.echo("No cards created yet")

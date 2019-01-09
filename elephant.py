import os
import sys
import time
import pickle
import click

CARDS_DATABASE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cards.p')
METADATA_DATABASE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'metadata.p')

LEVELS_TO_INTERVALS = {
    0: 3600 * 0,                    # 0 hrs
    1: 3600 * 24,                   # 24 hrs
    2: 3600 * 48,                   # 48 hrs
    3: 3600 * 24 * 7,               # 1 week
    4: 3600 * 24 * 7 * 2,           # 2 weeks
    5: 3600 * 24 * 7 * 4,           # 1 month
    6: 3600 * 24 * 7 * 4 * 2,       # 2 months
    7: 3600 * 24 * 7 * 4 * 4,       # 4 months
    8: 3600 * 24 * 7 * 4 * 8,       # 8 months
    9: 3600 * 24 * 7 * 4 * 16,      # 16 months
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

def get_next_id(path):
    """Gets the next id from the database at the given path and increments the value in this database"""
    try:
        with open(path, 'rb') as f:
            data = pickle.load(f)
            id = data['next_id']
            data['next_id'] += 1
    except:
        id, data = 0, {}
        data['next_id'] = id + 1
    with open(path, 'wb') as f:
        pickle.dump(data, f)
    return id
    
@click.group()
def main():
    """The elephant spaced repetition memory application"""
    pass

@main.command()
@click.argument("question")
@click.argument("answer")
def add(question, answer):
    """Create a card"""
    cards = read_cards(CARDS_DATABASE)
    cards.append(
        {   
            'id': get_next_id(METADATA_DATABASE), 
            'question': question,
            'answer': answer,
            'time_created': time.time(),
            'level': 0,
            'last_reviewed': time.time(),
        }
    )
    write_cards(cards, CARDS_DATABASE)

@main.command()
@click.option("--limit", default=10,
    help="The maximum number of cards to list")
def ls(limit):
    """List some cards"""
    cards = read_cards(CARDS_DATABASE)
    if cards:
        for card in cards[:limit]:
            click.echo("#{}: {} --> {}".format(card['id'], card['question'], card['answer']))
    else:
        click.echo("No cards available")

@main.command()
@click.argument("ids", nargs=-1, type=int)
def rm(ids):
    """Remove cards with listed ids"""
    number_cards_removed = 0
    cards = read_cards(CARDS_DATABASE)
    if cards:
        i = 0
        while i < len(cards):
            if cards[i]['id'] in ids:
                cards.pop(i)
                number_cards_removed += 1
            else:
                i += 1
        write_cards(cards, CARDS_DATABASE)
        click.echo("Removed {} cards".format(number_cards_removed))
    else:
        click.echo("No cards available")

@main.command()
@click.option("--limit", default=15,
    help="The maximum number of cards to list")
@click.argument("phrases", nargs=-1)
def search(phrases, limit):
    """Print cards whose question or answer combined contain all inputed phrases"""
    got_hits = False
    cards = read_cards(CARDS_DATABASE)
    if cards:
        for card in cards[:limit]:
            if limit <= 0:
                break
            if all([(phrase in card['question'] or phrase in card['answer']) for phrase in phrases]):
                got_hits = True
                limit -= 1
                click.echo("#{}: {} --> {}".format(card['id'], card['question'], card['answer']))
    else:
        click.echo("No cards available")
        sys.exit()
    if not got_hits:
        click.echo("Found no matches")

@main.command()
@click.argument("phrases", nargs=-1)
def quiz(phrases):
    """Review cards that you are at risk of forgetting and that contain PHRASES if given"""
    cards = read_cards(CARDS_DATABASE)
    if cards:
        current_time = time.time()
        todays_cards = [card for card in cards \
            if ((card['last_reviewed']+LEVELS_TO_INTERVALS[card['level']]) < current_time) \
            and all([(phrase in card['question'] or phrase in card['answer']) for phrase in phrases])]
        if not todays_cards:
            click.echo("Cards don't require reviewing now")
            sys.exit()
        click.echo("Starting review session... Spam Ctrl-C to stop")
        try:
            for card in todays_cards:
                print_card("QUESTION", card['question'])
                click.pause(info="(Press any key to show answer)")
                print_card("ANSWER", card['answer'])
                mem_status = click.prompt("Did you remember it? yes/meh/no", default='yes')
                if mem_status in ['yes', 'YES', 'y', 'Y']:
                    card['level'] += (1 if card['level'] < 11 else 0)
                    card['last_reviewed'] = time.time()
                elif mem_status in ['meh', 'MEH', 'm', 'M']:
                    card['level'] = int(card['level'] / 1.99)
                    card['last_reviewed'] = time.time()
                elif mem_status in ['no', 'NO', 'n', 'N']:
                    card['level'] = 0
                    card['last_reviewed'] = time.time()
                else:
                    click.echo("Unrecognized response. Made no change to card state")
        except KeyboardInterrupt:
            click.echo("Ending session...")
        write_cards(cards, CARDS_DATABASE)
    else:
        click.echo("No cards available")

def print_card(title, text, width=40):
    """Prints the text in a box with a title on top

    TODO:
        -Center justify the text, as opposed to left justify?
    """
    DOUBLE_MARGIN = 4 # So a horizontal margin of n --> n*2
    MARGIN = " " * (DOUBLE_MARGIN // 2)
    assert len(title) < (width - DOUBLE_MARGIN - 2), "Title is too long for card"
    assert width % 2 == 0, "Width must be divisible by two"
    def split_text_into_lines(text):
        words = text.split(' ')
        assert all([len(word) < width for word in words])
        lines = []
        line = ""
        i = 0
        while i < len(words):
            if len(line) + len(words[i]) + 1 <= width - DOUBLE_MARGIN - 2: # +1 for space, -2 for border
                line += words[i] + " "
                i += 1
            else:
                lines.append(line)
                line = ""
        lines.append(line)
        return lines
    lines = split_text_into_lines(text)

    click.echo("+" + ("-" * (width - 2)) + "+")
    title = title if len(title) % 2 == 0 else title + " "
    title_margin = " " * ((width - 2 - len(title)) // 2)
    click.echo("|" + title_margin + title + title_margin + "|")
    click.echo("|" + " " * (width - 2) + "|")

    for line in lines:
        click.echo("|" + MARGIN + line + (' ' * (width - len(line) - DOUBLE_MARGIN - 2)) + MARGIN + "|")
    click.echo("|" + " " * (width - 2) + "|")
    click.echo("+" + ("-" * (width - 2)) + "+")

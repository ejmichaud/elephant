import os
import sys
import time

import click
import sqlite3

DATABASE = os.path.join(os.path.dirname(os.path.realpath('__file__')), 'data.db')
# METADATA_DATABASE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'metadata.p')

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

class Card:
    """A 'card'.

    This app allows users to make two kinds of records: 'cards' & 'notes'. 
    This class represents a 'card', which has a question and an answer, and
    contains metadata for the spaced-repetition system.
    
    Attributes:
        id (int): A unique numeric id.
        question (str): The 'question' on the card.
        answer (str): The 'answer' on the card.
        level (int): A spaced-repetition score (see LEVELS_TO_INTERVALS).
        time_created (float): The UTC UNIX time of the card's creation.
        last_reviewed (float): The UTC UNIX time when the card was last quized.
    
    """

    def __init__ (self, id, question, answer, level, 
                        time_created, last_reviewed):
        """The initializer for the class."""
        self.id = id
        self.question = question
        self.answer = answer
        self.level = level
        self.time_created = time_created
        self.last_reviewed = last_reviewed

    @classmethod
    def fromtuple(self, data):
        return self(data[0], data[1], data[2], data[3], data[4], data[5])

def read_all_cards():
    """Loads card list from global variable DATABASE"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM cards')
    rows = c.fetchall()
    conn.close()
    return [Card.fromtuple(row) for row in rows]

# def write_cards(cards, path):
#     """Writes card list to database at 'path', overriding previous contents"""
#     with open(path, 'wb') as f:
#         pickle.dump(cards, f)

def get_next_id():
    """Gets the next id from the DATABASE and increments its value
    in the database. """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT value FROM metadata WHERE key="next_id"')
    next_id = int(c.fetchone()[0])
    tup = (str(next_id + 1), )
    c.execute('UPDATE metadata SET value=? WHERE key="next_id"', tup)
    conn.commit()
    conn.close()
    return next_id
    
@click.group()
def main():
    """The elephant spaced repetition memory application"""
    pass

@main.command()
@click.argument("question")
@click.argument("answer")
def add(question, answer):
    """Create a card"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    new_row = (
            get_next_id(), 
            question,
            answer,
            0,
            time.time(),
            time.time()
        )
    c.execute('INSERT INTO cards VALUES (?,?,?,?,?,?)', new_row)
    conn.commit()
    conn.close()

@main.command()
@click.option("--limit", default=10,
    help="The maximum number of cards to list")
def ls(limit):
    """List some cards"""
    if limit == 0:
        click.echo("Showing 0 cards ;)")
        return
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM cards LIMIT ?', (limit,))
    cards = [Card.fromtuple(row) for row in c.fetchall()]
    conn.close()
    if cards:
        for card in cards:
            click.echo("#{}: {} --> {}".format(card.id, 
                    card.question, card.answer))
    else:
        click.echo("No cards available")

@main.command()
@click.argument("ids", nargs=-1, type=int)
def rm(ids):
    """Remove cards with listed ids"""
    number_cards_removed = 0
    removed_cards = []
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    for identifier in ids:
        c.execute('SELECT * FROM cards WHERE id=?', (identifier,))
        num_cards_found = len(c.fetchall())
        if num_cards_found == 1:
            c.execute('DELETE FROM cards WHERE id=?', (identifier,))
            removed_cards.append(int(identifier))
            number_cards_removed += 1
        elif num_cards_found >= 2:
            raise Exception("Found {} cards with id {}. \
                Should be either 0 or 1".format(number_cards_found, 
                    identifier))
    conn.commit()
    conn.close()
    if number_cards_removed > 0:
        click.echo("Removed cards: {}".format(removed_cards))
    else:
        click.echo("Removed no cards")

@main.command()
@click.option("--limit", default=15,
    help="The maximum number of cards to list")
@click.argument("phrases", nargs=-1)
def search(phrases, limit):
    """Print cards whose question or answer combined contain all inputed phrases"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    query = 'SELECT * FROM cards WHERE '
    for phrase in phrases:
        query += '(instr("question", "{}") > 0 OR instr("answer", "{}") > 0)'.format(
            phrase, phrase)
        query += ' AND '
    query = query[:-4]
    query += ' LIMIT {}'.format(limit)
    c.execute(query)
    cards = [Card.fromtuple(row) for row in c.fetchall()]
    conn.close()
    for card in cards:
        click.echo("#{}: {} --> {}".format(card.id, card.question, card.answer))
    if not cards:
        click.echo("Found no matches")

@main.command()
@click.argument("phrases", nargs=-1)
def quiz(phrases):
    """Review cards that you are at risk of forgetting and that contain PHRASES if given"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    query = 'SELECT * FROM cards WHERE '
    for phrase in phrases:
        query += '(instr("question", "{}") > 0 OR instr("answer", "{}") > 0)'.format(
            phrase, phrase)
        query += ' AND '
    query = query[:-4]
    c.execute(query)
    cards = [Card.fromtuple(row) for row in c.fetchall()]
    if cards:
        current_time = time.time()
        todays_cards = [card for card in cards \
            if ((card.last_reviewed+LEVELS_TO_INTERVALS[card.level]) < current_time)]
        if not todays_cards:
            click.echo("No cards require revieiwng now.")
            sys.exit()
        click.echo("Starting review session... Spam Ctrl-C to stop")
        try:
            for card in todays_cards:
                print_card("QUESTION", card.question)
                click.pause(info="(Press any key to show answer)")
                print_card("ANSWER", card.answer)
                mem_status = click.prompt("Did you remember it? yes/meh/no", default='yes')
                if mem_status in ['yes', 'YES', 'y', 'Y']:
                    tup = (card.level + (1 if card.level < 11 else 0), card.id)
                    c.execute('UPDATE cards SET level=? WHERE id=?', tup)
                    tup = (time.time(), card.id)
                    c.execute('UPDATE cards SET last_reviewed=? WHERE id=?', tup)
                elif mem_status in ['meh', 'MEH', 'm', 'M']:
                    tup = (card.level / 1.99, card.id)
                    c.execute('UPDATE cards SET level=? WHERE id=?', tup)
                    tup = (time.time(), card.id)
                    c.execute('UPDATE cards SET last_reviewed=? WHERE id=?', tup)
                elif mem_status in ['no', 'NO', 'n', 'N']:
                    tup = (0, card.id)
                    c.execute('UPDATE cards SET level=? WHERE id=?', tup)
                    tup = (time.time(), card.id)
                    c.execute('UPDATE cards SET last_reviewed=? WHERE id=?', tup)
                else:
                    click.echo("Unrecognized response. Made no change to card state")
        except KeyboardInterrupt:
            click.echo("Ending session...")
        conn.commit()
        conn.close()
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

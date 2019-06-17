```
 __
'. \
 '- \
  / /_         .---.
 / | \\,.\/--.//    )                       +-------------------+
 |  \//        )/  /                        |                   |
  \  ' ^ ^    /    )____.----..  6          |  A spaced         |
   '.____.    .___/            \._)         |  repetition       |
      .\/.                      )           |  memory system    |
       '\                       /           |  for the command  |
       _/ \/    ).        )    (            |  line!            |
      /#  .!    |        /\    /            |                   |
      \  C// #  /'---+-''/ #  /             +-------------------+
   .   'C/ |    |    |   |    |mrf  ,
   \), .. .'OOO-'. ..'OOO'OOO-'. ..\(,

```

## Motivation
Spaced repetition memory systems are great, but popular solutions like [Anki](https://apps.ankiweb.net/) are bulky and have ugly interfaces. This system is a lightweight solution for recording and reviewing knowledge and runs purely in the command line, the easiest way to augment your memory.

An elephant never forgets!

## Requires
Should be compatible with Python 2 & 3 on MacOS, Linux, and Windows! The only 3rd party library installed with the package will be [Click](http://click.pocoo.org/6/).

## Installation
```
$ git clone https://github.com/ejmichaud/elephant.git
$ cd elephant
$ pip install .
```
If you somehow compromise the application's sqlite3 database, you can reset it by running `. db_init.sh` from the repo root directory. This will delete the current `data.db` file, create a new one, and add `cards` and `metadata` tables. 

## Tutorial
```
$ elephant
Usage: elephant [OPTIONS] COMMAND [ARGS]...

  The elephant spaced repetition memory application

Options:
  --help  Show this message and exit.

Commands:
  add     Create a card
  ls      List some cards
  quiz    Review cards that you are at risk of...
  rm      Remove cards with listed ids
  search  Print cards whose question or answer combined...
```

### To add a card:
```
$ elephant add "Your question?" "Your answer."
$ elephant add 'another question' answer
$ elephant add QUESTION 42
```
As you can see, the system is quite flexible to different ways of formatting text. Any question or answer over one word needs to be enclosed in double or single quotes.

### To view cards (and their ids):
```
$ elephant ls
#0: Your question --> Your answer.
#1: another question --> answer
#2: QUESTION --> 42

$ elephant ls --limit 1
#0: Your question --> Your answer.
```

### To search your card deck:
```
$ elephant search 42
#2: QUESTION --> 42

$ elephant search question
#0: Your question --> Your answer.
#1: another question --> answer
#2: QUESTION --> 42

$ elephant search --limit 1 question
#0: Your question --> Your answer.
```

### To remove a card:
```
$ elephant rm 0 1
Removed cards: [0, 1]

$ elephant ls
#2: QUESTION --> 42
```
`elephant rm` takes an arbitrary number of card ids as arguments and removes them.

### To review cards:
```
$ elephant quiz
Starting review session... Spam Ctrl-C to stop
+--------------------------------------+
|               QUESTION               |
|                                      |
|  QUESTION                            |
|                                      |
+--------------------------------------+
(Press any key to show answer)

+--------------------------------------+
|                ANSWER                |
|                                      |
|  42                                  |
|                                      |
+--------------------------------------+
Did you remember it? yes/meh/no [yes]: 

...
```
And the process continues until you go through all the cards that the spaced repetition system decides it's time for you to review. Version 1.0 features an extremely simple system (far less sophistocated than Anki) that gives each card a 'level'. When cards are created they are given a level of 0. When quized, if you answer 'yes' to the prompt (you remembered it), this level is increased by 1. If you answer 'meh', the level is halved. If you answer 'no', the level is reset back to 0. The higher a card's level, the longer it is before you will be quizzed on it again:

| level | time before you'll see it again |
| ----- | ------------------------------- |
| 0		| 0 minutes						  |
| 1 	| 24 hours						  |
| 2		| 48 hours						  |
| 3 	| 1 week						  |
| 4 	| 2 weeks						  |
| 5 	| 1 month						  |
| 6 	| 2 months						  |
| 7 	| 4 months						  |
| 8 	| 8 months						  |
| 9 	| 16 months						  |
| 10 	| 2 years						  |
| 11 	| 4 years						  |

*If you find bugs, post an 'issue' to the repository, or email me at eric.michaud99 [at]gmail[dot]com*
# elephant
A spaced repetition memory system for the command line!

```
 __                 
'. \                
 '- \               
  / /_         .---.
 / | \\,.\/--.//    )
 |  \//        )/  / 
  \  ' ^ ^    /    )____.----..  6
   '.____.    .___/            \._) 
      .\/.                      )
       '\                       /
       _/ \/    ).        )    (
      /#  .!    |        /\    /
      \  C// #  /'-----''/ #  / 
   .   'C/ |    |    |   |    |mrf  ,
   \), .. .'OOO-'. ..'OOO'OOO-'. ..\(,
```

## Motivation
Spaced repetition memory systems are great, but popular solutions like [Anki](https://apps.ankiweb.net/) are bulky and have ugly interfaces. This system is a lightweight solution for recording and reviewing knowledge and runs purely in the command line, the easiest way to augment your memory.

An elephant never forgets!

## Installation
```
$ git clone https://github.com/ejmichaud/elephant.git
$ cd elephant
$ pip install .
```

## Tutorial
```
Usage: elephant [OPTIONS] COMMAND [ARGS]...

  The elephant spaced repetition memory application

Options:
  --help  Show this message and exit.

Commands:
  add     Create a card
  quiz    Print cards one-by-one
  search  Print cards containing phrase (case...
  view    Print some cards
```
#!/usr/bin/env python3.8

import argparse
import os
import sys
from tokenize import generate_tokens

from story6.tokenizer import Tokenizer
from story6.generator3 import generate
from story6.visualizer import Visualizer

argparser = argparse.ArgumentParser()
argparser.add_argument("grammar", nargs="?", default="story6/toy.gram", help="Grammar file (toy.gram)")
argparser.add_argument("-o", "--output", help="Output file (toy.py)")
argparser.add_argument("-c", "--classname", help="Output class name (ToyParser)")
argparser.add_argument("-v", "--visualize", action="store_true", help="Use visualizer")
argparser.add_argument("-b", "--backup", action="store_true", help="Use old grammar parser")


def main():
    args = argparser.parse_args()
    file = args.grammar
    outfile = args.output
    if not outfile:
        head, tail = os.path.split(file)
        base, ext = os.path.splitext(tail)
        outfile = os.path.join(head, base + ".py")
    classname = args.classname

    if args.backup:
        from story6.grammar import GrammarParser
    else:
        from story6.grammarparser import GrammarParser

    print("Reading", file)
    with open(file) as f:
        tokengen = generate_tokens(f.readline)
        vis = None
        if args.visualize:
            vis = Visualizer()
        try:
            tok = Tokenizer(tokengen, vis)
            p = GrammarParser(tok)
            grammar = p.start()
            if vis:
                vis.done()
        finally:
            if vis:
                vis.close()

    if not grammar:
        if tok.tokens:
            last = tok.tokens[-1]
            print(f"Line {last.start[0]}:")
            print(last.line)
            print(" "*last.start[1] + "^")
            breakpoint()
        sys.exit("SyntaxError")

    print(repr(grammar))
    print(str(grammar))

    if not classname:
        classname = grammar.metas_dict.get("class")
        if not classname:
            tail = os.path.basename(file)
            base, ext = os.path.splitext(tail)
            classname = base.title() + "Parser"


    print("writing class", classname, "to", outfile, file=sys.stderr)
    with open(outfile, "w") as stream:
        generate(grammar, classname, stream)


if __name__ == '__main__':
    main()

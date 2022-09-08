#!/usr/bin/env python3

import chess.pgn
import sys

def process_pgn(pgn):
    while True:
        game = chess.pgn.read_game(pgn)
        if not game:
            break
        print(game.headers)

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        with open(arg) as pgn:
            process_pgn(pgn)
else:
    process_pgn(sys.stdin)

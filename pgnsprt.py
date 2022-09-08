#!/usr/bin/env python3

import chess.pgn
import sys

results = {
    'win': 0,
    'loss': 0,
    'draw': 0,
}

players = {}

def process_pgn(pgn):
    while True:
        headers = chess.pgn.read_headers(pgn)
        if not headers:
            break

        if not players:
            players['us'] = headers['Black']
            players['them'] = headers['White']

        if headers['White'] == players['us'] and headers['Black'] == players['them']:
            if headers['Result'] == '1/2-1/2':
                results['draw'] += 1
            elif headers['Result'] == '1-0':
                results['win'] += 1
            elif headers['Result'] == '0-1':
                results['loss'] += 1
        elif headers['Black'] == players['us'] and headers['White'] == players['them']:
            if headers['Result'] == '1/2-1/2':
                results['draw'] += 1
            elif headers['Result'] == '1-0':
                results['loss'] += 1
            elif headers['Result'] == '0-1':
                results['win'] += 1

    total = results['win'] + results['loss'] + results['draw']
    ratio = (results['win'] + 0.5 * results['draw']) / total
    print(f"Score of {players['us']} vs {players['them']}: {results['win']} - {results['loss']} - {results['draw']}  [{ratio:.3f}] {total}")

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        with open(arg) as pgn:
            process_pgn(pgn)
else:
    process_pgn(sys.stdin)

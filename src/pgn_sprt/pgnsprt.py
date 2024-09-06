#!/usr/bin/env python3

import chess.pgn

import argparse
import math
import sys

class ResultCount:
    def __init__(self):
        self.win = 0
        self.draw = 0
        self.loss = 0

    def __bool__(self):
        return any(r > 0 for r in self.values())

    @property
    def total(self):
        return sum(self.values())

    @property
    def can_sprt(self):
        return sum([r > 0 for r in self.values()]) >= 2

    def values(self):
        return [self.win, self.draw, self.loss]

# Based on https://github.com/lucasart/c-chess-cli/blob/master/src/sprt.c
def elo_to_score(elo):
    return 1 / (1 + math.pow(10, -elo / 400))

class Sprt:
    def __init__(self, *, elo0, elo1, alpha, beta):
        self.lower = math.log(beta / (1. - alpha))
        self.upper = math.log((1 - beta) / alpha)

        self.s0 = elo_to_score(elo0)
        self.s1 = elo_to_score(elo1)

    def llr(self, results):
        if not results.can_sprt:
            return 0

        score = (results.win + 0.5 * results.draw) / results.total
        return (self.s1 - self.s0) * (2 * score - self.s0 - self.s1) / (
            2 * ((results.win + 0.25 * results.draw) / results.total - score * score) / results.total
        )

    def finished(self, results):
        llr = self.llr(results);

        accepted = ""
        if llr > self.upper:
            accepted = ". H1 accepted."
        elif llr < self.lower:
            accepted = ". H0 accepted."

        print(f"SPRT: LLR = {llr:.3f} [{self.lower:.3f},{self.upper:.3f}]{accepted}")
        return accepted != ""

def process_pgn(pgn, players, results):
    while True:
        headers = chess.pgn.read_headers(pgn)
        if not headers:
            break

        if 'us' not in players:
            if headers['Black'] != players.get('them'):
                players['us'] = headers['Black']
            elif headers['White'] != players.get('them'):
                players['us'] = headers['White']
        if 'them' not in players:
            if headers['Black'] != players.get('us'):
                players['them'] = headers['Black']
            elif headers['White'] != players.get('us'):
                players['them'] = headers['White']

        if headers['White'] == players['us'] and headers['Black'] == players['them']:
            if headers['Result'] == '1/2-1/2':
                results.draw += 1
            elif headers['Result'] == '1-0':
                results.win += 1
            elif headers['Result'] == '0-1':
                results.loss += 1
        elif headers['Black'] == players['us'] and headers['White'] == players['them']:
            if headers['Result'] == '1/2-1/2':
                results.draw += 1
            elif headers['Result'] == '1-0':
                results.loss += 1
            elif headers['Result'] == '0-1':
                results.win += 1

def status(players, results, sprt):
    if not results:
        return False
    score = (results.win + 0.5 * results.draw) / results.total
    print(f"Score of {players['us']} vs {players['them']}: {results.win} - {results.loss} - {results.draw}  [{score:.3f}] {results.total}")
    return sprt.finished(results)

def build_arg_parser():
    parser = argparse.ArgumentParser(description='Run SPRT on games from PGN files.')
    parser.add_argument('pgn_files', metavar='PGN', type=str, nargs='*', help='PGN files')
    parser.add_argument('--player0', type=str, default='')
    parser.add_argument('--player1', type=str, default='')
    parser.add_argument('--elo0', type=int, default=0)
    parser.add_argument('--elo1', type=int, default=4)
    parser.add_argument('--alpha', type=float, default=0.05)
    parser.add_argument('--beta', type=float, default=0.05)
    parser.add_argument('--games', type=int, default=0)
    return parser

def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    finished = False
    results = ResultCount()
    players = {}
    if args.player0:
        players['them'] = args.player0
    if args.player1:
        players['us'] = args.player1

    sprt = Sprt(elo0=args.elo0, elo1=args.elo1, alpha=args.alpha, beta=args.beta)

    if args.pgn_files:
        for f in args.pgn_files:
            with open(f) as pgn:
                print(f)
                process_pgn(pgn, players, results)
                finished = status(players, results, sprt)
    else:
        process_pgn(sys.stdin, players, results)
        finished = status(players, results, sprt)

    if finished or (args.games and results.total >= args.games):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()

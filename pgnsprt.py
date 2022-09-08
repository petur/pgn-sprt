#!/usr/bin/env python3

import chess.pgn
import math
import sys

class ResultCount:
    def __init__(self):
        self.win = 0
        self.draw = 0
        self.loss = 0

    @property
    def total(self):
        return self.win + self.draw + self.loss

    @property
    def can_sprt(self):
        return sum([r > 0 for r in [self.win, self.draw, self.loss]]) >= 2

# Based on https://github.com/lucasart/c-chess-cli/blob/master/src/sprt.c
def elo_to_score(elo):
    return 1 / (1 + math.pow(10, -elo / 400))

class Sprt:
    def __init__(self, *, elo0=0., elo1=4., alpha=0.05, beta=0.05):
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

        if not players:
            players['us'] = headers['Black']
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
    score = (results.win + 0.5 * results.draw) / results.total
    print(f"Score of {players['us']} vs {players['them']}: {results.win} - {results.loss} - {results.draw}  [{score:.3f}] {results.total}")
    return sprt.finished(results)

def main():
    finished = False
    results = ResultCount()
    players = {}

    sprt = Sprt()

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            with open(arg) as pgn:
                print(arg)
                process_pgn(pgn, players, results)
                finished = status(players, results, sprt)
    else:
        process_pgn(sys.stdin, players, results)
        finished = status(players, results, sprt)

    if finished:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()

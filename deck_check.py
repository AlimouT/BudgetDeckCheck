import argparse
from dataclasses import dataclass
import re
import os
import time
from typing import Any
import requests

CARDS_WITH_DIGITS = {'Borrowing 100,000 Arrows', '1996 World Champion', 'Guan Yu\'s 1,000-Li March'}
BASIC_LANDS = {'Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes'}
CARDMULT_RE = r'\d+\s?x?\s*'

@dataclass
class Card:
    name: str
    price: float = 999
    notes: Any = None


class Deck:
    def __init__(self, card_list=None, save_name='temp'):
        if card_list is not None:
            cards = []
            for card_name in card_list:
                cards.append(Card(card_name))
            self.card_list = cards
        else:
            self.card_list = None
        self.deck_info = None
        self.save_name = save_name

    def price_deck(self):
        if self.card_list is None:
            print('Decklist undefined')
            return
        self.deck_info = None
        # Get card data
        base_url = 'https://api.scryfall.com/cards/search'
        for card in self.card_list:
            if card.name in BASIC_LANDS:
                card.price = 0
                continue
            payload = {'q':f'!"{card.name}" f:c usd>0'}
            response = requests.get(base_url, params=payload)
            if response.status_code != 200:
                print(f'ERROR [{card.name}]\tBad Response {response}')
                card.notes = "BAD RESP"
                continue
            data = response.json()['data']
            if len(data) > 1:
                print(f'ERROR [{card.name}]\tToo many cards found {len(data)}')
                card.notes = "TOO MANY"
                continue
            regular_price = data[0]['prices']['usd']
            foil_price = data[0]['prices']['usd_foil']
            if regular_price is not None and foil_price is not None:
                card.price = min(float(regular_price), float(foil_price))
            elif regular_price is None and foil_price is None:
                card.notes = 'MIS $$$$'
            elif regular_price is not None:
                card.price = float(regular_price)
            elif foil_price is not None:
                card.price = float(foil_price)
            time.sleep(.01)

    def __str__(self):
        if self.deck_info is not None:
            return self.deck_info
        decklist = []
        problem_cards = []
        deck_price = 0
        for card in self.card_list:
            if card.notes is None:
                decklist.append(f'{card.price:6.2f}\t{card.name}')
                deck_price = deck_price + card.price
            else:
                problem_cards.append(f'{card.notes}\t{card.name}')
        decklist_str = '\n'.join(decklist)
        problem_str = '\n'.join(problem_cards)
        if len(problem_cards) > 0:
            summary_str = f'NOT ALL CARDS ARE COUNTED.\nTotal cost: ${deck_price:.2f}\n'
        else:
            summary_str = f'Total cost: ${deck_price:.2f}\n'
        self.deck_info = '\n\n'.join([summary_str,decklist_str,problem_str,summary_str])
        return self.deck_info

    def save(self, file_name=None):
        if file_name is None:
            file_name = self.save_name
        with open(f'output/{file_name}', 'w') as file:
            file.write(str(self))


def get_list(file_name):
    deck_path = f'decklists/{file_name}'
    if not os.path.exists(deck_path):
        print(f'No file found at\t{deck_path}')
        return None
    with open(deck_path, 'r') as file:
        text_lines = [line.strip() for line in file.readlines() if line.strip() != '']

    # The script won't work with the card "1996 World Champion"
    card_list = [re.sub(CARDMULT_RE, '', text) for text in text_lines if not text.startswith('#')]
    return Deck(card_list, file_name)


def check_deck(deck_file):
    temp_deck = get_list(deck_file)
    temp_deck.price_deck()
    temp_deck.save()


def test():
    pass


def main():
    deck_file = 'test.txt'

    parser = argparse.ArgumentParser()
    parser.add_argument('deck', nargs='?', default=None, help='File name of deck to check.')
    args = parser.parse_args()
    if args.deck is not None:
        deck_file = f'{args.deck}'
    check_deck(deck_file)


if __name__ == "__main__":
    main()

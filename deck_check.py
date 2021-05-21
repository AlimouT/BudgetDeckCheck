from dataclasses import dataclass
from typing import Any
import os
import time
import requests

CARDS_WITH_DIGITS = {'Borrowing 100,000 Arrows', '1996 World Champion', 'Guan Yu\'s 1,000-Li March'}
BASIC_LANDS = {'Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes'}


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
            card.price = float(data[0]['prices']['usd'])
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
        with open(f'output/{file_name}.txt', 'w') as file:
            file.write(str(self))


def get_list(deck_path):
    if not os.path.exists(deck_path):
        print(f'No file found at\t{deck_path}')
        return None
    with open(deck_path, 'r') as file:
        card_list = [line.strip() for line in file.readlines() if line.strip() != '']
    return Deck(card_list)


### STEPS TO DO
#   Find Decklist
#   Read Decklist
#   Process Decklist
#   Get card list
#   Generate Queries
#   Get Card Prices
#   Get Cheapest _Legal_ printing
#   Assign Prices
#   Calculate Sum
#   Process (Sort? Write details?)
#   Write file


def test():
    file_loc = 'decklists/test.txt'
    test_deck = get_list(file_loc)
    test_deck.price_deck()
    test_deck.save()


def main():
    test()


if __name__ == "__main__":
    main()

"""Check that the deck is created and deals cards correctly."""

import unittest
import deck

class DeckTest(unittest.TestCase):
    """Contain the unit tests for the Deck class."""

    def test_new_deck_has_52_unique_cards(self):
        """Check that a new deck has 52 cards with no duplicates."""
        card_deck = deck.Deck()

        #standard deck should contain exactly 52 cards.
        self.assertEqual(len(card_deck.cards), 52)

        #set removes duplicates, so it should still have 52 cards.
        unique_cards = set(card_deck.cards)
        self.assertEqual(len(unique_cards), 52)

    def test_dealing_removes_and_returns_top_card(self):
        """Check that dealing takes the top card out of the deck."""
        card_deck = deck.Deck()

        #Remember the top card before it is removed.
        top_card = card_deck.cards[-1]
        dealt_card = card_deck.deal_card()

        #The returned card should be the one that was on top.
        self.assertEqual(dealt_card, top_card)

        #There should be 51 cards left, without the dealt card.
        self.assertEqual(len(card_deck.cards), 51)
        self.assertNotIn(dealt_card, card_deck.cards)

if __name__ == "__main__":
    unittest.main()
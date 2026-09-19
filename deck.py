"""Create a deck of cards and allow cards to be dealt."""


class Deck:
    """Represent a standard deck of 52 cards."""

    def __init__(self):
        """Build the deck when a Deck object is created."""
        self.cards = []
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        #Each suit has 13 cards.
        #1 is Ace, 11 is Jack, 12 is Queen, and 13 is King.
        for suit in suits:
            for rank in range(1, 14):
                card = (rank, suit)
                self.cards.append(card)
    def deal_card(self):
        """Remove and return one card from the deck.

        Raises:
            ValueError: If no cards are left.
        """
        #Check that there is a card available before dealing.
        if len(self.cards) == 0:
            raise ValueError("Cannot deal from an empty deck.")

        #Treat the last card in the list as the top of the deck.
        card = self.cards.pop()
        return card
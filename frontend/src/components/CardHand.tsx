import React, { useState } from 'react';
import { WhiteCard as WhiteCardType } from '../types/game.types';
import { WhiteCard } from './WhiteCard';

interface CardHandProps {
  cards: WhiteCardType[];
  onSubmit: (cardIds: string[]) => void;
  cardsToSelect: number;
  disabled?: boolean;
}

export const CardHand: React.FC<CardHandProps> = ({
  cards,
  onSubmit,
  cardsToSelect,
  disabled = false,
}) => {
  const [selectedCards, setSelectedCards] = useState<string[]>([]);

  const handleCardClick = (cardId: string) => {
    if (disabled) return;

    if (selectedCards.includes(cardId)) {
      setSelectedCards(selectedCards.filter((id) => id !== cardId));
    } else {
      if (selectedCards.length < cardsToSelect) {
        setSelectedCards([...selectedCards, cardId]);
      }
    }
  };

  const handleSubmit = () => {
    if (selectedCards.length === cardsToSelect) {
      onSubmit(selectedCards);
      setSelectedCards([]);
    }
  };

  return (
    <div className="w-full">
      <div className="mb-4 flex justify-between items-center">
        <h3 className="text-xl font-bold text-white">
          Your Hand
          {cardsToSelect > 1 && (
            <span className="ml-2 text-sm text-gray-400">
              (Select {cardsToSelect} cards)
            </span>
          )}
        </h3>
        <button
          onClick={handleSubmit}
          disabled={disabled || selectedCards.length !== cardsToSelect}
          className={`
            px-6 py-2 rounded-lg font-semibold transition-all duration-300
            ${
              selectedCards.length === cardsToSelect && !disabled
                ? 'bg-game-highlight text-white hover:bg-red-600 transform hover:scale-105'
                : 'bg-gray-600 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          Submit {selectedCards.length}/{cardsToSelect}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {cards.map((card) => (
          <WhiteCard
            key={card.id}
            card={card}
            selected={selectedCards.includes(card.id)}
            onClick={() => handleCardClick(card.id)}
            disabled={disabled}
          />
        ))}
      </div>
    </div>
  );
};

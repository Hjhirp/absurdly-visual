import React from 'react';
import { BlackCard as BlackCardType } from '../types/game.types';

interface BlackCardProps {
  card: BlackCardType;
  className?: string;
}

export const BlackCard: React.FC<BlackCardProps> = ({ card, className = '' }) => {
  return (
    <div
      className={`
        bg-black-card text-white rounded-xl p-6 shadow-2xl
        border-2 border-gray-800
        min-h-[200px] flex flex-col justify-between
        transform transition-all duration-300 hover:scale-105
        ${className}
      `}
    >
      <div className="flex-1 flex items-center justify-center">
        <p className="text-xl font-bold text-center leading-relaxed">
          {card.text}
        </p>
      </div>
      <div className="flex justify-between items-center mt-4 text-sm text-gray-400">
        <span className="font-semibold">BLACK CARD</span>
        {card.pick > 1 && (
          <span className="bg-gray-800 px-3 py-1 rounded-full">
            Pick {card.pick}
          </span>
        )}
      </div>
    </div>
  );
};

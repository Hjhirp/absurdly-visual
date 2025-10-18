import React from 'react';
import { WhiteCard as WhiteCardType } from '../types/game.types';

interface WhiteCardProps {
  card: WhiteCardType;
  selected?: boolean;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

export const WhiteCard: React.FC<WhiteCardProps> = ({
  card,
  selected = false,
  onClick,
  disabled = false,
  className = '',
}) => {
  return (
    <div
      onClick={!disabled ? onClick : undefined}
      className={`
        bg-white-card text-black rounded-xl p-4 shadow-lg
        border-2 min-h-[160px] flex flex-col justify-between
        transform transition-all duration-300
        ${!disabled && onClick ? 'cursor-pointer hover:scale-105 hover:shadow-xl' : ''}
        ${selected ? 'border-game-highlight scale-105 shadow-2xl' : 'border-gray-300'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
    >
      <div className="flex-1 flex items-center justify-center">
        <p className="text-base font-medium text-center leading-relaxed">
          {card.text}
        </p>
      </div>
      <div className="flex justify-between items-center mt-3 text-xs text-gray-500">
        <span className="font-semibold">WHITE CARD</span>
        {card.nsfw && (
          <span className="bg-red-100 text-red-600 px-2 py-1 rounded-full text-xs">
            NSFW
          </span>
        )}
      </div>
    </div>
  );
};

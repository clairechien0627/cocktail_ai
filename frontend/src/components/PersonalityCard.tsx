import React from 'react';
import type { Personality } from '../types/index';
import { Check } from 'lucide-react';

interface PersonalityCardProps {
  personality: Personality;
  selected: boolean;
  onClick: () => void;
}

const PersonalityCard: React.FC<PersonalityCardProps> = ({ personality, selected, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`
        card p-6 cursor-pointer transition-all duration-200 relative
        ${
          selected
            ? 'ring-2 ring-primary-600 ring-offset-2 bg-primary-50 shadow-lg'
            : 'hover:shadow-lg hover:scale-105'
        }
      `}
    >
      {/* 選中標記 */}
      {selected && (
        <div className="absolute top-3 right-3">
          <div className="bg-primary-600 rounded-full p-1">
            <Check className="w-4 h-4 text-white" />
          </div>
        </div>
      )}

      {/* 內容 */}
      <div className="text-center">
        {/* 圖標 */}
        <div className="text-5xl mb-3">{personality.icon}</div>

        {/* 名稱 */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{personality.name}</h3>

        {/* 描述 */}
        <p className="text-sm text-gray-600 leading-relaxed">{personality.description}</p>
      </div>

      {/* 選中徽章 */}
      {selected && (
        <div className="mt-4 flex justify-center">
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-primary-600 text-white">
            <Check className="w-3 h-3" />
            已選擇
          </span>
        </div>
      )}
    </div>
  );
};

export default PersonalityCard;

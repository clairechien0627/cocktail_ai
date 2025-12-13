import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown } from 'lucide-react';
import type { Personality } from '../types';
import { personalitiesAPI } from '../services/api';

interface PersonalityQuickSelectorProps {
  value: string;
  onChange: (personalityId: string) => void;
}

const PersonalityQuickSelector: React.FC<PersonalityQuickSelectorProps> = ({
  value,
  onChange,
}) => {
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // 載入性格列表
  useEffect(() => {
    const loadPersonalities = async () => {
      try {
        setLoading(true);
        const data = await personalitiesAPI.getPersonalities();
        setPersonalities([...data.system, ...data.custom]);
      } catch (error) {
        console.error('載入性格失敗:', error);
      } finally {
        setLoading(false);
      }
    };
    loadPersonalities();
  }, []);

  // 點擊外部關閉下拉選單
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // 取得當前選中的性格
  const selectedPersonality = personalities.find((p) => p.personality_id === value);

  // 處理選擇
  const handleSelect = (personalityId: string) => {
    onChange(personalityId);
    setIsOpen(false);
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-white/10 rounded-lg text-white text-sm">
        載入中...
      </div>
    );
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* 當前選中的性格 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors text-sm font-medium min-w-[140px]"
      >
        <span className="text-lg">{selectedPersonality?.icon || '😊'}</span>
        <span className="truncate">{selectedPersonality?.name || '友善酒保'}</span>
        <ChevronDown
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {/* 下拉選單 */}
      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-96 overflow-y-auto">
          {/* 系統性格 */}
          <div className="p-2">
            <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
              系統性格
            </div>
            {personalities
              .filter((p) => p.type === 'system')
              .map((personality) => (
                <button
                  key={personality.personality_id}
                  onClick={() => handleSelect(personality.personality_id)}
                  className={`
                    w-full flex items-center gap-3 px-3 py-2 rounded-md text-left transition-colors
                    ${
                      value === personality.personality_id
                        ? 'bg-primary-50 text-primary-700'
                        : 'hover:bg-gray-100 text-gray-700'
                    }
                  `}
                >
                  <span className="text-2xl">{personality.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{personality.name}</div>
                    {personality.description && (
                      <div className="text-xs text-gray-500 truncate">
                        {personality.description}
                      </div>
                    )}
                  </div>
                  {value === personality.personality_id && (
                    <div className="w-2 h-2 rounded-full bg-primary-600"></div>
                  )}
                </button>
              ))}
          </div>

          {/* 自訂性格 */}
          {personalities.filter((p) => p.type === 'custom').length > 0 && (
            <div className="p-2 border-t border-gray-200">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                自訂性格
              </div>
              {personalities
                .filter((p) => p.type === 'custom')
                .map((personality) => (
                  <button
                    key={personality.personality_id}
                    onClick={() => handleSelect(personality.personality_id)}
                    className={`
                      w-full flex items-center gap-3 px-3 py-2 rounded-md text-left transition-colors
                      ${
                        value === personality.personality_id
                          ? 'bg-primary-50 text-primary-700'
                          : 'hover:bg-gray-100 text-gray-700'
                      }
                    `}
                  >
                    <span className="text-2xl">{personality.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{personality.name}</div>
                      {personality.description && (
                        <div className="text-xs text-gray-500 truncate">
                          {personality.description}
                        </div>
                      )}
                    </div>
                    {value === personality.personality_id && (
                      <div className="w-2 h-2 rounded-full bg-primary-600"></div>
                    )}
                  </button>
                ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PersonalityQuickSelector;

import React, { useState, useEffect } from 'react';
import type { Personality } from '../types/index';
import { personalitiesAPI } from '../services/api';
import PersonalityCard from './PersonalityCard';
import { Loader2 } from 'lucide-react';

interface PersonalitySelectorProps {
  value: string;
  onChange: (personalityId: string) => void;
}

const PersonalitySelector: React.FC<PersonalitySelectorProps> = ({ value, onChange }) => {
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadPersonalities();
  }, []);

  const loadPersonalities = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await personalitiesAPI.getPersonalities();

      // 合併系統性格和用戶自訂性格
      const allPersonalities = [...data.system, ...data.custom];
      setPersonalities(allPersonalities);
    } catch (err: any) {
      console.error('載入性格失敗:', err);
      setError(err.response?.data?.error || '載入性格列表失敗');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        <span className="ml-2 text-gray-600">載入性格中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 text-sm">{error}</p>
        <button
          onClick={loadPersonalities}
          className="mt-2 text-sm text-primary-600 hover:text-primary-700 underline"
        >
          重試
        </button>
      </div>
    );
  }

  if (personalities.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
        <p className="text-gray-600">目前沒有可用的性格選項</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {personalities.map((personality) => (
        <PersonalityCard
          key={personality.personality_id}
          personality={personality}
          selected={value === personality.personality_id}
          onClick={() => onChange(personality.personality_id)}
        />
      ))}
    </div>
  );
};

export default PersonalitySelector;

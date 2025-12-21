import React from 'react';
import { Zap } from 'lucide-react';

export const ModelGrid = ({ models, selectedModels, onToggle }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {models.map(model => (
        <div
          key={model.id}
          onClick={() => onToggle(model.id)}
          className={`cursor-pointer p-4 rounded-lg border flex items-start space-x-3 transition ${
            selectedModels.includes(model.id)
              ? 'bg-blue-900/20 border-blue-500'
              : 'bg-slate-900 border-slate-800 hover:border-slate-700'
          }`}
        >
          <div className={`w-5 h-5 rounded border flex items-center justify-center mt-1 ${
            selectedModels.includes(model.id) ? 'bg-blue-600 border-blue-600' : 'border-slate-600'
          }`}>
            {selectedModels.includes(model.id) && <Zap size={12} className="text-white" />}
          </div>
          <div>
            <div className="font-semibold text-sm">{model.name}</div>
            <div className="text-xs text-slate-500">{model.description}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export const ChairmanSelect = ({ models, value, onChange }) => {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {models.map(model => (
        <option key={model.id} value={model.id}>{model.name} ({model.description})</option>
      ))}
    </select>
  );
};

import React, { useState } from 'react';
import { streamCouncil } from '../api';
import NodeTree from './NodeTree';
import { ModelGrid, ChairmanSelect } from './ModelSelector';
import { useModels } from '../hooks';

const Council = () => {
  const [prompt, setPrompt] = useState('');
  const [selectedModels, setSelectedModels] = useState(['openai/gpt-4o', 'anthropic/claude-3-opus']);
  const [chairman, setChairman] = useState('openai/gpt-4o');
  const [method, setMethod] = useState('dag'); // dag or ensemble
  const [isResearching, setIsResearching] = useState(false);
  const [nodes, setNodes] = useState([]);
  const [status, setStatus] = useState('');

  const { models, loading, error } = useModels();

  const toggleModel = (id) => {
    setSelectedModels(prev =>
      prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]
    );
  };

  const handleStart = () => {
    if (!prompt) return;
    setIsResearching(true);
    setNodes([]);
    setStatus('Initializing...');

    streamCouncil(prompt, selectedModels, chairman, method, (event) => {
      if (event.type === 'status') {
        setStatus(event.message);
      } else if (event.type === 'node') {
        setNodes(prev => [...prev, event.node]);
      } else if (event.type === 'done') {
        setStatus('done');
        setIsResearching(false);
      } else if (event.type === 'error') {
        setStatus('Error: ' + event.message);
        setIsResearching(false);
      }
    });
  };

  if (loading) return <div className="p-8 text-center text-slate-400">Loading models...</div>;
  if (error) return <div className="p-8 text-center text-red-400">Error loading models: {error.message}</div>;

  return (
    <div className="max-w-5xl mx-auto">
      {/* Input Section */}
      {!isResearching && nodes.length === 0 ? (
        <div className="space-y-8 animate-fade-in">
          <div>
            <h2 className="text-2xl font-bold mb-4">Research Prompt</h2>
            <div className="relative mb-4">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter your research question or topic..."
                className="w-full h-32 bg-slate-800 border border-slate-700 rounded-lg p-4 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
              />
              <div className="absolute bottom-4 right-4 flex space-x-2">
                <button className="text-xs bg-slate-700 hover:bg-slate-600 px-2 py-1 rounded text-slate-300">Web Frameworks</button>
                <button className="text-xs bg-slate-700 hover:bg-slate-600 px-2 py-1 rounded text-slate-300">API Security</button>
              </div>
            </div>

            {/* Method Selection */}
            <div className="flex space-x-6">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="method"
                  value="dag"
                  checked={method === 'dag'}
                  onChange={() => setMethod('dag')}
                  className="form-radio text-blue-600 bg-slate-800 border-slate-700 focus:ring-blue-500"
                />
                <span>AI Council (DAG)</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="method"
                  value="ensemble"
                  checked={method === 'ensemble'}
                  onChange={() => setMethod('ensemble')}
                  className="form-radio text-blue-600 bg-slate-800 border-slate-700 focus:ring-blue-500"
                />
                <span>Ensemble</span>
              </label>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-end mb-4">
              <h2 className="text-xl font-bold">Council Members</h2>
              <span className="text-sm text-slate-400">Select 2+ models for best results</span>
            </div>

            <ModelGrid models={models} selectedModels={selectedModels} onToggle={toggleModel} />
          </div>

          <div>
            <h2 className="text-xl font-bold mb-4">Chairman Model</h2>
            <ChairmanSelect models={models} value={chairman} onChange={setChairman} />
          </div>

          <button
            onClick={handleStart}
            disabled={!prompt || selectedModels.length === 0}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 rounded-lg shadow-lg transform transition active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Start Research
          </button>
        </div>
      ) : (
        <div className="animate-fade-in">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-slate-200">{prompt}</h2>
            <button onClick={() => { setIsResearching(false); setNodes([]); }} className="text-sm text-slate-500 hover:text-white">New Research</button>
          </div>

          <NodeTree nodes={nodes} status={status} />
        </div>
      )}
    </div>
  );
};

export default Council;

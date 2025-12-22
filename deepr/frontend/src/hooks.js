import { useState, useEffect } from 'react';
import { fetchModels } from './api';

export const useModels = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchModels()
      .then(data => {
        setModels(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch models", err);
        setError(err);
        setLoading(false);
      });
  }, []);

  return { models, loading, error };
};

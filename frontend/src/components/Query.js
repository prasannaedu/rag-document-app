// src/components/Query.js
import React, { useState } from 'react';
import axios from 'axios';
import { getToken } from '../utils/auth';

const Query = () => {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = getToken();

    if (!token) {
      setError(' You must be logged in to query.');
      return;
    }

    try {
      const response = await axios.post(
        '/api/documents/query',
        { query },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      setResult(response.data);
      setError('');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message;
      setError(`Query failed: ${errorMessage}`);
      console.error(' Query error:', err);
      setResult(null);
    }
  };

  return (
    <div>
      <h2>Query Documents</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your question"
          required
        />
        <button type="submit">Ask</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {result && (
        <div>
          <h3>Answer:</h3>
          <p>{result.answer}</p>
          {result.sources?.length > 0 && (
            <>
              <h4>Sources:</h4>
              <ul>
                {result.sources.map((src, i) => (
                  <li key={i}>{src}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default Query;

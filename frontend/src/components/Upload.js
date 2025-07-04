
import React, { useState } from 'react';
import { uploadDocument } from '../services/api';

const Upload = ({ token }) => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      await uploadDocument(file);
      alert(' File uploaded successfully');
      setError('');
      setFile(null);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message;
      setError(`Upload failed: ${errorMessage}`);
      console.error('Upload error:', err.response?.data || err);
    }
  };

  return (
    <div>
      <h2>Upload Document</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default Upload;
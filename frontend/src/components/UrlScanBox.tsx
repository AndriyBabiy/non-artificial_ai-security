"use client";

import React, { useState } from 'react';

interface UrlScanBoxProps {
  onScan: (url: string) => void;
}

const UrlScanBox: React.FC<UrlScanBoxProps> = ({ onScan }) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState<string | null>(null);

  const isValidUrl = (input: string) => {
    // Accept if input starts with 'https://' or 'www.'
    if (/^(https?:\/\/|www\.)/i.test(input)) {
      try {
        // If it starts with 'www.', prepend 'http://' for validation
        const urlToTest = input.startsWith('www.') ? `http://${input}` : input;
        new URL(urlToTest);
        return true;
      } catch {
        return false;
      }
    }
    return false;
  };

  const handleScan = () => {
    const trimmed = url.trim();
    if (!trimmed) {
      setError('Please enter a website URL.');
      return;
    }
    if (!isValidUrl(trimmed)) {
      setError('Invalid website URL.');
      return;
    }
    setError(null);
    onScan(trimmed);
  };

  return (
    <>
      <form className="url-form" onSubmit={e => { e.preventDefault(); handleScan(); }}>
        <input
          type="text"
          placeholder="Enter your link"
          value={url}
          onChange={e => setUrl(e.target.value)}
          className="url-input"
        />
        <button type="submit" className="url-btn">Check Website</button>
      </form>
      {url && (
        <div style={{
          color: isValidUrl(url) ? 'green' : 'red',
          background: 'rgba(0,0,0,0.05)',
          borderRadius: 4,
          padding: '4px 8px',
          fontSize: '0.95rem',
          marginTop: 4,
          display: 'inline-block',
        }}>
          {isValidUrl(url) ? 'Valid URL' : 'Invalid URL'}
        </div>
      )}
      {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
    </>
  );
};

export default UrlScanBox; 
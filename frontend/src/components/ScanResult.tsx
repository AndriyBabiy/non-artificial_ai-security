import React from 'react';

interface ScanResultProps {
  result: string | null;
}

const ScanResult: React.FC<ScanResultProps> = ({ result }) => {
  if (!result) return null;
  return (
    <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #eee', borderRadius: '6px', background: '#fafafa', minWidth: '320px', textAlign: 'center' }}>
      {result}
    </div>
  );
};

export default ScanResult; 
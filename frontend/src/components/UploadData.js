import React from 'react';

const UploadData = ({ 
  uploadStatus, 
  uploadingDataset, 
  handleFileUpload, 
  datasets 
}) => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>📁 Upload Football Data</h2>
        <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
          Upload your football datasets to enable predictions and analysis.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            { id: 'matches', name: 'Match Data', desc: 'Upload match results and statistics' },
            { id: 'team-stats', name: 'Team Stats', desc: 'Upload team-level statistics' },
            { id: 'player-stats', name: 'Player Stats', desc: 'Upload individual player statistics' }
          ].map(dataset => (
            <div key={dataset.id} className="border-2 rounded-lg p-4" style={{borderColor: '#1C5D99', backgroundColor: '#F2E9E4'}}>
              <h3 className="font-semibold mb-2" style={{color: '#002629'}}>{dataset.name}</h3>
              <p className="text-sm mb-4" style={{color: '#002629', opacity: 0.8}}>{dataset.desc}</p>
              
              <input
                type="file"
                accept=".csv"
                onChange={(e) => handleFileUpload(e, dataset.id)}
                disabled={uploadingDataset}
                className="w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:text-white hover:file:opacity-90"
                style={{
                  color: '#002629',
                  caretColor: '#002629'
                }}
              />
              <style jsx>{`
                input[type="file"]::file-selector-button {
                  background-color: #1C5D99;
                  color: white;
                  border: none;
                  margin-right: 1rem;
                  padding: 0.5rem 1rem;
                  border-radius: 0.5rem;
                  font-size: 0.875rem;
                  font-weight: 500;
                  cursor: pointer;
                  transition: opacity 0.2s;
                }
                input[type="file"]::file-selector-button:hover {
                  opacity: 0.9;
                }
              `}</style>
              
              {uploadStatus[dataset.id] && (
                <div className="mt-2 text-sm font-medium" style={{color: '#002629'}}>
                  {uploadStatus[dataset.id]}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Uploaded Datasets */}
        {datasets && datasets.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>📊 Uploaded Datasets</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {datasets.map(dataset => (
                <div key={dataset.name} className="p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#12664F'}}>
                  <div className="font-medium" style={{color: '#002629'}}>{dataset.name}</div>
                  <div className="text-sm" style={{color: '#002629', opacity: 0.8}}>{dataset.records} records</div>
                  <div className="text-xs" style={{color: '#002629', opacity: 0.6}}>Uploaded: {new Date(dataset.uploaded_at).toLocaleDateString()}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadData;
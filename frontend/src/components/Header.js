import React from 'react';

const Header = () => {
  return (
    <div style={{backgroundColor: '#002629'}} className="shadow-lg border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">⚽ Football Analytics Suite</h1>
            <span className="text-sm" style={{color: '#A3D9FF'}}>Enhanced with Starting XI & Time Decay</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
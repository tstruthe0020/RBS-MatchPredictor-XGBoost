import React, { useState, useRef, useEffect } from 'react';

const PlayerSearchInput = ({ 
  positionId, 
  positionType, 
  isHomeTeam, 
  currentPlayer, 
  searchTerm, 
  searchResults, 
  onSearch, 
  onSelect,
  placeholder = "Search players..."
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInputChange = (e) => {
    const value = e.target.value;
    onSearch(value);
    setIsOpen(value.length > 0);
  };

  const handlePlayerSelect = (player) => {
    onSelect(player);
    setIsOpen(false);
    if (inputRef.current) {
      inputRef.current.blur();
    }
  };

  const handleInputFocus = () => {
    if (searchTerm && searchTerm.length > 0) {
      setIsOpen(true);
    }
  };

  const handleClearSelection = () => {
    onSelect(null);
    onSearch('');
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const getPlayerPositionBadge = (playerPosition) => {
    const colors = {
      'GK': 'bg-yellow-100 text-yellow-800',
      'DEF': 'bg-blue-100 text-blue-800',
      'MID': 'bg-green-100 text-green-800',
      'FWD': 'bg-red-100 text-red-800'
    };
    return colors[playerPosition] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={searchTerm || ''}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          placeholder={currentPlayer ? currentPlayer.player_name : placeholder}
          className={`w-full px-3 py-2 pr-8 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            isHomeTeam 
              ? 'border-green-300 focus:ring-green-500 focus:border-green-500' 
              : 'border-blue-300 focus:ring-blue-500 focus:border-blue-500'
          } ${currentPlayer ? 'bg-gray-50' : 'bg-white'}`}
        />
        
        {currentPlayer && (
          <button
            onClick={handleClearSelection}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
        
        {!currentPlayer && (
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        )}
      </div>

      {/* Search Results Dropdown */}
      {isOpen && searchResults && searchResults.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-64 overflow-y-auto">
          {searchResults.map((player, index) => (
            <div
              key={`${player.player_name}_${index}`}
              onClick={() => handlePlayerSelect(player)}
              className={`px-3 py-2 cursor-pointer hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                player.position === positionType ? 'bg-blue-25' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="font-medium text-gray-900 text-sm">{player.player_name}</div>
                  <div className="text-xs text-gray-500">
                    {player.matches_played || 0} matches played
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPlayerPositionBadge(player.position)}`}>
                    {player.position}
                  </span>
                  {player.position === positionType && (
                    <span className="text-green-500">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No Results Message */}
      {isOpen && searchTerm && searchTerm.length > 0 && (!searchResults || searchResults.length === 0) && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
          <div className="px-3 py-4 text-center text-gray-500 text-sm">
            <div className="mb-2">
              <svg className="w-8 h-8 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <div>No players found for "{searchTerm}"</div>
            <div className="text-xs text-gray-400 mt-1">Try a different search term</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlayerSearchInput;
import React, { useState } from 'react';
import { Search as SearchIcon } from 'lucide-react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { SearchResults } from './SearchResults';
import { searchService } from '../../services/searchService';
import type { SearchResult } from '../../types/search';

export const SearchPanel: React.FC = () => {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setHasSearched(true);

    try {
      const response = await searchService.search({
        query: query.trim(),
        max_results: maxResults,
      });
      setResults(response.results);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="h-full flex flex-col p-6">
      {/* Search Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-dark-800 mb-4">Code Search</h2>

        <div className="bg-white rounded-lg border border-dark-200 p-4">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <Input
                label="Search Query"
                placeholder="e.g., JWT authentication, database connection..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
              />
            </div>

            <div className="w-32">
              <label className="block text-sm font-medium text-dark-700 mb-1">
                Max Results
              </label>
              <select
                value={maxResults}
                onChange={(e) => setMaxResults(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-dark-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>

            <Button onClick={handleSearch} disabled={!query.trim() || isLoading}>
              <SearchIcon className="w-5 h-5 mr-2" />
              Search
            </Button>
          </div>

          <p className="text-xs text-dark-500 mt-3">
            Search uses semantic similarity to find relevant code across your repository
          </p>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-auto">
        {hasSearched ? (
          <>
            <div className="mb-4">
              <p className="text-sm text-dark-600">
                {!isLoading && (
                  <>
                    Found <span className="font-semibold">{results.length}</span> results
                    {results.length > 0 && ` for "${query}"`}
                  </>
                )}
              </p>
            </div>
            <SearchResults results={results} isLoading={isLoading} />
          </>
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center text-dark-400">
              <SearchIcon className="w-16 h-16 mx-auto mb-4 text-dark-300" />
              <h3 className="text-xl font-medium text-dark-600 mb-2">
                Search Your Codebase
              </h3>
              <p className="text-sm">
                Enter a query to find relevant code snippets
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

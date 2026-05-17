import React from 'react';
import { FileCode } from 'lucide-react';
import type { SearchResult } from '../../types/search';
import { CodeBlock } from '../Chat/CodeBlock';
import { Card } from '../common/Card';
import { formatters } from '../../utils/formatters';

interface SearchResultsProps {
  results: SearchResult[];
  isLoading?: boolean;
}

export const SearchResults: React.FC<SearchResultsProps> = ({ results, isLoading }) => {
  if (isLoading) {
    return (
      <div className="text-center py-12">
        <p className="text-dark-500">Searching...</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <FileCode className="w-16 h-16 mx-auto mb-4 text-dark-300" />
        <p className="text-dark-500">No results found</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {results.map((result, index) => (
        <Card key={index} className="p-4">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <p className="font-mono text-sm text-dark-600 mb-1">
                {result.file}
              </p>
              <p className="text-xs text-dark-500">
                Lines {result.start_line}-{result.end_line}
                {result.function && ` • ${result.function}`}
              </p>
            </div>
            <span className="text-sm font-medium text-primary-600">
              {formatters.formatRelevanceScore(result.relevance_score)}
            </span>
          </div>
          <CodeBlock
            code={result.code}
            fileName={result.file}
            startLine={result.start_line}
          />
        </Card>
      ))}
    </div>
  );
};

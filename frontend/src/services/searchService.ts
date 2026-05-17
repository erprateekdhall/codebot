import api from './api';
import type { SearchRequest, SearchResponse } from '../types/search';

export const searchService = {
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await api.post<SearchResponse>('/api/search', request);
    return response.data;
  },
};

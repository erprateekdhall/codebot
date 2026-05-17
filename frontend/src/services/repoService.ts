import api from './api';
import type { RepoStatus, HealthCheck, IndexResponse } from '../types/repo';

export const repoService = {
  getStatus: async (): Promise<RepoStatus> => {
    const response = await api.get<RepoStatus>('/api/repo/status');
    return response.data;
  },

  getHealth: async (): Promise<HealthCheck> => {
    const response = await api.get<HealthCheck>('/health');
    return response.data;
  },

  triggerIndex: async (): Promise<IndexResponse> => {
    const response = await api.post<IndexResponse>('/api/repo/index');
    return response.data;
  },

  syncRepo: async (): Promise<IndexResponse> => {
    const response = await api.post<IndexResponse>('/api/repo/sync');
    return response.data;
  },
};

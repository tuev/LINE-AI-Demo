import liff from '@line/liff';
import { LiffRepo } from './LineRepo';
import { AIRepo } from './AIRepo';
import { UsageRepo } from './UsageRepo';
import axios from 'axios';

const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;
const liffId = import.meta.env.VITE_LIFF_ID;
const apiClient = axios.create({ baseURL: apiEndpoint });

export const liffRepo = new LiffRepo(liff, liffId);
export const aiRepo = new AIRepo(apiEndpoint);
export const usageRepo = new UsageRepo(apiClient);

import liff from '@line/liff';
import { LiffRepo } from './LineRepo';
import { AIRepo } from './AIRepo';

const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;
const liffId = import.meta.env.VITE_LIFF_ID;

export const liffRepo = new LiffRepo(liff, liffId);
export const aiRepo = new AIRepo(apiEndpoint);

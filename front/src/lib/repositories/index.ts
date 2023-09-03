import liff from '@line/liff';
import { LiffRepo } from './LineRepo';
import { AIRepo } from './AIRepo';

const apiEndpoint = 'http://127.0.0.1:8081';

export const liffRepo = new LiffRepo(liff, '1657284859-EPPekL6D');
export const aiRepo = new AIRepo(apiEndpoint);

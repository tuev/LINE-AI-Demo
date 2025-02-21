import liff from '@line/liff';
import {LiffRepo} from './LiffRepo';
import axios from 'axios';
import {DocumentRepo} from './DocumentRepo';
import {AuthRepo} from './AuthRepo';
import {AIRepo} from './AIRepo';
import {UsageRepo} from './UsageRepo';

const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;
const liffId = import.meta.env.VITE_LIFF_ID;
const apiClient = axios.create({baseURL: apiEndpoint, timeout: 10_000});

export const authRepo = new AuthRepo(apiClient);
export const liffRepo = new LiffRepo(liff, liffId);

apiClient.interceptors.request.use(req => {
    const bearer = liffRepo.getIDToken();
    req.headers.set('Authorization', `Bearer ${bearer}`);
    return req;
});

export const documentRepo = new DocumentRepo(apiClient);
export const aiRepo = new AIRepo(apiClient);
export const usageRepo = new UsageRepo(apiClient);

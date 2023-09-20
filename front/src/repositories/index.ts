import liff from '@line/liff';
import {LiffRepo} from './LineRepo';
import axios from 'axios';
import {DocumentRepo} from './DocumentRepo';
import {AuthRepo} from './AuthRepo';

const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;
const liffId = import.meta.env.VITE_LIFF_ID;
const apiClient = axios.create({baseURL: apiEndpoint});

export const authRepo = new AuthRepo(apiClient);
export const liffRepo = new LiffRepo(liff, liffId);

apiClient.interceptors.request.use(req => {
    const bearer = liffRepo.getIDToken();
    req.headers.set('Authorization', `Bearer ${bearer}`);
    return req;
});

export const documentRepo = new DocumentRepo(apiClient);

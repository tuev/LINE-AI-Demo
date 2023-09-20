import * as TE from 'fp-ts/lib/TaskEither';
import {AxiosInstance} from 'axios';
import {AppError} from './AppError';
import {Document} from '@/domain/Document';

export class DocumentRepo {
    constructor(private client: AxiosInstance) {}

    upload(namespace: string, file: File) {
        var formData = new FormData();
        formData.append('namespace', namespace);
        formData.append('visibility', 'public');
        formData.append('file', file);
        return TE.tryCatch(
            () => this.client.post('/document/upload', formData),
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    delete(docId: string) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.delete(`/document/delete/${docId}`);
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    listMy(skip: number, limit: number) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.get<Document[]>(
                    `/document/list_my/?skipt=${skip}&limit=${limit}`
                );
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    listPublic(skip: number, limit: number) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.get<Document[]>(
                    `/document/list_public/?skipt=${skip}&limit=${limit}`
                );
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }
}

import * as TE from 'fp-ts/lib/TaskEither';
import {AxiosInstance} from 'axios';
import {AppError} from './AppError';
import {Document, DocumentWithSimilarity} from '@/domain/Document';

export class DocumentRepo {
    private prefix: string = '/document';

    constructor(private client: AxiosInstance) {}

    uploadFile(namespace: string, file: File) {
        var formData = new FormData();
        formData.append('namespace', namespace);
        formData.append('visibility', 'public');
        formData.append('file', file);
        return TE.tryCatch(
            () => this.client.post(`${this.prefix}/upload/file`, formData),
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    uploadLandpress(namespace: string, url: string) {
        return TE.tryCatch(
            () =>
                this.client.post(`${this.prefix}/upload/landpress`, {
                    namespace,
                    url,
                    visibility: 'public',
                }),
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    uploadText(namespace: string, title: string, text: string) {
        return TE.tryCatch(
            () =>
                this.client.post(`${this.prefix}/upload/text`, {
                    namespace,
                    title,
                    text,
                    visibility: 'public',
                }),
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    parseHtml(html: string) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.post<string>(`${this.prefix}/parse/html_page`, {
                    html,
                });
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    delete(docId: string) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.delete(`${this.prefix}/delete/${docId}`);
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    listMy(skip: number, limit: number) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.get<Document[]>(
                    `${this.prefix}/list_my?skipt=${skip}&limit=${limit}`
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
                    `${this.prefix}/list_public?skipt=${skip}&limit=${limit}`
                );
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    queryPublicDocuments(namespace: string, query: string) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.post<DocumentWithSimilarity[]>(
                    `${this.prefix}/query_public_document_summary`,
                    {
                        namespace,
                        query,
                        limit: 5,
                    }
                );
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }
}

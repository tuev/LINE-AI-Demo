import * as TE from 'fp-ts/lib/TaskEither';
import {AxiosInstance} from 'axios';
import {AppError} from './AppError';
import {Usage, UsageType} from '@/domain/Usage';

export class UsageRepo {
    private prefix: string = '/usage';

    constructor(private client: AxiosInstance) {}

    record(query: string, result: string, usage_type: UsageType, usage_data: object) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.post(`${this.prefix}/record`, {
                    query,
                    result,
                    usage_type,
                    usage_data,
                });
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    listByTimestamp(skip: number, limit: number) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.get<Usage[]>(
                    `${this.prefix}/list_by_timestamp/?skip=${skip}&limit=${limit}`
                );
                for (const d of data) {
                    d.timestamp = new Date(d.timestamp);
                }
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    delete(usageId: string) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.delete(`${this.prefix}/delete/${usageId}`);
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }
}

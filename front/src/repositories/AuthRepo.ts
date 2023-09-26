import * as TE from 'fp-ts/lib/TaskEither';
import {AxiosInstance} from 'axios';
import {AppError} from './AppError';

export class AuthRepo {
    private prefix: string = '/auth';
    constructor(private client: AxiosInstance) {}

    setInternalToken(token: string) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.post(`${this.prefix}/set_internal_token`, {
                    token,
                });
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }

    getInternalTokenTimestamp() {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.get<string>(
                    `${this.prefix}/internal_token_timestamp`
                );
                return new Date(data);
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }
}

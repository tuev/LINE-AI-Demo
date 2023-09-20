import * as TE from 'fp-ts/lib/TaskEither';
import {AxiosError, AxiosInstance} from 'axios';
import {AppError} from './AppError';

export class AuthRepo {
    constructor(private client: AxiosInstance) {}

    setInternalToken(token: string) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.post(`/auth/set_internal_token`, {
                    token,
                });
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }
}

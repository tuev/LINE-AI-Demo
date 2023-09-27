import * as TE from 'fp-ts/lib/TaskEither';
import {AxiosInstance} from 'axios';
import {AppError} from './AppError';
import {Answer} from '@/domain/SimpleSystem';

export class AIRepo {
    private prefix: string = '/ai';
    private answerTimeout = 60_000;

    constructor(private client: AxiosInstance) {}

    simpleExtract(question: string, documents: string[]) {
        return TE.tryCatch(
            async () => {
                const {data} = await this.client.post<Answer>(
                    `${this.prefix}/simple_extract`,
                    {
                        question,
                        documents,
                    },
                    {timeout: this.answerTimeout}
                );
                return data;
            },
            (err: any) => AppError.fromAxiosError(err)
        );
    }
}

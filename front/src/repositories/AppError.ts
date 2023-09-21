import {AxiosError} from 'axios';

export class AppError<T> {
    constructor(
        public err: T,
        public msg: string
    ) {}

    static fromAxiosError(err: AxiosError) {
        if (!err.response?.data) {
            console.error(err);
            return new AppError(err, 'Server Internal Error');
        }
        const {detail} = err.response.data as {detail: string};
        return new AppError(err, detail || String(JSON.stringify(err.response.data)));
    }
}

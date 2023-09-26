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
        const {detail} = err.response.data as {detail: {loc: any; msg: string}[]};
        let message = '';
        if (typeof detail == 'string') {
            message = detail;
        } else if (typeof detail == 'object' && detail.length) {
            message = detail?.map(d => d.msg).join('.');
        } else {
            message = String(err.response.data);
        }
        return new AppError(err, message);
    }
}

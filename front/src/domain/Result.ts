import {cloneDeep} from 'lodash';

export enum DataState {
    NotInited = 'NotInited',
    Loading = 'Loading',
    HasData = 'HasData',
    HasError = 'HasError',
}

export class Result<Err, T> {
    public value: T;
    public err: Err | null = null;
    public state: DataState = DataState.NotInited;
    private initialValue: T;

    constructor(value: T) {
        this.value = value;
        this.initialValue = cloneDeep(value);
    }

    get notInited() {
        return this.state === DataState.NotInited;
    }

    get loading() {
        return this.state === DataState.Loading;
    }

    get hasData() {
        return this.state === DataState.HasData;
    }

    get hasError() {
        return this.state === DataState.HasError;
    }

    reset() {
        this.state = DataState.NotInited;
        this.err = null;
        this.value = this.initialValue;
        return this;
    }

    setLoading() {
        this.state = DataState.Loading;
        return this;
    }

    setValue(val: T) {
        this.state = DataState.HasData;
        this.value = val;
        this.err = null
        return this;
    }

    setError(err: Err) {
        this.state = DataState.HasError;
        this.err = err;
        return this;
    }

    onNotInited<R>(notInited: () => R) {
        if (this.state === DataState.NotInited) {
            notInited();
        }
        return this;
    }

    onLoading<R>(loading: () => R) {
        if (this.state === DataState.Loading) {
            loading();
        }
        return this;
    }

    onHasData<R>(hasData: (data: T) => R) {
        if (this.state === DataState.HasData) {
            hasData(this.value!);
        }
        return this;
    }

    onHasError<R>(hasError: (err: Err) => R) {
        if (this.state === DataState.HasError) {
            hasError(this.err!);
        }
        return this;
    }

    match<R>({
        notInited,
        loading,
        hasData,
        hasError,
    }: {
        notInited: () => R;
        loading: () => R;
        hasData: (data: T) => R;
        hasError: (err: Err) => R;
    }) {
        if (this.state === DataState.NotInited) {
            return notInited();
        }
        if (this.state === DataState.Loading) {
            return loading();
        }
        if (this.state === DataState.HasData) {
            return hasData(this.value!);
        }
        if (this.state === DataState.HasError) {
            return hasError(this.err!);
        }
    }
}

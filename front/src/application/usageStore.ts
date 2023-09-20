import * as TE from 'fp-ts/lib/TaskEither';
import * as T from 'fp-ts/lib/Task';
import {Result} from '@/domain/Result';
import {pipe} from 'fp-ts/lib/function';
import {ref} from 'vue';

export const last10Usage = ref(new Result<string, any[]>([]));

export const getUsage = async () => {
    last10Usage.value.setLoading();
    await pipe(
        //
        TE.tryCatch(
            async () => [] as any[],
            () => {
                return 'hi';
            }
        ),
        TE.fold(
            err => T.of(last10Usage.value.setError(err)),
            res => T.of(last10Usage.value.setValue(res))
        )
    )();
};

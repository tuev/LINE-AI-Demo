import * as TE from 'fp-ts/lib/TaskEither';
import * as T from 'fp-ts/lib/Task';
import {aiRepo} from '@/repositories';
import {Result} from '@/domain/Result';
import {ref} from 'vue';
import {pipe} from 'fp-ts/lib/function';
import { Answer } from '@/domain/SimpleSystem';

export const simpleExtractResult = ref(new Result<string, Answer | null>(null));

export const simpleExtract = async (question: string, documents: string[]) => {
    simpleExtractResult.value.setLoading();
    await pipe(
        aiRepo.simpleExtract(question, documents),
        TE.fold(
            err => T.of(simpleExtractResult.value.setError(err.msg)),
            res => T.of(simpleExtractResult.value.setValue(res))
        )
    )();
};

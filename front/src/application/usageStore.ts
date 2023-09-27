import * as TE from 'fp-ts/lib/TaskEither';
import * as T from 'fp-ts/lib/Task';
import {Result} from '@/domain/Result';
import {pipe} from 'fp-ts/lib/function';
import {ref} from 'vue';
import {usageRepo} from '@/repositories';
import {Usage, UsageType} from '@/domain/Usage';

export const listUsageByTimestampResult = ref(new Result<string, Usage[]>([]));

export const listUsageByTimestamp = async (skip: number, limit: number) => {
    listUsageByTimestampResult.value.setLoading();
    await pipe(
        //
        usageRepo.listByTimestamp(skip, limit),
        TE.fold(
            err => T.of(listUsageByTimestampResult.value.setError(err.msg)),
            res => T.of(listUsageByTimestampResult.value.setValue(res))
        )
    )();
};

export const recordUsageResult = ref(new Result<string, null>(null));

export const recordUsage = async (
    query: string,
    result: string,
    usageType: UsageType,
    usageData: object
) => {
    recordUsageResult.value.setLoading();
    await pipe(
        usageRepo.record(query, result, usageType, usageData),
        TE.fold(
            err => T.of(recordUsageResult.value.setError(err.msg)),
            res => T.of(recordUsageResult.value.setValue(res))
        )
    )();
};

export const deleteUsageResult = ref(new Result<string, null>(null));

export const deleteUsage = async (usageId: string) => {
    deleteUsageResult.value.setLoading();
    await pipe(
        //
        usageRepo.delete(usageId),
        TE.fold(
            err => T.of(deleteUsageResult.value.setError(err.msg)),
            res => T.of(deleteUsageResult.value.setValue(res))
        )
    )();
};

import { writable } from 'svelte/store';
import { Result, foldTEResult } from '$lib/domain/Result';
import { usageRepo } from '$lib/repositories';
import { pipe } from 'fp-ts/lib/function';
import type { UsageItem } from '$lib/domain/UsageItem';

export const last10Usage = writable(new Result<UsageItem[], string>([]));

export const getUsage = async () => {
	last10Usage.update((v) => v.setLoading());
	await pipe(
		//
		usageRepo.listLastUsages(),
		foldTEResult(last10Usage)
	)();
};

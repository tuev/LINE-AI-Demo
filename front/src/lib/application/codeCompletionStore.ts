import { derived, get, writable } from 'svelte/store';
import { liffRepo, aiRepo } from '$lib/repositories';
import { Result } from '$lib/domain/Result';
import type { LLMFinalContent, LLMStreamContent } from '$lib/domain/LLMContent';
import { pipe } from 'fp-ts/lib/function';
import * as E from 'fp-ts/lib/Either';

export const streamLoading = writable(false);
export const streamContent = writable(
	new Result<{ stream: string; final: LLMFinalContent | null }, string>()
);

export const sendPrompt = async (query: string) => {
	streamLoading.set(true);
	streamContent.update((v) => v.setLoading());
	const token = liffRepo.getIDToken();
	if (!token) {
		streamContent.update((v) => v.setError('must have access token'));
		return;
	} else {
		streamContent.update((v) => v.setValue({ stream: '', final: null }));
		await aiRepo.streamCompletion({ query }, token, (value) => {
			pipe(
				value,
				E.mapLeft((err) => {
					streamContent.update((v) => v.setError(err));
				}),
				E.map((result) => {
					if (result.stop === false) {
						const s = get(streamContent).value!.stream + (result as LLMStreamContent).content;
						streamContent.update((v) => v.setValue({ stream: s, final: null }));
					} else {
						const s = result as LLMFinalContent;
						streamContent.update((v) => v.setValue({ stream: s.final_content, final: s }));
					}
				})
			);
		});
	}
	streamLoading.set(false);
};

export const llmHealth = writable(new Result<boolean, string>());

export const isLLMOnline = derived(llmHealth, (v) => {
	return v.hasData && v.value === true;
});

export const checkLLmHealth = async () => {
	llmHealth.update((v) => v.setLoading());
	const health = await aiRepo.healthCheck();
	llmHealth.update((v) => v.setValue(health));
};

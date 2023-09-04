import { derived, writable } from 'svelte/store';
import { liffRepo } from '$lib/repositories';
import { Result } from '$lib/domain/Result';
import type { LiffProfile } from '$lib/domain/LineProfile';

export const liffProfile = writable(new Result<LiffProfile | null, string>(null));

export const isLoggedIn = derived(liffProfile, (v) => {
	return v.hasData && v.value !== null;
});

export const initLiff = async () => {
	liffProfile.update((v) => v.setLoading());
	await liffRepo.initLiff();

	if (liffRepo.isLoggedIn()) {
		// Initial check IDToken
		liffRepo.getIDToken();

		const profile = await liffRepo.getLiffProfile();
		liffProfile.update((v) => v.setValue(profile));
	} else {
		liffProfile.update((v) => v.setValue(null));
	}
};

export const login = () => {
	liffRepo.login();
};

export const logout = () => {
	liffRepo.logout();
	liffProfile.update((v) => v.setValue(null));
};

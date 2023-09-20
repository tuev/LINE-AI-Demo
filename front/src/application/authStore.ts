import * as TE from 'fp-ts/lib/TaskEither';
import * as T from 'fp-ts/lib/Task';
import {authRepo, liffRepo} from '@/repositories';
import {Result} from '@/domain/Result';
import type {LiffProfile} from '@/domain/LineProfile';
import {computed, ref} from 'vue';
import {pipe} from 'fp-ts/lib/function';

export const liffProfile = ref(new Result<string, LiffProfile | null>(null));

export const isLoggedIn = computed(() => {
    return liffProfile.value.hasData && liffProfile.value.value !== null;
});

export const initLiff = async () => {
    liffProfile.value.setLoading();
    await liffRepo.initLiff();

    if (liffRepo.isLoggedIn()) {
        // Initial check IDToken
        liffRepo.getIDToken();

        const profile = await liffRepo.getLiffProfile();
        liffProfile.value.setValue(profile);
    } else {
        liffProfile.value.setValue(null);
    }
};

export const login = () => {
    liffRepo.login();
};

export const logout = () => {
    liffRepo.logout();
    liffProfile.value.setValue(null);
};

export const setInternalTokenResult = ref(new Result<string, null>(null));

export const setInternalToken = async (token: string) => {
    setInternalTokenResult.value.setLoading();
    await pipe(
        authRepo.setInternalToken(token),
        TE.fold(
            err => T.of(setInternalTokenResult.value.setError(err.msg)),
            () => T.of(setInternalTokenResult.value.setValue(null))
        )
    )();
};

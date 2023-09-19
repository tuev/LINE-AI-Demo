import {liffRepo} from '@/repositories';
import {Result} from '@/domain/Result';
import type {LiffProfile} from '@/domain/LineProfile';
import {computed, ref} from 'vue';

export const liffProfile = ref(new Result<LiffProfile | null, string>(null));

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

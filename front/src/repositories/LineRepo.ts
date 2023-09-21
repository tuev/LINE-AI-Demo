import type {LiffProfile} from '@/domain/LineProfile';
import type {Liff} from '@liff/liff-types';

export class LiffRepo {
    constructor(
        private liff: Liff,
        private liffId: string
    ) {}

    async initLiff() {
        await this.liff.init({
            liffId: this.liffId,
            // withLoginOnExternalBrowser: true,
        });
    }

    isLoggedIn() {
        return this.liff.isLoggedIn();
    }

    async getLiffProfile() {
        const profile = await this.liff.getProfile();
        return profile as LiffProfile;
    }

    getLiffAccessToken() {
        return this.liff.getAccessToken();
    }

    getIDToken() {
        const idToken = this.liff.getDecodedIDToken();
        if (!idToken || !idToken.exp || idToken.exp < new Date().getTime() / 1000) {
            this.logout();
            this.login();
            return;
        }
        return this.liff.getIDToken();
    }

    login() {
        return this.liff.login({redirectUri: document.location.href});
    }

    logout() {
        return this.liff.logout();
    }
}

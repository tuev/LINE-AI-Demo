<script setup lang="ts">
import {
    liffProfile,
    login,
    logout,
    setInternalToken,
    setInternalTokenResult,
} from '@/application/authStore';
import {useRouter} from 'vue-router';
import {RouteName} from '@/router';
import {ref} from 'vue';

const router = useRouter();

const onLogin = () => {
    login();
};

const onLogout = () => {
    logout();
};

const setInternalTokenModal = ref(false);
const token = ref('');
const onSetInternalToken = async () => {
    await setInternalToken(token.value);
    if (!setInternalTokenResult.value.hasError) {
        setInternalTokenModal.value = false;
        token.value = '';
    }
};
</script>

<template>
    <v-toolbar color="white" class="my-toolbar">
        <v-toolbar-title @click="router.push({name: RouteName.HomePage})">
            <div class="d-flex align-center" style="cursor: pointer">
                <div class="ms-3 me-5">
                    <v-img height="80%" width="100px" src="/line-logo.png"></v-img>
                </div>
                <span class="text-h4 font-weight-bold text-primary">VN AI Demo</span>
            </div>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-progress-circular v-if="liffProfile.loading" indeterminate></v-progress-circular>
        <v-menu v-else-if="liffProfile.hasData && liffProfile.value != null" location="bottom">
            <template v-slot:activator="{props}">
                <v-btn color="primary" dark v-bind="props" icon>
                    <v-avatar>
                        <v-img
                            :src="liffProfile.value?.pictureUrl"
                            :alt="liffProfile.value?.displayName"
                        ></v-img>
                    </v-avatar>
                </v-btn>
            </template>
            <v-list>
                <v-list-item @click="setInternalTokenModal = true">
                    <v-list-item-title>Set Internal Token</v-list-item-title>
                </v-list-item>
                <v-list-item @click="onLogout">
                    <v-list-item-title>Logout</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>
        <v-btn v-else variant="flat" color="primary" @click="onLogin">Login</v-btn>

        <v-dialog width="500" v-model="setInternalTokenModal">
            <template v-slot:default="{isActive}">
                <v-card>
                    <v-card-text>
                        <v-text-field
                            v-model="token"
                            color="primary"
                            label="Internal Token"
                            :error-messages="setInternalTokenResult.err || ''"
                            :error="setInternalTokenResult.hasError"
                        ></v-text-field>
                    </v-card-text>

                    <v-card-actions>
                        <v-spacer></v-spacer>

                        <v-btn
                            color="primary"
                            variant="flat"
                            text="Set"
                            :disabled="setInternalTokenResult.loading"
                            @click="onSetInternalToken"
                        ></v-btn>
                        <v-btn text="Back" @click="isActive.value = false"></v-btn>
                    </v-card-actions>
                </v-card>
            </template>
        </v-dialog>
    </v-toolbar>
</template>

<style lang="scss" scoped>
.my-toolbar {
    border-bottom: 1px #8080802e solid;
}
</style>

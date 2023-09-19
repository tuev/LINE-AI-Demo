<script setup lang="ts">
import {onMounted} from 'vue';
import {liffProfile, login, logout} from '@/application/authStore';

onMounted(async () => {});

const onLogin = () => {
    login();
};

const onLogout = () => {
    logout();
};
</script>

<template>
    <v-toolbar color="white" class="my-toolbar">
        <div class="ms-3">
            <v-img height="80%" width="100px" src="/line-logo.png"></v-img>
        </div>
        <v-toolbar-title>
            <span class="text-h4 font-weight-bold text-primary">LVN AI Demo</span>
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
                <v-list-item @click="onLogout">
                    <v-list-item-title>Logout</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>
        <v-btn v-else variant="flat" color="primary" @click="onLogin">Login</v-btn>
    </v-toolbar>
</template>

<style lang="scss" scoped>
.my-toolbar {
    border-bottom: 1px #8080802e solid;
}
</style>

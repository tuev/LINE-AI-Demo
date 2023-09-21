<script setup lang="ts">
import {useTheme} from 'vuetify';
import {onMounted} from 'vue';
import {initLiff} from '@/application/authStore';
import AppToolbar from './AppToolbar.vue';

const theme = useTheme();

onMounted(async () => {
    theme.global.name.value = 'light';
    await initLiff();
});
</script>

<template>
    <v-app>
        <AppToolbar />
        <v-container>
            <router-view />
        </v-container>
    </v-app>
</template>

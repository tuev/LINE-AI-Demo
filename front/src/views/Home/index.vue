<script setup lang="ts">
import {appRoutes} from '@/router';
import {onMounted} from 'vue';
import {useRouter} from 'vue-router';

const router = useRouter();

onMounted(() => {});

const routes = [appRoutes.ManageFiles, appRoutes.AskQuestion];

const onRoute = (routeName: string) => {
    router.push({name: routeName});
};
</script>

<template>
    <h1>HOME</h1>
    <v-list nav>
        <v-list-item
            v-for="(route, i) in routes"
            :key="i"
            color="primary"
            role="button"
            @click="onRoute(route.name)"
        >
            <v-list-item-title v-text="route.name"></v-list-item-title>
        </v-list-item>
    </v-list>
</template>

<script setup lang="ts">
import {RouteName, appRoutes} from '@/router';
import {onMounted} from 'vue';
import {useRouter} from 'vue-router';

const router = useRouter();

onMounted(() => {});

const routes = [
    {name: 'Manage Files', routeName: appRoutes.ManageFiles.name},
    {name: 'Ask Question', routeName: appRoutes.AskQuestion.name},
    {name: 'List Usages', routeName: appRoutes.Usage.name},
];

const onRoute = (routeName: RouteName) => {
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
            @click="onRoute(route.routeName)"
        >
            <v-list-item-title v-text="route.name"></v-list-item-title>
        </v-list-item>
    </v-list>
</template>

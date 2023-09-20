<script setup lang="ts">
import {RouteName} from '@/router';
import {onMounted} from 'vue';
import {useRouter} from 'vue-router';

const router = useRouter();

onMounted(() => {});

const routes = [{text: 'Manage Files', route: '/manage-files'}];

const onRoute = () => {
    router.push({name: RouteName.ManageFiles});
};
</script>

<template>
    <h1>HOME</h1>
    <v-list nav>
        <v-list-item v-for="(route, i) in routes" :key="i" color="primary" @click="onRoute">
            <v-list-item-title v-text="route.text"></v-list-item-title>
        </v-list-item>
    </v-list>
</template>

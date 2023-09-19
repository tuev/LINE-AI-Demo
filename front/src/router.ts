import {createRouter, createWebHistory} from 'vue-router';
import Home from '@/views/Home/index.vue';

export enum RouteName {
    HomePage = 'HomePage',
}

export default createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: RouteName.HomePage,
            components: {default: Home as any},
        },
    ],
});

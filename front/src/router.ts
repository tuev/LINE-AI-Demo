import {createRouter, createWebHistory} from 'vue-router';
import Home from '@/views/Home/index.vue';
import ManageFiles from '@/views/ManageFiles/index.vue';

export enum RouteName {
    HomePage = 'HomePage',
    ManageFiles = 'ManageFiles',
}

export default createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: RouteName.HomePage,
            components: {default: Home as any},
        },
        {
            path: '/manage-files',
            name: RouteName.ManageFiles,
            components: {default: ManageFiles as any},
        },
    ],
});

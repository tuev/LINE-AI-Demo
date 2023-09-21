import {createRouter, createWebHistory} from 'vue-router';
import Home from '@/views/Home/index.vue';
import ManageFiles from '@/views/ManageFiles/index.vue';
import AskQuestion from '@/views/AskQuestion/index.vue';

export enum RouteName {
    Home = 'Home',
    ManageFiles = 'ManageFiles',
    AskQuestion = 'AskQuestion',
}

export const appRoutes = {
    HomePage: {
        path: '/',
        name: RouteName.Home,
        components: {default: Home as any},
    },
    ManageFiles: {
        path: '/manage-files',
        name: RouteName.ManageFiles,
        components: {default: ManageFiles as any},
    },
    AskQuestion: {
        path: '/ask-question',
        name: RouteName.AskQuestion,
        components: {default: AskQuestion as any},
    },
};

export default createRouter({
    history: createWebHistory(),
    routes: Object.values(appRoutes),
});
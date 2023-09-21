import {createApp} from 'vue';
import App from '@/views/App.vue';
import vuetify from '@/plugins/vuetify';
import './main.scss';

import router from './router';

createApp(App).use(router).use(vuetify).mount('#app');

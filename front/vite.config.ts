import {defineConfig} from 'vite';
import vue from '@vitejs/plugin-vue';
import {fileURLToPath, URL} from 'url';
import fs from 'fs';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    server: {
        https: {
            key: fs.readFileSync(`${__dirname}/dev-certs/key.pem`),
            cert: fs.readFileSync(`${__dirname}/dev-certs/cert.pem`),
        },
    },
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
        },
    },
});

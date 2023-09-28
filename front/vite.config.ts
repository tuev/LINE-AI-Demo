import {defineConfig, loadEnv} from 'vite';
import vue from '@vitejs/plugin-vue';
import {fileURLToPath, URL} from 'url';
import basicSsl from '@vitejs/plugin-basic-ssl';

// https://vitejs.dev/config/
export default ({mode}) => {
    process.env = {...process.env, ...loadEnv(mode, process.cwd())};
    return defineConfig({
        plugins: [vue(), basicSsl()],
        server: {
            host: 'local-line-ai-demo.line-alpha.me',
            port: 5173,
            https: true,
            proxy: {
                '/api': {
                    target: process.env.VITE_API_PROXY,
                    rewrite: path => path.replace(/^\/api/, ''),
                },
            },
        },
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url)),
            },
        },
    });
};

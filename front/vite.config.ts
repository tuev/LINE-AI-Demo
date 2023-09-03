import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';
import fs from 'fs';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}']
	},
	server: {
		https: {
			key: fs.readFileSync(`${__dirname}/dev-certs/key.pem`),
			cert: fs.readFileSync(`${__dirname}/dev-certs/cert.pem`)
		}
	}
});

<script>
	import '../app.postcss';
	import Header from './Header.svelte';
	import './styles.scss';
</script>

<div class="container mx-auto">
	<Header />

	<main>
		<slot />
	</main>
</div>

<style>
</style>

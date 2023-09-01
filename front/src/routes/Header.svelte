<script>
	import { page } from '$app/stores';
	import { Navbar, NavBrand, NavLi, NavUl, NavHamburger } from 'flowbite-svelte';
	$: activeUrl = $page.url.pathname;
</script>

<header>
	<Navbar let:hidden let:toggle>
		<NavBrand href="/">
			<img
				src="/line-logo.png"
				class="mr-3 h-6 sm:h-9"
				alt="Line Logo"
			/>
			<span class="self-center whitespace-nowrap text-xl font-semibold text-primary-500">
                VN AI DEMO
			</span>
		</NavBrand>
		<NavHamburger on:click={toggle} />
		<NavUl {activeUrl} {hidden}>
			<NavLi href="/">Completion</NavLi>
			<NavLi href="/about">About</NavLi>
		</NavUl>
	</Navbar>
</header>

<style>
</style>

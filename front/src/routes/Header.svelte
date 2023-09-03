<script lang="ts">
	import { page } from '$app/stores';
	import { login, logout, initLiff, liffProfile } from '$lib/application/authStore';
	import { checkLLmHealth, isLLMOnline } from '$lib/application/codeCompletionStore';
	import {
		Navbar,
		NavBrand,
		NavLi,
		NavUl,
		NavHamburger,
		Avatar,
		Button,
		Dropdown,
		DropdownHeader,
		DropdownItem,
		Spinner,
		Tooltip
	} from 'flowbite-svelte';
	import { onDestroy, onMount } from 'svelte';
	$: activeUrl = $page.url.pathname;

	let healthCheckInterval: any;

	onMount(async () => {
		await initLiff();
		await checkLLmHealth();
		healthCheckInterval = setInterval(() => {
			checkLLmHealth();
		}, 10_000);
	});

	onDestroy(() => {
		clearInterval(healthCheckInterval);
	});

	const onLogin = () => {
		login();
	};

	const onLogout = () => {
		logout();
	};
</script>

<header>
	<Navbar let:hidden let:toggle>
		<NavBrand href="/">
			<img src="/line-logo.png" class="mr-3 h-6 sm:h-9" alt="Line Logo" />
			<span class="self-center whitespace-nowrap text-xl font-semibold text-primary-500">
				LVN TECH AI DEMO
			</span>
		</NavBrand>
		<div class="flex items-center md:order-2">
			<div class="w-8 h-8 flex">
				<span
					class="self-center text-lg material-icons"
					class:text-green-500={$isLLMOnline}
					class:text-red-500={!$isLLMOnline}
				>
					{#if $isLLMOnline}
						cloud_queue
					{:else}
						cloud_off
					{/if}
				</span>
				<Tooltip>
					Server Status:
					{#if $isLLMOnline}
						Online
					{:else}
						Offline
					{/if}
				</Tooltip>
			</div>
			{#if $liffProfile.loading}
				<Spinner />
			{:else if $liffProfile.hasData && $liffProfile.value !== null}
				<Avatar id="avatar-menu" class="cursor-pointer" src={$liffProfile.value.pictureUrl} />
				<Dropdown placement="bottom" triggeredBy="#avatar-menu">
					<DropdownHeader>
						<span class="block text-sm">{$liffProfile.value.displayName}</span>
					</DropdownHeader>
					<DropdownItem on:click={onLogout}>Logout</DropdownItem>
				</Dropdown>
			{:else if $liffProfile.hasData && $liffProfile.value === null}
				<Button on:click={onLogin}>Login</Button>
			{/if}
			<NavHamburger on:click={toggle} class1="w-full md:flex md:w-auto md:order-1" />
		</div>
		<NavUl {activeUrl} {hidden}>
			<NavLi href="/code_completion">Code Completion</NavLi>
			<NavLi href="/about">About</NavLi>
		</NavUl>
	</Navbar>
</header>

<style>
</style>

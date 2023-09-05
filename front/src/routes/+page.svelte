<script>
	import { getUsage, last10Usage } from '$lib/application/usageStore';
	import { Button, P } from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import LastUsageList from './LastUsageList.svelte';

	onMount(() => {
		getUsage();
	});
</script>

<svelte:head>
	<title>LINE AI Demo</title>
	<meta
		name="description"
		content="LINE AI Demo - use publicly available Large Language Models to showcase the capabilities and quality of these models"
	/>
</svelte:head>

<section class="flex flex-col justify-center items-center gap-5">
	<div class="my-5 flex flex-col gap-5 max-w-xl">
		<P>
			The Language Learning Model (LLM) is currently operating on my personal computer, a Macbook
			Pro M1 Pro 14 with 16GB RAM. The performance is approximately 9 tokens per second.
		</P>
		<P>
			The cloud icon (<span class="text-lg material-icons">cloud_queue</span>) next to your avatar
			indicates whether I have turned on the Backend server running the LLM or not. If it is
			offline, please be patient as I am working on improving the backend.
		</P>
		<P>
			To manage the system's load, there is a rate limit applied, allowing
			<span class="text-red-500">1 completion per 30 seconds</span> for each account.
		</P>
		<P>
			Users are required to log in using a
			<span class="text-green-500 font-bold">Line Account</span> to access the system.
		</P>
		<P>
			This setup is primarily serving as a proof of concept rather than a fully operational system.
		</P>
		<P>Please note that this information should be used for reference purposes only.</P>
		<P>
			The source code is available at
			<a href="https://github.com/trchopan/LINE-AI-Demo" class="font-bold text-green-500">Github</a>
		</P>
	</div>
	<Button href="/code_completion">Code Completion</Button>
	{#if $last10Usage.hasData}
		<div class="py-5 max-w-md">
			<h1 class="text-lg font-bold my-3">Last 10 Usage</h1>
			<div>
				<LastUsageList usages={$last10Usage.value} />
			</div>
		</div>
	{/if}
</section>

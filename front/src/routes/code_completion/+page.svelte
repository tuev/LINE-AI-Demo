<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { streamLoading, streamContent, sendPrompt } from '$lib/application/codeCompletionStore';
	import { Heading, Textarea, Label, Button, Spinner, Radio } from 'flowbite-svelte';
	import ResponseContent from './ResponseContent.svelte';
	import { isLoggedIn, liffProfile, login } from '$lib/application/authStore';
	import axios from 'axios';
	import { parse } from 'yaml';

	let textareaRef: any;

	let prompt: string = '';
	let examples: { title: string; content: string }[] = [];

	const onSelectExample = (content: string) => {
		prompt = content;
		textareaRef.scrollIntoViewIfNeeded({ behavior: 'smooth' });
		textareaRef.querySelector('textarea').focus();
	};

	const onSend = async () => {
		if (!prompt) return;
		await sendPrompt(prompt);
		// @ts-ignore
		Prism.highlightAll();
	};

	const onLogin = () => {
		login();
	};

	onMount(async () => {
		const resp = await axios.get('/exampleCodes.yaml');
		const data = parse(resp.data);
		examples = data.example_codes;
		await tick();
		// @ts-ignore
		Prism.highlightAll();
	});
</script>

<svelte:head>
	<title>Code Completion</title>
	<meta name="description" content="Code Completion feature" />
</svelte:head>

<div>
	<div class="mx-auto text-column px-5 flex flex-col gap-5 max-w-xl">
		<Heading tag="h1" customSize="text-center text-4xl">Code Completion</Heading>
		<form on:submit|preventDefault={() => onSend()}>
			<div bind:this={textareaRef}>
				<Label for="prompt" class="mb-2">Prompt</Label>
				<Textarea
					bind:value={prompt}
					type="text"
					id="prompt"
					placeholder="Prompt"
					rows="4"
					required
					disabled={!$isLoggedIn || $streamLoading}
				/>
			</div>
			<div class="flex gap-3 items-center">
				<Button
					type="submit"
					disabled={!$isLoggedIn || $streamLoading}
					color={$streamLoading ? 'alternative' : 'primary'}
				>
					{#if $streamLoading}
						<Spinner class="mr-3" size="4" />Loading ...
					{:else}
						Send
					{/if}
				</Button>
				{#if $liffProfile.notInited === false && $liffProfile.loading === false && $isLoggedIn == false}
					<p>
						<!-- svelte-ignore a11y-click-events-have-key-events -->
						<!-- svelte-ignore a11y-no-static-element-interactions -->
						You need to
						<span on:click={() => onLogin()} class="cursor-pointer text-primary-500 font-bold">
							Login
						</span> to perform request
					</p>
				{/if}
				{#if $streamContent.hasError}
					<p class="text-red-500">{$streamContent.err}</p>
				{/if}
			</div>
		</form>
		<div class="mb-5">
			{#if $streamContent.value}
				<ResponseContent content={$streamContent.value.stream} />
				{#if $streamContent.value.final}
					{@const final = $streamContent.value.final}
					<div class="text-sm text-stone-400">
						<div>Tokens in prompt: {final.usage.tokens_evaluated}</div>
						<div>Tokens predicted: {final.usage.tokens_predicted}</div>
						<div>
							Predict tokens per second: {final.usage.timings.predicted_per_second.toFixed(3)}
						</div>
						<div>
							Predict token time (ms): {final.usage.timings.predicted_per_token_ms.toFixed(3)}
						</div>
					</div>
				{/if}
			{/if}
		</div>
		{#if $streamLoading === false}
			<div>
				<h1 class="text-xl font-bold">Example Prompts</h1>
				<hr class="my-3" />
				<div class="flex flex-col gap-3">
					{#each examples as e}
						<ResponseContent content={e.content} />
						<div class="flex justify-end">
							<Button on:click={() => onSelectExample(e.content)} color="alternative" size="xs">
								Use
							</Button>
						</div>
						<hr />
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>

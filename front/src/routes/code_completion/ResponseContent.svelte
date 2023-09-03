<script lang="ts">
	import { marked } from 'marked';
	import { onMount } from 'svelte';

	export let content: string;

	$: localContent = marked.parse(content, {
		mangle: false,
		headerIds: false
	});
</script>

<div class="response-content">{@html localContent}</div>

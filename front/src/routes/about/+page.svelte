<script>
	import { Heading, P } from 'flowbite-svelte';
</script>

<svelte:head>
	<title>About</title>
	<meta name="description" content="About this app" />
</svelte:head>

<div class="mx-auto text-column px-5 flex flex-col gap-5 max-w-xl">
	<Heading tag="h1" customSize="text-4xl" class="text-center">About this app</Heading>

	<P>
		<span class="font-bold">The Line AI demo app</span> is a project that leverages Large Language Models
		on consumer hardware. Its main goal is to exhibit the quality of these models, providing a practical
		tool for users to experience AI capabilities in real-time.
	</P>

	<P>
		Furthermore, this demo is the starting point for the
		<a href="#" class="text-primary-500">LINE VN AI Study Group</a>. This group aims to build a
		final demonstration product, using this project as a learning and development opportunity,
		allowing them to explore the complexities of AI.
	</P>
</div>

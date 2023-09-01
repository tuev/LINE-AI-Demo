<script>
	import { Heading, P } from 'flowbite-svelte';
</script>

<svelte:head>
	<title>About</title>
	<meta name="description" content="About this app" />
</svelte:head>

<div class="text-center text-column px-5 flex flex-col gap-5">
	<Heading tag="h1" customSize="text-4xl">About this app</Heading>

	<P>
		The Line AI demo is a project that utilizes publicly available Large Language Models on
		<a href="https://chop.dev" target="_blank" class="text-primary-500">Quang Tran</a>'s hardware to
		showcase the capabilities and quality of these models. It is designed to provide a practical and
		interactive demonstration of how these advanced AI models can be used in real-world
		applications.
	</P>
	<P>
		Moreover, the Line AI demo serves as the foundation for the
		<a href="#" class="text-primary-500">LINE VN AI Study Group</a>. This group aims to build a
		final demonstration product using the insights and experience gained from the Line AI demo
		project. It is a collaborative effort that brings together AI enthusiasts and experts to
		explore, learn, and innovate in the field of AI. This project, therefore, plays a crucial role
		in advancing AI knowledge and applications.
	</P>
</div>

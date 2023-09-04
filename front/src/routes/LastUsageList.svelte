<script lang="ts">
    import {format} from 'date-fns'
	import type { UsageItem } from '$lib/domain/UsageItem';
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell,
		Avatar
	} from 'flowbite-svelte';

	export let usages: UsageItem[];
</script>

<Table>
	<TableHead>
		<TableHeadCell class="!p-4" />
		<TableHeadCell>Name</TableHeadCell>
		<TableHeadCell>Timestamp</TableHeadCell>
	</TableHead>
	<TableBody tableBodyClass="divide-y">
		{#each usages as usage}
			<TableBodyRow>
				<TableBodyCell class="!p-4">
					<Avatar src={usage.picture} />
				</TableBodyCell>
				<TableBodyCell>{usage.name}</TableBodyCell>
				<TableBodyCell>{format(usage.timestamp, "yyyy-MM-dd HH:mm:ss")}</TableBodyCell>
			</TableBodyRow>
		{/each}
	</TableBody>
</Table>

<script setup lang="ts">
import {computed} from 'vue';

const props = defineProps<{text: string}>();

const paragraphs = computed(() => props.text.split('\n'));
</script>

<template>
    <p v-for="p in paragraphs" class="pb-3">{{ p }}</p>
</template>

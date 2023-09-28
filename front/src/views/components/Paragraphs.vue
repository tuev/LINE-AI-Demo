<script setup lang="ts">
import {computed} from 'vue';

const props = defineProps<{text: string}>();

const paragraphs = computed(() => props.text.split('\n'));
</script>

<template>
    <p v-for="(p, i) in paragraphs" :class="{'pb-3': i < paragraphs.length - 1}">{{ p }}</p>
</template>

<script setup lang="ts">
import {queryPublicDocumentsResult} from '@/application/documentStore';
import {similarityFormat} from '@/domain/Document';
import Paragraphs from '@/views/components/Paragraphs.vue';
import {ref} from 'vue';

const state = ref<string[]>([]);

const onToggleExpansion = (docId: string) => {
    if (state.value.includes(docId)) {
        state.value = state.value.filter(v => v != docId);
    } else {
        state.value = state.value.concat(docId);
    }
};

const emit = defineEmits<{
    (event: 'update:selected', selected: string[]): void;
}>();

const props = defineProps<{selected: string[]}>();

const onToggleSelected = (docId: string) => {
    const selected = props.selected.includes(docId)
        ? props.selected.filter(v => v !== docId)
        : props.selected.concat(docId);
    emit('update:selected', selected);
};
</script>
<template>
    <v-expansion-panels readonly v-model="state">
        <v-expansion-panel v-for="doc in queryPublicDocumentsResult.value" :value="doc.doc_id">
            <v-expansion-panel-title>
                <v-checkbox
                    hide-details
                    compact
                    :model-value="props.selected.includes(doc.doc_id)"
                    @click="onToggleSelected(doc.doc_id)"
                >
                    <template v-slot:label>
                        <span class="text-black">{{ doc.filename }}</span>
                    </template>
                </v-checkbox>
                <span class="text-caption"> Relevant: {{ similarityFormat(doc.similarity) }} </span>
                <template v-slot:actions>
                    <v-btn size="small" variant="plain" icon @click="onToggleExpansion(doc.doc_id)">
                        <v-icon icon="mdi-chevron-down"></v-icon>
                    </v-btn>
                </template>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
                <Paragraphs :text="doc.summary" />
            </v-expansion-panel-text>
        </v-expansion-panel>
    </v-expansion-panels>
</template>

<style scoped>
:deep(.v-label) {
    opacity: 1;
}
</style>

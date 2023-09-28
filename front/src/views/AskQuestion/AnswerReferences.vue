<script setup lang="ts">
import {simpleExtractResult} from '@/application/aiStore';
import {documentLink, similarityFormat} from '@/domain/Document';
import {AggerateReference, aggerateReferences} from '@/domain/SimpleSystem';
import {computed} from 'vue';

const references = computed<AggerateReference[]>(() => {
    if (!simpleExtractResult.value.hasData || !simpleExtractResult.value.value) return [];
    return aggerateReferences(simpleExtractResult.value.value.references);
});

const onClickReference = (docId: string, page: number) => {
    window.open(documentLink(docId, page), '_blank');
};
</script>

<template>
    <v-row>
        <v-col v-for="(reference, i) in references" cols="12">
            <div class="font-weight-bold mb-2">{{ reference.filename }}</div>
            <div>
                <span class="me-3">Pages:</span>
                <v-chip
                    v-for="p in reference.pages"
                    class="mb-1 me-1"
                    size="small"
                    @click="onClickReference(reference.doc_id, p.page_number)"
                >
                    <span>
                        {{ p.page_number }}
                        <span class="text-blue text-caption" style="font-size: 0.5rem !important">
                            ({{ similarityFormat(p.similarity) }})
                        </span>
                    </span>
                </v-chip>
            </div>
            <hr v-if="i < references.length - 1" class="mt-3" />
        </v-col>
    </v-row>
</template>

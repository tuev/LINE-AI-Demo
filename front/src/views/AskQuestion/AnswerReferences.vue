<script setup lang="ts">
import {simpleExtractResult} from '@/application/aiStore';
import {documentLink, similarityFormat} from '@/domain/Document';
import {computed} from 'vue';

interface AggerateReference {
    doc_id: string;
    filename: string;
    pages: {page_number: number; similarity: number}[];
}

const aggeratedReferences = computed(() => {
    if (!simpleExtractResult.value.hasData || !simpleExtractResult.value.value) return [];
    return simpleExtractResult.value.value.references.reduce((acc, cur) => {
        const pageInfo = {
            page_number: cur.metadata.page_number,
            similarity: cur.similarity,
        };
        const foundIndex = acc.findIndex(v => v.doc_id === cur.doc_id);
        if (foundIndex < 0) {
            acc.push({doc_id: cur.doc_id, filename: cur.filename, pages: [pageInfo]});
        } else {
            acc[foundIndex].pages.push(pageInfo);
        }
        return acc;
    }, [] as AggerateReference[]);
});

const onClickReference = (docId: string, page: number) => {
    window.open(documentLink(docId, page), '_blank');
};
</script>

<template>
    <v-row>
        <v-col v-for="(reference, i) in aggeratedReferences" cols="12">
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
            <hr v-if="i < aggeratedReferences.length - 1" class="mt-3"/>
        </v-col>
    </v-row>
</template>

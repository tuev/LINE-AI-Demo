<script setup lang="ts">
import {deleteDocument, deleteDocumentResult, processDocument} from '@/application/documentStore';
import {Document, documentLink, uploadTimestampFormat} from '@/domain/Document';
import {ref} from 'vue';
import DocumentSummaryModal from './DocumentSummaryModal.vue';
import {nextTick} from 'vue';
import {computed} from 'vue';
import {isEmpty} from 'lodash';

const props = defineProps<{documents: Document[]}>();

const onCopyDocId = (docId: string) => {
    navigator.clipboard.writeText(docId);
};

const onDelete = (docId: string) => {
    deleteDocument(docId);
};

const onOpenFile = (docId: string) => {
    window.open(documentLink(docId, 0), '_blank');
};

const selectedDocId = ref('');
const selectedSummary = computed(() => {
    if (isEmpty(props.documents)) return '';
    return props.documents.find(d => d.doc_id === selectedDocId.value)?.summary || '';
});
const isDocumentSummaryModalOpen = ref(false);

const onOpenSummary = async (docId: string) => {
    selectedDocId.value = docId;
    await nextTick();
    isDocumentSummaryModalOpen.value = true;
};

const onProcessDocument = () => {
    processDocument(selectedDocId.value);
};
</script>

<template>
    <v-list>
        <v-list-item v-for="doc in props.documents">
            <v-list-item-title>
                <span
                    :class="{
                        'text-red-lighten-2': deleteDocumentResult.value == doc.doc_id,
                        'text-grey-lighten-1': doc.process_status == 'processing',
                    }"
                >
                    {{ doc.filename }}
                </span>
            </v-list-item-title>
            <v-list-item-subtitle>
                <span>{{ doc.namespace }} | {{ doc.content_type }}</span>
                <span
                    v-if="deleteDocumentResult.value == doc.doc_id && deleteDocumentResult.hasError"
                    class="text-red ms-3"
                >
                    {{ deleteDocumentResult.err }}
                </span>
            </v-list-item-subtitle>
            <template v-slot:append>
                <v-menu location="bottom">
                    <template v-slot:activator="{props}">
                        <div class="text-end text-caption">
                            <div
                                :class="{
                                    'text-green': doc.process_status === 'processed',
                                    'text-orange': doc.process_status == 'processing',
                                    'text-red': doc.process_status == 'error',
                                }"
                            >
                                {{ doc.process_status }}
                            </div>
                            <div>{{ uploadTimestampFormat(new Date(doc.upload_at)) }}</div>
                        </div>
                        <v-btn
                            v-bind="props"
                            color="grey-lighten-1"
                            icon="mdi-information"
                            variant="text"
                        ></v-btn>
                    </template>
                    <v-list>
                        <v-list-item @click="onOpenFile(doc.doc_id)">
                            <v-list-item-title>Open File</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="onOpenSummary(doc.doc_id)">
                            <v-list-item-title>Open Summary</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="onCopyDocId(doc.doc_id)">
                            <v-list-item-title>Copy ID</v-list-item-title>
                        </v-list-item>
                        <v-list-item v-if="deleteDocumentResult.loading">
                            <v-progress-circular indeterminate></v-progress-circular>
                        </v-list-item>
                        <v-list-item v-else @click="onDelete(doc.doc_id)">
                            <v-list-item-title>
                                <span class="text-red">Delete</span>
                            </v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
            </template>
        </v-list-item>
    </v-list>

    <DocumentSummaryModal
        v-model="isDocumentSummaryModalOpen"
        :summary="selectedSummary"
        @process="onProcessDocument"
    />
</template>

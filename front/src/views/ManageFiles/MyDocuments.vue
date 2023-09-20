<script setup lang="ts">
import {deleteDocument, deleteDocumentResult} from '@/application/documentStore';
import {Document} from '@/domain/Document';

const props = defineProps<{documents: Document[]}>();

const onCopyDocId = (docId: string) => {
    navigator.clipboard.writeText(docId);
};

const onDelete = (docId: string) => {
    deleteDocument(docId);
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
                <span>{{ doc.namespace }}</span>
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
                        <v-btn
                            v-bind="props"
                            color="grey-lighten-1"
                            icon="mdi-information"
                            variant="text"
                        ></v-btn>
                    </template>
                    <v-list>
                        <v-list-item>
                            <v-list-item-title>
                                <span class="text-caption">status: {{ doc.process_status }}</span>
                            </v-list-item-title>
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
</template>

<script setup lang="ts">
import {listMyDocuments, myDocuments, uploadFile, uploadResult} from '@/application/documentStore';
import {onMounted} from 'vue';
import {ref} from 'vue';
import MyDocuments from './MyDocuments.vue';

const namespace = ref('test');
const files = ref();

const onUpload = () => {
    uploadFile(namespace.value, files.value[0]);
};

const onListMyDocuments = () => {
    listMyDocuments();
};

onMounted(() => {
    listMyDocuments();
});
</script>

<template>
    <v-container>
        <v-row>
            <div class="d-flex">
                <h1 class="me-3">Manage Files</h1>
                <v-btn variant="flat" icon="mdi-refresh" @click="onListMyDocuments"></v-btn>
            </div>
        </v-row>
        <v-row>
            <v-col cols="3">
                <div class="d-flex flex-column">
                    <v-text-field
                        v-model="namespace"
                        color="primary"
                        label="Namespace"
                    ></v-text-field>
                    <v-file-input
                        v-model="files"
                        accept="application/pdf, text/html"
                    ></v-file-input>
                    <v-btn
                        variant="flat"
                        color="primary"
                        :loading="uploadResult.loading"
                        @click="onUpload"
                    >
                        Upload
                    </v-btn>
                </div>
            </v-col>
            <v-col cols="9">
                <v-progress-circular v-if="myDocuments.loading" indeterminate></v-progress-circular>
                <v-row v-else-if="myDocuments.hasError">{{ myDocuments.err }}</v-row>
                <MyDocuments v-else-if="myDocuments.hasData" :documents="myDocuments.value" />
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import {
    listMyDocuments,
    listMyDocumentsResult,
    uploadFile,
    uploadFileResult,
    uploadLandpress,
    uploadLandpressResult,
    uploadText,
} from '@/application/documentStore';
import {onMounted} from 'vue';
import {ref} from 'vue';
import MyDocuments from './MyDocuments.vue';
import UploadHtmlModal from './UploadHtmlModal.vue';

const namespace = ref('test');
const files = ref([]);

const onUploadFile = async () => {
    await uploadFile(namespace.value, files.value[0]);
    files.value = [];
};

const landpressUrl = ref('');
const onUploadLandpress = async () => {
    await uploadLandpress(namespace.value, landpressUrl.value);
    landpressUrl.value = '';
};

const onListMyDocuments = () => {
    listMyDocuments();
};

onMounted(() => {
    listMyDocuments();
});

const isUploadHtmlModalOpen = ref(false);

const onUploadText = async (value: {title: string; text: string}) => {
    await uploadText(namespace.value, value.title, value.text);
    isUploadHtmlModalOpen.value = false;
};
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
                <div class="d-flex flex-column" style="gap: 20px">
                    <v-text-field v-model="namespace" label="Namespace"></v-text-field>

                    <div>
                        <h6 class="mb-2">Upload File</h6>
                        <v-file-input
                            v-model="files"
                            accept="application/pdf, text/html"
                        ></v-file-input>
                        <v-btn
                            variant="flat"
                            color="primary"
                            :loading="uploadFileResult.loading"
                            @click="onUploadFile"
                        >
                            Upload File
                        </v-btn>
                    </div>

                    <div>
                        <h6 class="mb-2">Upload Landpress</h6>
                        <v-text-field v-model="landpressUrl" label="Landpress URL"></v-text-field>
                        <v-btn
                            variant="flat"
                            color="primary"
                            :loading="uploadLandpressResult.loading"
                            @click="onUploadLandpress"
                        >
                            Upload Landpress
                        </v-btn>
                    </div>

                    <div>
                        <h6 class="mb-2">Upload HTML</h6>
                        <v-btn variant="flat" color="primary" @click="isUploadHtmlModalOpen = true">
                            Upload HTML
                        </v-btn>
                        <UploadHtmlModal v-model="isUploadHtmlModalOpen" @upload="onUploadText" />
                    </div>
                </div>
            </v-col>
            <v-col cols="9">
                <v-progress-circular
                    v-if="listMyDocumentsResult.loading"
                    indeterminate
                ></v-progress-circular>
                <v-row v-else-if="listMyDocumentsResult.hasError">
                    {{ listMyDocumentsResult.err }}
                </v-row>
                <MyDocuments
                    v-else-if="listMyDocumentsResult.hasData"
                    :documents="listMyDocumentsResult.value"
                />
            </v-col>
        </v-row>
    </v-container>
</template>

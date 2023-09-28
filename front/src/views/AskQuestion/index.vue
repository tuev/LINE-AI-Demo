<script setup lang="ts">
import {queryPublicDocuments, queryPublicDocumentsResult} from '@/application/documentStore';
import {ref} from 'vue';
import SearchDocumentResults from './SearchDocumentResults.vue';
import {simpleExtract, simpleExtractResult} from '@/application/aiStore';
import {isEmpty} from 'lodash';
import AnswerReferences from '@/views/components/AnswerReferences.vue';
import Paragraphs from '../components/Paragraphs.vue';
import {recordUsage, recordUsageResult} from '@/application/usageStore';
import {UsageType} from '@/domain/Usage';
import {useRouter} from 'vue-router';
import {RouteName} from '@/router';

const router = useRouter();

const namespace = ref('test');
const question = ref('Thủ tục đăng ký bảo hiểm cho nhân viên LINE như thế nào?');
const selectedDocuments = ref<string[]>([]);

const onSearch = async () => {
    await queryPublicDocuments(namespace.value, question.value);
    selectedDocuments.value = queryPublicDocumentsResult.value.value.map(v => v.doc_id);
};

const onAnswer = () => {
    simpleExtract(question.value, selectedDocuments.value);
};

const onRecordUsage = async () => {
    if (!simpleExtractResult.value.hasData) return;
    await recordUsage(
        question.value,
        simpleExtractResult.value.value!.result,
        UsageType.Extract,
        simpleExtractResult.value.value!
    );
    if (recordUsageResult.value.hasData) {
        router.push({name: RouteName.Usage});
    }
};
</script>

<template>
    <v-container>
        <v-row>
            <div class="d-flex">
                <h1>Ask Question</h1>
            </div>
        </v-row>
        <v-row>
            <v-col cols="2">
                <v-text-field v-model="namespace" color="primary" label="Namespace"></v-text-field>
            </v-col>
            <v-col cols="7">
                <v-textarea v-model="question" color="primary" label="Question"></v-textarea>
            </v-col>
            <v-col cols="3">
                <v-btn
                    variant="flat"
                    color="primary"
                    :loading="queryPublicDocumentsResult.loading"
                    @click="onSearch"
                >
                    Search
                </v-btn>
            </v-col>
        </v-row>
        <v-row>
            <v-col>
                <h4 class="mb-5">Relevant Documents</h4>
            </v-col>
        </v-row>
        <v-row>
            <v-col cols="9">
                <div v-if="queryPublicDocumentsResult.hasError">
                    {{ queryPublicDocumentsResult.err }}
                </div>
                <SearchDocumentResults
                    v-if="queryPublicDocumentsResult.hasData"
                    v-model:selected="selectedDocuments"
                />
            </v-col>
            <v-col v-if="queryPublicDocumentsResult.hasData" cols="3">
                <v-btn
                    variant="flat"
                    color="primary"
                    :loading="simpleExtractResult.loading"
                    :disabled="isEmpty(selectedDocuments)"
                    @click="onAnswer"
                >
                    Answer
                </v-btn>
            </v-col>
        </v-row>
        <v-row v-if="isEmpty(selectedDocuments)">
            <v-col>Search then select Relevant Documents</v-col>
        </v-row>
        <v-row v-if="simpleExtractResult.hasError">
            <v-col>{{ simpleExtractResult.err }}</v-col>
        </v-row>
        <v-row v-if="simpleExtractResult.hasData">
            <v-col cols="9">
                <h4 class="mb-5">Answer</h4>
                <v-row>
                    <v-col>
                        <Paragraphs :text="simpleExtractResult.value?.result || ''" />
                    </v-col>
                </v-row>
            </v-col>
            <v-col cols="3">
                <div class="mb-3">
                    <v-btn
                        @click="onRecordUsage"
                        :disabled="recordUsageResult.loading"
                        :loading="recordUsageResult.loading"
                        text="Record"
                        color="secondary"
                    ></v-btn>
                    <div v-if="recordUsageResult.hasError" class="text-red">
                        {{ recordUsageResult.err }}
                    </div>
                </div>
                <h4 class="mb-3">References</h4>
                <AnswerReferences :references="simpleExtractResult.value?.references || []" />
            </v-col>
        </v-row>
    </v-container>
</template>

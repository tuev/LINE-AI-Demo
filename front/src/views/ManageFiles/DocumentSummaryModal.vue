<script setup lang="ts">
import {computed} from 'vue';
import Paragraphs from '@/views/components/Paragraphs.vue';
import {processDocumentResult} from '@/application/documentStore';
import {Document} from '@/domain/Document';

const props = defineProps<{modelValue: boolean; document: Document; readonly: boolean}>();
const emit = defineEmits<{
    (event: 'update:modelValue', value: boolean): void;
    (event: 'process'): void;
}>();

const localValue = computed({
    get() {
        return props.modelValue;
    },
    set(v: boolean) {
        emit('update:modelValue', v);
    },
});
</script>

<template>
    <v-dialog width="80vw" v-model="localValue">
        <v-card>
            <v-card-text>
                <Paragraphs :text="props.document.summary" />
            </v-card-text>

            <v-card-actions>
                <span v-if="processDocumentResult.hasError" class="text-caption text-red">
                    {{ processDocumentResult.err }}
                </span>
                <v-spacer></v-spacer>

                <v-btn
                    v-if="readonly === false"
                    @click="$emit('process')"
                    :disabled="
                        props.document.process_status === 'processing' ||
                        processDocumentResult.loading
                    "
                    :loading="processDocumentResult.loading"
                    color="primary"
                    variant="flat"
                    text="Re-process"
                ></v-btn>
                <v-btn text="Back" @click="localValue = false"></v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

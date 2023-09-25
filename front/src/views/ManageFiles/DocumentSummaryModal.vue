<script setup lang="ts">
import {computed} from 'vue';
import Paragraphs from '@/views/components/Paragraphs.vue';
import {processDocumentResult} from '@/application/documentStore';

const props = defineProps<{modelValue: boolean; summary: string}>();
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
                <Paragraphs :text="props.summary" />
            </v-card-text>

            <v-card-actions>
                <v-spacer></v-spacer>

                <v-btn
                    color="primary"
                    variant="flat"
                    text="Re-process"
                    :disabled="processDocumentResult.loading"
                    :loading="processDocumentResult.loading"
                    @click="$emit('process')"
                ></v-btn>
                <v-btn text="Back" @click="localValue = false"></v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

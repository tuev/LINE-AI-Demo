<script setup lang="ts">
import {parseHtml, parseHtmlResult, uploadTextResult} from '@/application/documentStore';
import {computed} from 'vue';
import {ref} from 'vue';

const props = defineProps<{modelValue: boolean}>();
const emit = defineEmits<{
    (event: 'update:modelValue', value: boolean): void;
    (event: 'upload', value: {title: string; text: string}): void;
}>();

const localValue = computed({
    get() {
        return props.modelValue;
    },
    set(v: boolean) {
        emit('update:modelValue', v);
    },
});

const title = ref('');
const html = ref('');
const text = ref('');
const htmlMode = ref(true);

const onToggleHtmlAndText = async () => {
    if (htmlMode.value) {
        await parseHtml(html.value);
        if (parseHtmlResult.value.hasData && parseHtmlResult.value !== null) {
            text.value = parseHtmlResult.value.value!;
        }
        htmlMode.value = false;
    } else {
        htmlMode.value = true;
    }
};

const onUpload = () => {
    emit('upload', {
        title: title.value,
        text: text.value,
    });
};
</script>

<template>
    <v-dialog width="80vw" v-model="localValue">
        <v-card>
            <v-card-text>
                <v-text-field v-model="title" color="primary" label="title"></v-text-field>
                <v-btn @click="onToggleHtmlAndText">
                    <span v-if="htmlMode">To Text</span>
                    <span v-else>To Html</span>
                </v-btn>
                <v-textarea v-show="htmlMode" v-model="html" label="html"></v-textarea>
                <v-textarea v-show="!htmlMode" v-model="text" label="text"></v-textarea>
            </v-card-text>

            <v-card-actions>
                <v-spacer></v-spacer>

                <v-btn
                    color="primary"
                    variant="flat"
                    text="Upload"
                    :disabled="uploadTextResult.loading"
                    :loading="uploadTextResult.loading"
                    @click="onUpload"
                ></v-btn>
                <v-btn text="Back" @click="localValue = false"></v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

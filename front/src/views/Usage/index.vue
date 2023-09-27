<script setup lang="ts">
import {
    deleteUsage,
    deleteUsageResult,
    listUsageByTimestamp,
    listUsageByTimestampResult,
} from '@/application/usageStore';
import {onMounted} from 'vue';
import Paragraphs from '../components/Paragraphs.vue';

const onRefreshUsage = () => {
    listUsageByTimestamp(0, 10);
};

onMounted(() => {
    listUsageByTimestamp(0, 10);
});

const onDelete = async (usageId: string) => {
    await deleteUsage(usageId);
    listUsageByTimestamp(0, 10);
};
</script>

<template>
    <div class="d-flex flex-column" style="gap: 20px">
        <div>
            <v-btn @click="onRefreshUsage" text="Refresh"></v-btn>
        </div>
        <v-progress-circular v-if="listUsageByTimestampResult.loading" indeterminate />
        <span v-else-if="listUsageByTimestampResult.hasError" class="ms-5 text-caption">
            Error: {{ listUsageByTimestampResult.err }}
        </span>
        <v-expansion-panels v-else-if="listUsageByTimestampResult.hasData">
            <v-expansion-panel
                v-for="usage in listUsageByTimestampResult.value"
                :value="usage.usage_id"
            >
                <v-expansion-panel-title>
                    {{ usage.usage_data.question }}
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                    <div>
                        <Paragraphs :text="usage.usage_data.result" />
                    </div>
                    <div>
                        <span v-if="deleteUsageResult.hasError" class="text-red">
                            {{ deleteUsageResult.err }}
                        </span>
                        <v-btn
                            @click="onDelete(usage.usage_id)"
                            :disabled="deleteUsageResult.loading"
                            :loading="deleteUsageResult.loading"
                            text="Delete"
                        ></v-btn>
                    </div>
                </v-expansion-panel-text>
            </v-expansion-panel>
        </v-expansion-panels>
    </div>
</template>

<script setup lang="ts">
import {RouteName, appRoutes} from '@/router';
import {useRouter} from 'vue-router';

const router = useRouter();

const routes = [
    {name: 'Manage Files', routeName: appRoutes.ManageFiles.name},
    {name: 'Ask Question', routeName: appRoutes.AskQuestion.name},
    {name: 'List Usages', routeName: appRoutes.Usage.name},
];

const onRoute = (routeName: RouteName) => {
    router.push({name: routeName});
};
</script>

<template>
    <v-list nav>
        <v-list-item
            v-for="(route, i) in routes"
            :key="i"
            color="primary"
            role="button"
            @click="onRoute(route.routeName)"
        >
            <v-list-item-title v-text="route.name"></v-list-item-title>
        </v-list-item>
    </v-list>
    <div class="d-flex flex-column" style="gap: 16px">
        <h2>Notice</h2>
        <p>
            This is an internal <span class="text-green font-weight-bold">LINE</span> system. Please
            contact
            <span class="font-weight-bold">
                Quang Tran
                <a href="mailto:quang.tran@linecopr.com">&lt;quang.tran@linecorp.com&gt;</a>
            </span>
            for information on how to obtain the
            <span class="text-red font-weight-bold">inhouse chatgpt</span> token.
        </p>
        <p>
            Users of this system will need a token to use the AI, both for processing documents and
            asking questions.
        </p>
        <h2>Introduction</h2>
        <p>This is a demonstration project by Line Vietnam AI Study group.</p>
        <p>
            The system includes a tool for managing documents called
            <span class="text-green font-weight-bold">Manage Files</span>. Users can upload files
            from multiple sources using this tool.
        </p>
        <p>
            After successful upload the system will process the file in to a
            <span class="font-weight-bold">Vector Database</span>. And store the metadata in
            multiple forms.
        </p>
        <p>
            The vector database allows for semantic search. We will utilize this feature to assist
            in document retrieval for the AI, enabling it to process the extensive information from
            the uploaded document.
        </p>
        <p>
            To interact with the AI, user can use the
            <span class="text-green font-weight-bold">Ask Question</span> page to query for answers.
        </p>
        <p>
            To answer the user's questions, the AI uses the available information in the content of
            the uploaded files.
        </p>
        <p>
            To record the Answer just press the Record button and it will be avaiable in the
            <span class="text-green font-weight-bold">List Usage</span> section
        </p>
        <h2>Future development</h2>
        <p>
            Notice that the answers are only derived from the uploaded documents. Additional
            features, such as utilizing a search engine or web scraping from sources like Wikipedia
            or news sites, will be implemented in the future.
        </p>
        <p>
            The main focus of this system is to parsing the avaiable documents into the system that
            we can then use the LLMs to perform automation jobs such as
        </p>
        <ul class="my-ul">
            <li>Question and Answer</li>
            <li>Information Extraction</li>
            <li>Learning Support</li>
            <li>etc.</li>
        </ul>
    </div>
</template>

<style lang="scss" scoped>
.my-ul {
    li {
        list-style: inside;
    }
}
</style>

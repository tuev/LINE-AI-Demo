import * as TE from 'fp-ts/lib/TaskEither';
import * as T from 'fp-ts/lib/Task';
import {documentRepo} from '@/repositories';
import {Result} from '@/domain/Result';
import {ref} from 'vue';
import {pipe} from 'fp-ts/lib/function';
import {Document, DocumentWithSimilarity} from '@/domain/Document';

export const uploadFileResult = ref(new Result<string, null>(null));

export const uploadFile = async (namespace: string, file: File) => {
    uploadFileResult.value.setLoading();
    await pipe(
        documentRepo.uploadFile(namespace, file),
        TE.fold(
            err => T.of(uploadFileResult.value.setError(err.msg)),
            () => {
                listMyDocuments();
                return T.of(uploadFileResult.value.setValue(null));
            }
        )
    )();
};

export const uploadLandpressResult = ref(new Result<string, null>(null));

export const uploadLandpress = async (namespace: string, url: string) => {
    uploadLandpressResult.value.setLoading();
    await pipe(
        documentRepo.uploadLandpress(namespace, url),
        TE.fold(
            err => T.of(uploadLandpressResult.value.setError(err.msg)),
            () => {
                listMyDocuments();
                return T.of(uploadLandpressResult.value.setValue(null));
            }
        )
    )();
};

export const uploadTextResult = ref(new Result<string, null>(null));

export const uploadText = async (namespace: string, title: string, text: string) => {
    uploadTextResult.value.setLoading();
    await pipe(
        documentRepo.uploadText(namespace, title, text),
        TE.fold(
            err => T.of(uploadTextResult.value.setError(err.msg)),
            () => {
                listMyDocuments();
                return T.of(uploadTextResult.value.setValue(null));
            }
        )
    )();
};

export const parseHtmlResult = ref(new Result<string, string | null>(null));

export const parseHtml = async (html: string) => {
    parseHtmlResult.value.reset();
    parseHtmlResult.value.setLoading();
    await pipe(
        documentRepo.parseHtml(html),
        TE.fold(
            err => T.of(parseHtmlResult.value.setError(err.msg)),
            res => {
                return T.of(parseHtmlResult.value.setValue(res));
            }
        )
    )();
};

export const processDocumentResult = ref(new Result<string, null>(null));

export const processDocument = async (docId: string) => {
    processDocumentResult.value.setLoading();
    await pipe(
        documentRepo.processDocument(docId),
        TE.fold(
            err => T.of(processDocumentResult.value.setError(err.msg)),
            () => {
                listMyDocuments();
                return T.of(processDocumentResult.value.setValue(null));
            }
        )
    )();
};

export const listMyDocumentsResult = ref(new Result<string, Document[]>([]));

export const listMyDocuments = async () => {
    listMyDocumentsResult.value.setLoading();
    await pipe(
        documentRepo.listMy(0, 100),
        TE.fold(
            err => T.of(listMyDocumentsResult.value.setError(err.msg)),
            res => T.of(listMyDocumentsResult.value.setValue(res))
        )
    )();
};

export const listPublicDocumentResult = ref(new Result<string, Document[]>([]));

export const listPublicDocument = async () => {
    listPublicDocumentResult.value.setLoading();
    await pipe(
        documentRepo.listPublic(0, 100),
        TE.fold(
            err => T.of(listPublicDocumentResult.value.setError(err.msg)),
            res => {
                if (!listMyDocumentsResult.value.hasData) {
                    return T.of(listPublicDocumentResult.value.setValue(res));
                }
                const myDocumentIds = listMyDocumentsResult.value.value.map(d => d.doc_id);
                const filteredMyDocuments = res.filter(doc => !myDocumentIds.includes(doc.doc_id));
                return T.of(listPublicDocumentResult.value.setValue(filteredMyDocuments));
            }
        )
    )();
};

export const listAllDocuments = async () => {
    await listMyDocuments();
    await listPublicDocument();
}

export const deleteDocumentResult = ref(new Result<string, string | null>(''));

export const deleteDocument = async (docId: string) => {
    deleteDocumentResult.value.reset();
    deleteDocumentResult.value.setValue(docId);
    deleteDocumentResult.value.setLoading();
    await pipe(
        documentRepo.delete(docId),
        TE.map(() => {
            deleteDocumentResult.value.setValue(null);
            listMyDocuments();
        }),
        TE.mapLeft(err => {
            deleteDocumentResult.value.setError(err.msg);
        })
    )();
};

export const queryPublicDocumentsResult = ref(new Result<string, DocumentWithSimilarity[]>([]));

export const queryPublicDocuments = async (namespace: string, query: string) => {
    queryPublicDocumentsResult.value.reset();
    queryPublicDocumentsResult.value.setLoading();
    await pipe(
        documentRepo.queryPublicDocuments(namespace, query),
        TE.fold(
            err => T.of(queryPublicDocumentsResult.value.setError(err.msg)),
            res => T.of(queryPublicDocumentsResult.value.setValue(res))
        )
    )();
};

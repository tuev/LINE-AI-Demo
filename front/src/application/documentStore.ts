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
        documentRepo.upload(namespace, file),
        TE.fold(
            err => T.of(uploadFileResult.value.setError(err.msg)),
            () => {
                listMyDocuments();
                return T.of(uploadFileResult.value.setValue(null));
            }
        )
    )();
};

export const listMyDocumentsResult = ref(new Result<string, Document[]>([]));

export const listMyDocuments = async () => {
    listMyDocumentsResult.value.setLoading();
    await pipe(
        documentRepo.listMy(0, 10),
        TE.fold(
            err => T.of(listMyDocumentsResult.value.setError(err.msg)),
            res => T.of(listMyDocumentsResult.value.setValue(res))
        )
    )();
};

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
    queryPublicDocumentsResult.value.reset()
    queryPublicDocumentsResult.value.setLoading();
    await pipe(
        documentRepo.queryPublicDocuments(namespace, query),
        TE.fold(
            err => T.of(queryPublicDocumentsResult.value.setError(err.msg)),
            res => T.of(queryPublicDocumentsResult.value.setValue(res))
        )
    )();
};

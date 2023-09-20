import * as TE from 'fp-ts/lib/TaskEither';
import * as T from 'fp-ts/lib/Task';
import {documentRepo} from '@/repositories';
import {Result} from '@/domain/Result';
import {ref} from 'vue';
import {pipe} from 'fp-ts/lib/function';
import {Document} from '@/domain/Document';

export const uploadResult = ref(new Result<string, null>(null));

export const uploadFile = async (namespace: string, file: File) => {
    uploadResult.value.setLoading();
    await pipe(
        documentRepo.upload(namespace, file),
        TE.fold(
            err => T.of(uploadResult.value.setError(err.msg)),
            () => {
                listMyDocuments();
                return T.of(uploadResult.value.setValue(null));
            }
        )
    )();
};

export const myDocuments = ref(new Result<string, Document[]>([]));

export const listMyDocuments = async () => {
    myDocuments.value.setLoading();
    await pipe(
        documentRepo.listMy(0, 10),
        TE.fold(
            err => T.of(myDocuments.value.setError(err.msg)),
            res => T.of(myDocuments.value.setValue(res))
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

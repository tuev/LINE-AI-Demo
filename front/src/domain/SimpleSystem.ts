export interface Answer {
    question: string;
    result: string;
    references: Reference[];
    duration_ms: number;
    timestamp: Date;
}

export interface Reference {
    namespace: string;
    doc_id: string;
    filename: string;
    metadata: Metadata;
    similarity: number;
    upload_by: string;
    upload_at: Date;
}

export interface Metadata {
    content: string;
    page_number: number;
}

export interface AggerateReferencePage {
    page_number: number;
    similarity: number;
}

export interface AggerateReference {
    doc_id: string;
    filename: string;
    pages: AggerateReferencePage[];
}

export const aggerateReferences = (references: Reference[]) => {
    const referencesMap: {[doc_id: string]: AggerateReference} = {};
    for (let reference of references) {
        const pageInfo: AggerateReferencePage = {
            page_number: reference.metadata.page_number,
            similarity: reference.similarity,
        };
        if (!referencesMap[reference.doc_id]) {
            referencesMap[reference.doc_id] = {
                doc_id: reference.doc_id,
                filename: reference.filename,
                pages: [pageInfo],
            };
        } else {
            referencesMap[reference.doc_id].pages.push(pageInfo);
        }
    }
    return Object.values(referencesMap);
};

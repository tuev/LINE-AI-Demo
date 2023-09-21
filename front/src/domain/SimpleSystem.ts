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

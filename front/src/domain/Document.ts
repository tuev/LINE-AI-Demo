import { format } from "date-fns";

export interface Document {
    namespace: string;
    doc_id: string;
    filename: string;
    content_type: string;
    bytesize: number;
    upload_by: string;
    upload_at: Date;
    summary: string;
    process_status: string;
    visibility: string;
}

const documentObjectHost = import.meta.env.VITE_DOCUMENT_OBJECT_HOST;

export function documentLink(doc_id: string, page?: number) {
    return documentObjectHost + `/${doc_id}` + (page ? `#page=${page}` : '');
}

export interface DocumentWithSimilarity extends Document {
    similarity: number;
}

export function similarityFormat(similarity: number): string {
    return (similarity * 100).toFixed(2);
}

export function uploadTimestampFormat(d: Date): string {
    return format(d, "yy-MM-dd hh:mm:ss x")
}

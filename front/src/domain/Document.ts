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

export enum UsageType {
    Extract = 'extract',
}

export interface Usage {
    usage_id: string;
    timestamp: Date;
    user_id: string;
    userdetail: Userdetail;
    result: string;
    usage_type: UsageType;
    usage_data: UsageData;
}

export interface UsageData {
    question: string;
    result: string;
    references: UsageReference[];
    duration_ms: number;
    timestamp: Date;
}

export interface UsageReference {
    namespace: string;
    doc_id: string;
    filename: string;
    metadata: UsageMetadata;
    similarity: number;
    upload_by: string;
    upload_at: Date;
}

export interface UsageMetadata {
    content: string;
    page_number: number;
}

export interface Userdetail {
    name: string;
    picture: string;
}

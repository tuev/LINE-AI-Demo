import { format } from "date-fns";

export interface LiffProfile {
	displayName: string;
	pictureUrl: string;
	userId: string;
}

export function tokenTimestampFmt(d: Date) {
    return format(d, "yyyy-MM-dd hh:mm:ss x")
}

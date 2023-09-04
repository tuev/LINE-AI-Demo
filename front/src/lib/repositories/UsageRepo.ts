import type { UsageItem } from '$lib/domain/UsageItem';
import type { AxiosInstance } from 'axios';
import * as TE from 'fp-ts/lib/TaskEither';

export class UsageRepo {
	constructor(private client: AxiosInstance) {}

	listLastUsages() {
		return TE.tryCatch(
			async () => {
				const { data } = await this.client.get('/usage/last_10');
				for (const d of data) {
					d.timestamp = new Date(d.timestamp);
				}
				return data as UsageItem[];
			},
			(err) => {
				console.error('listLastUsages ERR', err);
				return 'cannot get usage';
			}
		);
	}
}

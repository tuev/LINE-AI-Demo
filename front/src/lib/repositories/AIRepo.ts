import axios from 'axios';
import { streamHandler } from './SSEHandler';
import { LLMFinalContent, LLMStreamContent } from '$lib/domain/LLMContent';
import { pipe } from 'fp-ts/lib/function';
import * as E from 'fp-ts/lib/Either';

export class AIRepo {
	constructor(private apiEndpoint: string) {}

	async healthCheck() {
		try {
			await axios.get(`${this.apiEndpoint}/healthz`, { timeout: 5000 });
			return true;
		} catch (e) {
			console.error('healthCheck ERR', e);
			return false;
		}
	}

	async streamCompletion(
		payload: object,
		token: string,
		onNewValue: (value: E.Either<string, LLMStreamContent | LLMFinalContent>) => void
	) {
		await streamHandler(
			//
			`${this.apiEndpoint}/code/completion_stream`,
			payload,
			token,
			(value) => {
				pipe(
					value,
					E.map((result) => {
						const data = JSON.parse(result);
						const { stop } = data;
						const content = stop ? LLMFinalContent.fromApi(data) : LLMStreamContent.fromApi(data);
						onNewValue(E.right(content));
					}),
					E.mapLeft((err) => {
						onNewValue(E.left(err));
					})
				);
			}
		);
	}
}

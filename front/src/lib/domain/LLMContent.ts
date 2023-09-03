import { z } from 'zod';

export class LLMStreamContent {
	constructor(
		//
		public content: string,
		public stop: boolean
	) {}

	static fromApi(v: any) {
		return new LLMStreamContent(
			//
			z.string().parse(v.content),
			z.boolean().parse(v.stop)
		);
	}
}

export class LLMTimings {
	constructor(
		public predicted_ms: number,
		public predicted_n: number,
		public predicted_per_second: number,
		public predicted_per_token_ms: number,
		public prompt_ms: number,
		public prompt_n: number,
		public prompt_per_second: number,
		public prompt_per_token_ms: number
	) {}

	static fromApi(v: any) {
		return new LLMTimings(
			z.coerce.number().default(0).parse(v.predicted_ms),
			z.coerce.number().default(0).parse(v.predicted_n),
			z.coerce.number().default(0).parse(v.predicted_per_second),
			z.coerce.number().default(0).parse(v.predicted_per_token_ms),
			z.coerce.number().default(0).parse(v.prompt_ms),
			z.coerce.number().default(0).parse(v.prompt_n),
			z.coerce.number().default(0).parse(v.prompt_per_second),
			z.coerce.number().default(0).parse(v.prompt_per_token_ms)
		);
	}
}

export class LLMUsage {
	constructor(
		public timings: LLMTimings,
		public tokens_evaluated: number,
		public tokens_predicted: number
	) {}

	static fromApi(v: any) {
		return new LLMUsage(
			//
			LLMTimings.fromApi(v.timings),
			z.coerce.number().default(0).parse(v.tokens_evaluated),
			z.coerce.number().default(0).parse(v.tokens_predicted)
		);
	}
}

export class LLMFinalContent {
	constructor(
		//
		public final_content: string,
		public usage: LLMUsage,
		public stop: boolean
	) {}

	static fromApi(v: any) {
		return new LLMFinalContent(
			//
			z.string().parse(v.final_content),
			LLMUsage.fromApi(v.usage),
			z.boolean().parse(v.stop)
		);
	}
}

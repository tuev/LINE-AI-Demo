import fs from 'fs';
import { parse } from 'yaml';

export const load = async () => {
	const text = fs.readFileSync('static/exampleCodes.yaml').toString();
	const examples = parse(text);
	return {
		examples: examples.example_codes
	};
};

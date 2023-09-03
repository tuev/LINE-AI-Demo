import * as E from 'fp-ts/lib/Either';

export async function streamHandler(
	endpoint: string,
	payload: object,
	token: string,
	onNewValue: (value: E.Either<string, string>) => void
) {
	try {
		const response = await fetch(endpoint, {
			method: 'POST',
			cache: 'no-cache',
			keepalive: true,
			headers: {
				'Content-Type': 'application/json',
				Accept: 'text/event-stream',
				Authorization: `Bearer ${token}`
			},
			body: JSON.stringify(payload)
		});

		if (response.status > 299) {
			const err = await response.json();
			throw err;
		}

		if (response.body == null) {
			throw '>> no body';
		}
		const reader = response.body.getReader();

		while (true) {
			const { value, done } = await reader.read();
			if (done) break;

			const respText = new TextDecoder().decode(value);
			const data = respText.match(/data: (.*)/);

			if (!data || !data[1]) continue; // Server send ping

            console.log('streamHandler Data >>', data[1]);
			onNewValue(E.right(data[1]));
		}
	} catch (e) {
		if (!e) {
			onNewValue(E.left('empty error'));
		} else {
			let out = '';
			switch (typeof e) {
				case 'string':
					out = e;
					break;
				case 'object':
					out = (e as any).detail;
					break;
				default:
					out = String(e);
					break;
			}
			console.error('streamHandler ERR', out);
			onNewValue(E.left(out));
		}
	}
}

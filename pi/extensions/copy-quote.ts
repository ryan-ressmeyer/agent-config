import type { ExtensionAPI, SessionEntry } from "@earendil-works/pi-coding-agent";

type CopyToClipboard = (text: string) => Promise<void>;

async function copyWithPi(text: string): Promise<void> {
	const { copyToClipboard } = await import("@earendil-works/pi-coding-agent");
	await copyToClipboard(text);
}

function prose(lines: string[]): string | undefined {
	const paragraphs: string[] = [];
	let paragraph: string[] = [];

	for (const line of lines) {
		if (line.trim()) {
			paragraph.push(line.trim());
		} else if (paragraph.length) {
			paragraphs.push(paragraph.join(" "));
			paragraph = [];
		}
	}
	if (paragraph.length) paragraphs.push(paragraph.join(" "));

	return paragraphs.join("\n\n") || undefined;
}

function lastBlockquote(markdown: string): string | undefined {
	let fence: string | undefined;
	let quoteLines: string[] = [];
	let lastQuote: string | undefined;

	const finishQuote = () => {
		lastQuote = prose(quoteLines) ?? lastQuote;
		quoteLines = [];
	};

	for (const line of markdown.split(/\r?\n/)) {
		if (fence) {
			const closing = line.match(/^ {0,3}(`{3,}|~{3,})\s*$/)?.[1];
			if (closing?.[0] === fence[0] && closing.length >= fence.length) fence = undefined;
			continue;
		}

		const opening = line.match(/^ {0,3}(`{3,}|~{3,})/)?.[1];
		if (opening) {
			finishQuote();
			fence = opening;
			continue;
		}

		const quoted = line.match(/^ {0,3}> ?(.*)$/);
		if (quoted) quoteLines.push(quoted[1]);
		else finishQuote();
	}
	finishQuote();

	return lastQuote;
}

function findLatestQuote(branch: SessionEntry[]): string | undefined {
	for (let i = branch.length - 1; i >= 0; i--) {
		const entry = branch[i];
		if (entry.type !== "message" || entry.message.role !== "assistant") continue;

		for (let j = entry.message.content.length - 1; j >= 0; j--) {
			const content = entry.message.content[j];
			if (content.type !== "text") continue;
			const quote = lastBlockquote(content.text);
			if (quote) return quote;
		}
	}
	return undefined;
}

export default function copyQuoteExtension(pi: ExtensionAPI, copy: CopyToClipboard = copyWithPi) {
	pi.registerCommand("copy-quote", {
		description: "Copy the latest assistant blockquote",
		handler: async (_args, ctx) => {
			const quote = findLatestQuote(ctx.sessionManager.getBranch());
			if (!quote) {
				ctx.ui.notify("No assistant blockquote found", "info");
				return;
			}

			try {
				await copy(quote);
				ctx.ui.notify("Copied quote to clipboard", "info");
			} catch (error) {
				const message = error instanceof Error ? error.message : String(error);
				ctx.ui.notify(`Could not copy quote: ${message}`, "error");
			}
		},
	});
}

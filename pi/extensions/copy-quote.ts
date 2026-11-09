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

function lastBashBlock(markdown: string): string | undefined {
	let fence: string | undefined;
	let shell = false;
	let lines: string[] = [];
	let lastBlock: string | undefined;

	for (const rawLine of markdown.split(/(?<=\n)/)) {
		const line = rawLine.replace(/\r?\n$/, "");
		if (fence) {
			const closing = line.match(/^ {0,3}(`{3,}|~{3,})[ \t]*$/)?.[1];
			if (closing?.[0] === fence[0] && closing.length >= fence.length) {
				const block = lines.join("").replace(/\r?\n$/, "");
				if (shell && block.trim()) lastBlock = block;
				fence = undefined;
				lines = [];
			} else if (shell) {
				lines.push(rawLine);
			}
			continue;
		}

		const opening = line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
		if (!opening || (opening[1][0] === "`" && opening[2].includes("`"))) continue;
		fence = opening[1];
		shell = /^(bash|sh|shell)(?:[ \t]|$)/.test(opening[2].trim());
	}
	return lastBlock;
}

function findLatestBlock(
	branch: SessionEntry[],
	extract: (markdown: string) => string | undefined,
): string | undefined {
	for (let i = branch.length - 1; i >= 0; i--) {
		const entry = branch[i];
		if (entry.type !== "message" || entry.message.role !== "assistant") continue;

		for (let j = entry.message.content.length - 1; j >= 0; j--) {
			const content = entry.message.content[j];
			if (content.type !== "text") continue;
			const block = extract(content.text);
			if (block) return block;
		}
	}
	return undefined;
}

export default function copyQuoteExtension(pi: ExtensionAPI, copy: CopyToClipboard = copyWithPi) {
	for (const [name, kind, label, extract] of [
		["copy-quote", "blockquote", "quote", lastBlockquote],
		["copy-bash", "bash block", "bash block", lastBashBlock],
	] as const) {
		pi.registerCommand(name, {
			description: `Copy the latest assistant ${kind}`,
			handler: async (_args, ctx) => {
				const block = findLatestBlock(ctx.sessionManager.getBranch(), extract);
				if (!block) {
					ctx.ui.notify(`No assistant ${kind} found`, "info");
					return;
				}

				try {
					await copy(block);
					ctx.ui.notify(`Copied ${label} to clipboard`, "info");
				} catch (error) {
					const message = error instanceof Error ? error.message : String(error);
					ctx.ui.notify(`Could not copy ${label}: ${message}`, "error");
				}
			},
		});
	}
}

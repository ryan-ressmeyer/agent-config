import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { test } from "node:test";

const extensionUrl = new URL("../pi/extensions/copy-quote.ts", import.meta.url);

async function runCopyQuote(branch, copy) {
  const extension = existsSync(extensionUrl) ? await import(extensionUrl) : {};
  let command;
  let copied;
  let thrown;
  const notifications = [];

  extension.default?.(
    {
      registerCommand(name, options) {
        if (name === "copy-quote") command = options;
      },
    },
    copy ?? (async (text) => {
      copied = text;
    }),
  );

  assert.ok(command, "the copy-quote command is registered");
  try {
    await command.handler("", {
      sessionManager: { getBranch: () => branch },
      ui: { notify: (message, level) => notifications.push([message, level]) },
    });
  } catch (error) {
    thrown = error;
  }

  return { copied, notifications, thrown };
}

const entry = (message) => ({ type: "message", message });

test("copies the last prose blockquote from the newest assistant message", async () => {
  const result = await runCopyQuote([
    entry({ role: "assistant", content: [{ type: "text", text: "> Stale quote." }] }),
    entry({ role: "toolResult", content: [{ type: "text", text: "> Tool quote." }] }),
    entry({
      role: "assistant",
      content: [
        { type: "thinking", thinking: "> Hidden reasoning." },
        {
          type: "text",
          text: [
            "> Earlier quote.",
            "",
            "> The reported effect (Smith et al., $\\alpha = .05$)",
            "> remains intact across this soft wrap.",
            ">",
            "> A second paragraph keeps `inline code`.",
            "",
            "```md",
            "> Example, not a real quote.",
            "```",
          ].join("\n"),
        },
      ],
    }),
    entry({ role: "user", content: "> User quote." }),
  ]);

  assert.equal(
    result.copied,
    "The reported effect (Smith et al., $\\alpha = .05$) remains intact across this soft wrap.\n\nA second paragraph keeps `inline code`.",
  );
  assert.deepEqual(result.notifications, [["Copied quote to clipboard", "info"]]);
  assert.equal(result.thrown, undefined);
});

test("notifies when the branch has no nonempty assistant blockquote", async () => {
  const result = await runCopyQuote([
    entry({ role: "assistant", content: [{ type: "text", text: ">   \n\nNo quote here." }] }),
    entry({ role: "user", content: "> User quote." }),
  ]);

  assert.equal(result.copied, undefined);
  assert.equal(result.thrown, undefined);
  assert.deepEqual(result.notifications, [["No assistant blockquote found", "info"]]);
});

test("reports clipboard failures without throwing", async () => {
  const result = await runCopyQuote(
    [entry({ role: "assistant", content: [{ type: "text", text: "> Quotable." }] })],
    async () => {
      throw new Error("clipboard denied");
    },
  );

  assert.equal(result.thrown, undefined);
  assert.deepEqual(result.notifications, [["Could not copy quote: clipboard denied", "error"]]);
});

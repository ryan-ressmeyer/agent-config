import assert from "node:assert/strict";
import { test } from "node:test";
import copyQuoteExtension from "../pi/extensions/copy-quote.ts";

const text = (value) => ({ type: "text", text: value });
const entry = (role, content) => ({ type: "message", message: { role, content } });
const assistant = (value) => entry("assistant", [text(value)]);

async function runCopyBash(branch, copy) {
  let command;
  const copied = [];
  const notifications = [];
  copyQuoteExtension(
    {
      registerCommand(name, options) {
        if (name === "copy-bash") command = options;
      },
    },
    copy ?? (async (value) => {
      copied.push(value);
    }),
  );
  assert.ok(command, "the copy-bash command is registered");
  await command.handler("", {
    sessionManager: { getBranch: () => branch },
    ui: { notify: (message, level) => notifications.push([message, level]) },
  });
  return { copied, notifications };
}

test("copies only the latest shell block from assistant text on the current branch", async () => {
  const result = await runCopyBash([
    assistant("```bash\nprintf stale\n```"),
    entry("assistant", [
      text("```sh\nprintf earlier-content\n```"),
      text("```bash\nprintf earlier-block\n```\n\n```shell\nprintf latest\n```\n```js\nnotShell()\n```"),
      { type: "thinking", thinking: "```bash\nprintf hidden\n```" },
    ]),
    assistant("Only prose and `inline code`.\n```python\nprint('ignore')\n```"),
    entry("toolResult", [text("```bash\nprintf tool\n```")]),
    entry("user", "```bash\nprintf user\n```"),
    { type: "custom_message", content: "```bash\nprintf custom\n```" },
  ]);
  assert.deepEqual(result, {
    copied: ["printf latest"],
    notifications: [["Copied bash block to clipboard", "info"]],
  });
});

test("preserves indentation, blank lines, and line endings without fences", async () => {
  const code = "\r\nif true; then\r\n\tprintf '  spaces  '  \r\n\r\n  printf done\r\nfi\r\n";
  const result = await runCopyBash([assistant(`  ~~~sh\r\n${code}\r\n  ~~~~  \r\n`)]);
  assert.deepEqual(result.copied, [code]);
});

test("accepts bash, sh, and shell with matching backtick or tilde fences", async () => {
  for (const [opening, closing] of [
    ["```bash", "```"],
    ["~~~sh", "~~~~ \t"],
    ["   ````shell", "  `````"],
    ["```bash title=example", "```"],
  ]) {
    const result = await runCopyBash([assistant(`${opening}\nprintf copied\n${closing}`)]);
    assert.deepEqual(result.copied, ["printf copied"], opening);
  }
});

test("does not close a block with a different, shorter, or annotated fence", async () => {
  const code = "printf first\n~~~\n```\n```` trailing\n    ````\nprintf last";
  const result = await runCopyBash([assistant(["````bash", code, "````"].join("\n"))]);
  assert.deepEqual(result.copied, [code]);
});

test("skips empty and incomplete blocks while searching backwards", async () => {
  const result = await runCopyBash([
    assistant("```bash\nprintf older\n```"),
    assistant("```sh\nprintf newest-complete\n```\n```bash\n\t \n```\n```shell\nprintf partial"),
    assistant("````bash\nprintf unfinished\n```\n~~~"),
  ]);
  assert.deepEqual(result.copied, ["printf newest-complete"]);
});

test("notifies without copying when no complete nonempty shell block exists", async () => {
  for (const markdown of [
    "No fenced code: `printf inline`.",
    "```bash\n  \t\n```",
    "```bash\nprintf partial",
    "````sh\nprintf partial\n```",
    "~~~shell\nprintf partial\n```",
    "```shell-session\n$ printf transcript\n```",
    "```\nprintf unlabelled\n```",
    "````markdown\n```bash\nprintf nested\n```\n````",
    "```bash`invalid\nprintf invalid\n```",
  ]) {
    const result = await runCopyBash([assistant(markdown)]);
    assert.deepEqual(result, {
      copied: [],
      notifications: [["No assistant bash block found", "info"]],
    }, markdown);
  }
  assert.deepEqual((await runCopyBash([])).copied, []);
});

test("reports clipboard failures without throwing", async () => {
  const result = await runCopyBash(
    [assistant("```bash\nprintf copied\n```")],
    async () => {
      throw new Error("clipboard denied");
    },
  );
  assert.deepEqual(result.notifications, [["Could not copy bash block: clipboard denied", "error"]]);
});

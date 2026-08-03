import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { chmodSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, test } from "node:test";

const coreUrl = new URL("../pi/extensions/agent-config-updater/core.ts", import.meta.url);
const extensionUrl = new URL("../pi/extensions/agent-config-updater/index.ts", import.meta.url);
const tempDirs = [];

function git(cwd, ...args) {
  return execFileSync("git", args, { cwd, encoding: "utf8" }).trim();
}

function createFixture() {
  const root = mkdtempSync(join(tmpdir(), "agent-config-updater-"));
  tempDirs.push(root);
  const remote = join(root, "remote.git");
  const upstream = join(root, "upstream");
  const checkout = join(root, "checkout");

  mkdirSync(upstream);
  git(root, "init", "--bare", "--initial-branch=main", remote);
  git(upstream, "init", "--initial-branch=main");
  git(upstream, "config", "user.name", "Updater Test");
  git(upstream, "config", "user.email", "updater@example.invalid");
  writeFileSync(join(upstream, "config.txt"), "initial\n");
  writeFileSync(join(upstream, "install.sh"), "#!/usr/bin/env bash\nset -euo pipefail\nprintf 'installed\\n' > \"$PWD/install-marker\"\n");
  chmodSync(join(upstream, "install.sh"), 0o755);
  git(upstream, "add", ".");
  git(upstream, "commit", "-m", "initial");
  git(upstream, "remote", "add", "origin", remote);
  git(upstream, "push", "-u", "origin", "main");

  git(root, "clone", remote, checkout);
  git(checkout, "config", "user.name", "Updater Test");
  git(checkout, "config", "user.email", "updater@example.invalid");

  function pushUpstream(text = "upstream change") {
    writeFileSync(join(upstream, "config.txt"), `${text}\n`, { flag: "a" });
    git(upstream, "add", "config.txt");
    git(upstream, "commit", "-m", text);
    git(upstream, "push", "origin", "main");
  }

  return { checkout, pushUpstream };
}

afterEach(() => {
  while (tempDirs.length > 0) rmSync(tempDirs.pop(), { recursive: true, force: true });
});

test("agent-config updater core is installed with the extension", () => {
  assert.equal(existsSync(coreUrl), true);
});

test("agent-config updater has a pi extension entrypoint", () => {
  assert.equal(existsSync(extensionUrl), true);
});

test("blocked update notification names the missing commits and local condition", async () => {
  const { formatBlockedMessage } = await import(extensionUrl);
  const message = formatBlockedMessage("/config", {
    kind: "blocked",
    branch: "main",
    ahead: 0,
    behind: 2,
    reason: "dirty",
  });

  assert.equal(
    message,
    "agent-config is 2 commits behind origin/main, but the checkout has uncommitted changes. Update it manually in /config.",
  );
});

test("reports an up-to-date checkout", async () => {
  const { inspectRepository } = await import(coreUrl);
  const { checkout } = createFixture();

  const state = await inspectRepository(checkout);

  assert.deepEqual(state, { kind: "up-to-date", branch: "main", ahead: 0, behind: 0 });
});

test("offers a clean fast-forward update", async () => {
  const { inspectRepository } = await import(coreUrl);
  const { checkout, pushUpstream } = createFixture();
  pushUpstream();

  const state = await inspectRepository(checkout);

  assert.deepEqual(state, { kind: "update-available", branch: "main", ahead: 0, behind: 1 });
});

test("blocks and reports a dirty checkout that is behind", async () => {
  const { inspectRepository } = await import(coreUrl);
  const { checkout, pushUpstream } = createFixture();
  pushUpstream();
  writeFileSync(join(checkout, "local.txt"), "uncommitted\n");

  const state = await inspectRepository(checkout);

  assert.deepEqual(state, { kind: "blocked", branch: "main", ahead: 0, behind: 1, reason: "dirty" });
});

test("blocks and reports divergence from origin/main", async () => {
  const { inspectRepository } = await import(coreUrl);
  const { checkout, pushUpstream } = createFixture();
  writeFileSync(join(checkout, "local.txt"), "local commit\n");
  git(checkout, "add", "local.txt");
  git(checkout, "commit", "-m", "local change");
  pushUpstream();

  const state = await inspectRepository(checkout);

  assert.deepEqual(state, { kind: "blocked", branch: "main", ahead: 1, behind: 1, reason: "diverged" });
});

test("blocks a checkout on a different branch when main has advanced", async () => {
  const { inspectRepository } = await import(coreUrl);
  const { checkout, pushUpstream } = createFixture();
  git(checkout, "switch", "-c", "work");
  pushUpstream();

  const state = await inspectRepository(checkout);

  assert.deepEqual(state, { kind: "blocked", branch: "work", ahead: 0, behind: 1, reason: "branch" });
});

test("finds the repository from a nested installed extension path", async () => {
  const { findRepositoryRoot } = await import(coreUrl);
  const { checkout } = createFixture();
  const nested = join(checkout, "pi", "extensions", "agent-config-updater");
  mkdirSync(nested, { recursive: true });

  assert.equal(await findRepositoryRoot(nested), checkout);
});

test("fast-forwards, runs install.sh, and returns the installed commit", async () => {
  const { applyRepositoryUpdate, inspectRepository } = await import(coreUrl);
  const { checkout, pushUpstream } = createFixture();
  pushUpstream("new skills");
  await inspectRepository(checkout);

  const result = await applyRepositoryUpdate(checkout);

  assert.equal(result.commit, git(checkout, "rev-parse", "origin/main"));
  assert.equal(readFileSync(join(checkout, "install-marker"), "utf8"), "installed\n");
});

test("startup acceptance applies the update without injecting a slash command", async () => {
  const { default: registerUpdater } = await import(extensionUrl);
  const handlers = new Map();
  const commands = [];
  const notifications = [];
  const sentUserMessages = [];

  const pi = {
    on(event, handler) {
      handlers.set(event, handler);
    },
    registerCommand() {},
    sendUserMessage(message) {
      sentUserMessages.push(message);
    },
    async exec(command, args) {
      commands.push([command, ...args]);
      const invocation = [command, ...args].join(" ");
      if (invocation === "env GIT_TERMINAL_PROMPT=0 AGENT_CONFIG_NONINTERACTIVE=1 git rev-parse --show-toplevel") {
        return { stdout: "/config\n", stderr: "", code: 0, killed: false };
      }
      if (invocation.endsWith("git symbolic-ref --quiet --short HEAD")) {
        return { stdout: "main\n", stderr: "", code: 0, killed: false };
      }
      if (invocation.endsWith("git rev-list --left-right --count HEAD...origin/main")) {
        return { stdout: "0 1\n", stderr: "", code: 0, killed: false };
      }
      if (invocation.endsWith("git rev-parse HEAD")) {
        return { stdout: "1234567890abcdef\n", stderr: "", code: 0, killed: false };
      }
      return { stdout: "", stderr: "", code: 0, killed: false };
    },
  };
  const ctx = {
    hasUI: true,
    ui: {
      async select() {
        return "Update now";
      },
      setStatus() {},
      notify(message) {
        notifications.push(message);
      },
    },
  };

  registerUpdater(pi);
  handlers.get("session_start")({ reason: "startup" }, ctx);
  await new Promise((resolve) => setImmediate(resolve));

  assert.equal(sentUserMessages.length, 0);
  assert.equal(commands.some((parts) => parts.includes("pull")), true);
  assert.equal(commands.some((parts) => parts.includes("/config/install.sh")), true);
  assert.equal(notifications.some((message) => message.includes("Run /reload")), true);
});

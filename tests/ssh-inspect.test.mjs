import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, symlinkSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { after, test } from "node:test";

// Use Pi's own loader and executor, without starting a session or contacting a model.
const piRoot = join(execFileSync("npm", ["root", "-g"], { encoding: "utf8" }).trim(), "@earendil-works/pi-coding-agent");
const { loadExtensions } = await import(pathToFileURL(join(piRoot, "dist/core/extensions/loader.js")));
const root = mkdtempSync(join(tmpdir(), "ssh-inspect-"));
const oldPath = process.env.PATH;
process.env.PATH = `${root}:${oldPath}`;
process.env.SSH_INSPECT_TEST_LOG = join(root, "args.json");
writeFileSync(join(root, "ssh"), `#!/usr/bin/env node
const fs = require('node:fs');
const { spawn } = require('node:child_process');
fs.writeFileSync(process.env.SSH_INSPECT_TEST_LOG, JSON.stringify(process.argv.slice(2)));
if (process.env.SSH_INSPECT_TEST_MODE === 'wait') {
  process.stdout.write('useful partial output\\n');
  setInterval(() => {}, 1000);
} else {
  const child = spawn('/bin/sh', ['-c', process.argv.at(-1)], { stdio: 'inherit', env: { ...process.env, HOME: __dirname } });
  process.on('SIGTERM', () => { child.kill(); process.exit(143); });
  child.on('exit', code => process.exit(code ?? 1));
}
`, { mode: 0o755 });
after(() => {
  process.env.PATH = oldPath;
  delete process.env.SSH_INSPECT_TEST_LOG;
  delete process.env.SSH_INSPECT_TEST_MODE;
  rmSync(root, { recursive: true, force: true });
});
const source = resolve("pi/extensions/ssh-inspect.ts");
const loaded = existsSync(source) ? await loadExtensions([source], root) : { extensions: [], errors: [] };
assert.deepEqual(loaded.errors, [], "extension loads with installed Pi");
const tool = loaded.extensions[0]?.tools.get("ssh_inspect")?.definition;
function inspect(params, signal) {
  assert.ok(tool, "ssh_inspect is registered");
  return tool.execute("test", { host: "some-alias", operation: "read", path: join(root, "text"), ...params }, signal);
}
const text = result => result.content.map(block => block.text).join("\n");
writeFileSync(join(root, "text"), "one\ntwo\nthree\nfour\n");

test("registers a structured tool and enforces safe SSH options without host allowlists", async () => {
  assert.ok(tool, "ssh_inspect is registered");
  assert.equal(tool.parameters.additionalProperties, false);
  for (const host of ["lab-alias", "ryan@machine.tailnet.ts.net", "100.101.2.3", "user@2001:db8::1", "user@[2001:db8::1]"]) {
    const result = await inspect({ host });
    assert.equal(result.isError, false, text(result));
    const args = JSON.parse(readFileSync(process.env.SSH_INSPECT_TEST_LOG, "utf8"));
    assert.equal(args.at(-2), host);
    assert.ok(args.includes("-T"));
    assert.ok(args.includes("-n"));
    for (const option of ["BatchMode=yes", "PreferredAuthentications=publickey", "PasswordAuthentication=no", "KbdInteractiveAuthentication=no", "StrictHostKeyChecking=yes", "UpdateHostKeys=no", "ForwardAgent=no", "ForwardX11=no", "ClearAllForwardings=yes", "PermitLocalCommand=no", "RemoteCommand=none", "ControlMaster=no", "ControlPath=none", "ControlPersist=no", "Tunnel=no", "ForkAfterAuthentication=no"]) assert.ok(args.includes(option), option);
    assert.ok(!args.includes("-F"), "retain trusted identity/routing configuration");
  }
});

test("OpenSSH accepts the generated options and overrides unsafe config without connecting", async () => {
  await inspect({});
  const args = JSON.parse(readFileSync(process.env.SSH_INSPECT_TEST_LOG, "utf8"));
  const config = join(root, "ssh-config");
  writeFileSync(config, "Host *\n  ForwardAgent yes\n  ForwardX11 yes\n  LocalForward 9999 localhost:9999\n  PermitLocalCommand yes\n  RemoteCommand touch INJECTED\n  ControlMaster auto\n  ControlPath /tmp/unsafe-control\n  ForkAfterAuthentication yes\n");
  const resolved = execFileSync("/usr/bin/ssh", ["-G", "-F", config, ...args], { encoding: "utf8" });
  for (const line of ["forwardagent no", "forwardx11 no", "permitlocalcommand no", "controlmaster false", "stricthostkeychecking true", "batchmode yes", "preferredauthentications publickey", "forkafterauthentication no"]) assert.ok(resolved.includes(line), line);
  assert.doesNotMatch(resolved, /^localforward |^remotecommand |^controlpath /m);
  assert.equal(existsSync(join(root, "INJECTED")), false);
});

test("rejects option/shell injection, unknown operations/flags, and irrelevant or unbounded arguments before SSH", async () => {
  for (const params of [
    ...["-oProxyCommand=touch /tmp/x", "host;id", "a b", "$(id)", "user@-host", "ssh://host", "a\nb", "host\n", "a\0b"].map(host => ({ host })),
    { operation: "bash" }, { command: "id" }, { flags: "-R" }, { path: "" }, { path: "a\0b" },
    { offset: 0 }, { offset: 1.5 }, { offset: 10000001 }, { limit: 2001 }, { limit: -1 },
    { operation: "ls", offset: 1 }, { operation: "read", pattern: "x" },
    { operation: "grep" }, { operation: "grep", pattern: "x\ny" }, { operation: "grep", pattern: "x\0y" },
    { operation: "find", maxDepth: 101 }, { operation: "ls", maxDepth: 2 }, { timeout: 0 }, { timeout: 61 },
  ]) {
    rmSync(process.env.SSH_INSPECT_TEST_LOG, { force: true });
    await assert.rejects(() => inspect(params), /invalid|unsupported|required|only/i, JSON.stringify(params));
    assert.equal(existsSync(process.env.SSH_INSPECT_TEST_LOG), false, JSON.stringify(params));
  }
});

test("reads bounded line pages and literal hostile filenames without shell expansion", async () => {
  const name = "- odd ' \" $(touch INJECTED) `touch INJECTED` ; *\nfile";
  writeFileSync(join(root, name), "a\nb\nc\nd\n");
  const result = await inspect({ path: name, offset: 2, limit: 2 });
  assert.equal(result.isError, false, text(result));
  assert.match(text(result), /^b\nc\n/);
  assert.match(text(result), /page|continue/i);
  assert.doesNotMatch(text(result), /^a\n|^d\n/m);
  assert.equal(existsSync(join(root, "INJECTED")), false);
});

test("home expansion and explicit regular-file symlinks work without expanding other shell syntax", async () => {
  symlinkSync(join(root, "text"), join(root, "text-link"));
  const result = await inspect({ path: "~/text-link", limit: 1 });
  assert.equal(result.isError, false, text(result));
  assert.match(text(result), /^one\n/);
  const literal = await inspect({ path: "$HOME/text" });
  assert.equal(literal.isError, true);
});

test("lists and finds dotfiles and literal paths; find uses basename globs and bounded depth", async () => {
  writeFileSync(join(root, ".hidden.txt"), "hidden");
  const listing = await inspect({ operation: "ls", path: root });
  assert.equal(listing.isError, false, text(listing));
  assert.match(text(listing), /\.hidden\.txt/);
  const found = await inspect({ operation: "find", path: root, pattern: "*.txt", maxDepth: 1 });
  assert.equal(found.isError, false, text(found));
  assert.match(text(found), /\.hidden\.txt/);
  assert.doesNotMatch(text(found), /args\.json/);
  mkdirSync(join(root, "nested"));
  writeFileSync(join(root, "nested", "deep.txt"), "deep");
  symlinkSync(join(root, "nested"), join(root, "linked-dir"));
  const shallow = await inspect({ operation: "find", path: root, pattern: "deep.txt", maxDepth: 1 });
  assert.doesNotMatch(text(shallow), /deep\.txt/);
  const deep = await inspect({ operation: "find", path: root, pattern: "deep.txt", maxDepth: 2 });
  assert.match(text(deep), /nested\/deep\.txt/);
  assert.doesNotMatch(text(deep), /linked-dir\/deep\.txt/);
  const none = await inspect({ operation: "find", path: root, pattern: "'$(touch INJECTED)'", maxDepth: 1 });
  assert.equal(none.isError, false, text(none));
  assert.equal(existsSync(join(root, "INJECTED")), false);
});

test("grep is recursive literal single-line matching; no matches differ from errors", async () => {
  const pattern = "-e ' $(touch INJECTED) [.*]";
  writeFileSync(join(root, "search"), `${pattern}\nother\n`);
  const result = await inspect({ operation: "grep", path: root, pattern });
  assert.equal(result.isError, false, text(result));
  assert.match(text(result), /search:1:/);
  const none = await inspect({ operation: "grep", path: join(root, "search"), pattern: "absent" });
  assert.equal(none.isError, false);
  assert.match(text(none), /no matches/i);
  const missing = await inspect({ operation: "grep", path: join(root, "missing"), pattern: "x" });
  assert.equal(missing.isError, true);
  assert.doesNotMatch(text(missing), /no matches/i);
  assert.equal(existsSync(join(root, "INJECTED")), false);
});

test("missing files, directories, FIFOs and devices cannot be read as regular files", async () => {
  execFileSync("mkfifo", [join(root, "fifo")]);
  for (const path of [join(root, "missing"), root, join(root, "fifo"), "/dev/zero"]) {
    const result = await inspect({ path });
    assert.equal(result.isError, true, path);
    assert.match(text(result), /regular file/i);
  }
  const result = await inspect({ operation: "grep", path: join(root, "fifo"), pattern: "x" });
  assert.equal(result.isError, false);
  assert.match(text(result), /no matches/i);
});

test("output truncation preserves partial long lines, caps memory and explicitly marks discarded output", async () => {
  writeFileSync(join(root, "huge"), "useful-prefix" + "x".repeat(300000));
  const result = await inspect({ path: join(root, "huge") });
  assert.match(text(result), /useful-prefix/);
  assert.match(text(result), /truncated/i);
  assert.equal(result.details.truncated, true);
  assert.ok(Buffer.byteLength(text(result)) <= 50 * 1024);
  assert.ok(text(result).split("\n").length <= 2000);
  writeFileSync(join(root, "lines"), "line\n".repeat(3000));
  const lines = await inspect({ operation: "grep", path: join(root, "lines"), pattern: "line" });
  assert.equal(lines.details.truncated, true);
  assert.ok(text(lines).split("\n").length <= 2000);
});

test("stderr flooding is bounded and remains an error with explicit truncation", async () => {
  writeFileSync(join(root, "ls"), "#!/bin/sh\nprintf 'diagnostic-prefix' >&2\nhead -c 300000 /dev/zero | tr '\\000' x >&2\nexit 2\n", { mode: 0o755 });
  try {
    const result = await inspect({ operation: "ls", path: root });
    assert.equal(result.isError, true);
    assert.match(text(result), /diagnostic-prefix/);
    assert.match(text(result), /truncated/i);
    assert.ok(Buffer.byteLength(text(result)) <= 50 * 1024);
  } finally { rmSync(join(root, "ls")); }
});

test("remote execution times out and preserves useful partial output", async () => {
  writeFileSync(join(root, "sed"), "#!/bin/sh\nprintf 'useful partial output\\n'\nexec sleep 10\n", { mode: 0o755 });
  const start = Date.now();
  try {
    const result = await inspect({ timeout: 1 });
    assert.equal(result.isError, true);
    assert.match(text(result), /timed out|timeout/i);
    assert.match(text(result), /useful partial output/);
    assert.ok(Date.now() - start < 5000);
  } finally { rmSync(join(root, "sed")); }
});

test("the local SSH deadline also stops a stalled connection with partial output", async () => {
  process.env.SSH_INSPECT_TEST_MODE = "wait";
  const start = Date.now();
  try {
    const result = await inspect({ timeout: 1 });
    assert.equal(result.isError, true);
    assert.match(text(result), /timed out/i);
    assert.match(text(result), /useful partial output/);
    assert.ok(Date.now() - start < 6500);
  } finally { delete process.env.SSH_INSPECT_TEST_MODE; }
});

test("cancellation stops SSH and preserves partial output; pre-aborted calls never spawn", async () => {
  process.env.SSH_INSPECT_TEST_MODE = "wait";
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 300);
  try {
    const result = await inspect({}, controller.signal);
    assert.equal(result.isError, true);
    assert.match(text(result), /cancel/i);
    assert.match(text(result), /useful partial output/);
    rmSync(process.env.SSH_INSPECT_TEST_LOG, { force: true });
    const preAborted = await inspect({}, controller.signal);
    assert.equal(preAborted.isError, true);
    assert.match(text(preAborted), /cancel/i);
    assert.equal(existsSync(process.env.SSH_INSPECT_TEST_LOG), false);
  } finally { clearTimeout(timer); delete process.env.SSH_INSPECT_TEST_MODE; }
});

import { spawn } from "node:child_process";
import { join } from "node:path";

export type BlockReason = "branch" | "dirty" | "diverged";

export type RepositoryState =
  | { kind: "up-to-date"; branch: string; ahead: number; behind: 0 }
  | { kind: "update-available"; branch: "main"; ahead: 0; behind: number }
  | { kind: "blocked"; branch: string; ahead: number; behind: number; reason: BlockReason };

export interface CommandOptions {
  cwd?: string;
  env?: NodeJS.ProcessEnv;
  timeout?: number;
}

export interface CommandResult {
  stdout: string;
  stderr: string;
  code: number;
  killed: boolean;
}

export type CommandRunner = (
  command: string,
  args: string[],
  options?: CommandOptions,
) => Promise<CommandResult>;

export const runCommand: CommandRunner = (command, args, options = {}) =>
  new Promise((resolve) => {
    const child = spawn(command, args, {
      cwd: options.cwd,
      env: options.env ?? process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    let killed = false;
    let timer: NodeJS.Timeout | undefined;

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => (stdout += chunk));
    child.stderr.on("data", (chunk) => (stderr += chunk));

    if (options.timeout) {
      timer = setTimeout(() => {
        killed = true;
        child.kill("SIGTERM");
      }, options.timeout);
    }

    child.on("error", (error) => {
      if (timer) clearTimeout(timer);
      resolve({ stdout, stderr: `${stderr}${error.message}`, code: 1, killed });
    });
    child.on("close", (code) => {
      if (timer) clearTimeout(timer);
      resolve({ stdout, stderr, code: code ?? 1, killed });
    });
  });

async function mustRun(
  runner: CommandRunner,
  command: string,
  args: string[],
  options?: CommandOptions,
): Promise<string> {
  const result = await runner(command, args, options);
  if (result.killed || result.code !== 0) {
    const detail = [result.stderr, result.stdout].filter(Boolean).join("\n").trim();
    throw new Error(`${command} ${args.join(" ")} failed${detail ? `: ${detail}` : ""}`);
  }
  return result.stdout.trim();
}

function gitEnvironment(): NodeJS.ProcessEnv {
  return { ...process.env, GIT_TERMINAL_PROMPT: "0" };
}

export async function findRepositoryRoot(
  startPath: string,
  runner: CommandRunner = runCommand,
): Promise<string> {
  return mustRun(runner, "git", ["rev-parse", "--show-toplevel"], { cwd: startPath, timeout: 10_000 });
}

export async function inspectRepository(
  repoRoot: string,
  runner: CommandRunner = runCommand,
): Promise<RepositoryState> {
  const options = { cwd: repoRoot, env: gitEnvironment(), timeout: 30_000 };
  await mustRun(runner, "git", ["fetch", "--quiet", "origin", "main"], options);

  const branchResult = await runner("git", ["symbolic-ref", "--quiet", "--short", "HEAD"], options);
  const branch = branchResult.code === 0 ? branchResult.stdout.trim() : "(detached)";
  const dirty = (await mustRun(runner, "git", ["status", "--porcelain"], options)).length > 0;
  const counts = await mustRun(runner, "git", ["rev-list", "--left-right", "--count", "HEAD...origin/main"], options);
  const [ahead, behind] = counts.split(/\s+/).map((value) => Number.parseInt(value, 10));

  if (behind === 0) return { kind: "up-to-date", branch, ahead, behind: 0 };
  if (branch !== "main") return { kind: "blocked", branch, ahead, behind, reason: "branch" };
  if (dirty) return { kind: "blocked", branch, ahead, behind, reason: "dirty" };
  if (ahead > 0) return { kind: "blocked", branch, ahead, behind, reason: "diverged" };
  return { kind: "update-available", branch: "main", ahead: 0, behind };
}

export async function applyRepositoryUpdate(
  repoRoot: string,
  runner: CommandRunner = runCommand,
): Promise<{ commit: string }> {
  const state = await inspectRepository(repoRoot, runner);
  if (state.kind !== "update-available") {
    throw new Error(`agent-config cannot be updated safely (${state.kind})`);
  }

  const gitOptions = { cwd: repoRoot, env: gitEnvironment(), timeout: 60_000 };
  await mustRun(runner, "git", ["pull", "--ff-only", "origin", "main"], gitOptions);
  await mustRun(runner, join(repoRoot, "install.sh"), [], {
    cwd: repoRoot,
    env: { ...process.env, AGENT_CONFIG_NONINTERACTIVE: "1" },
    timeout: 120_000,
  });
  const commit = await mustRun(runner, "git", ["rev-parse", "HEAD"], gitOptions);
  return { commit };
}

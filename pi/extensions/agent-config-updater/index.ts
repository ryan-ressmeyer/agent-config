import type {
  ExtensionAPI,
  ExtensionCommandContext,
  ExtensionContext,
} from "@earendil-works/pi-coding-agent";
import { realpathSync } from "node:fs";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import {
  applyRepositoryUpdate,
  findRepositoryRoot,
  inspectRepository,
  type BlockReason,
  type CommandRunner,
  type RepositoryState,
} from "./core.ts";

const extensionDirectory = realpathSync(dirname(fileURLToPath(import.meta.url)));

function plural(count: number, singular: string): string {
  return `${count} ${singular}${count === 1 ? "" : "s"}`;
}

export function formatBlockedMessage(repoRoot: string, state: Extract<RepositoryState, { kind: "blocked" }>): string {
  const behind = plural(state.behind, "commit");
  const reasons: Record<BlockReason, string> = {
    branch: `the current branch is ${state.branch}; switch to main first`,
    dirty: "the checkout has uncommitted changes",
    diverged: `main has ${plural(state.ahead, "local commit")} and has diverged`,
  };
  return `agent-config is ${behind} behind origin/main, but ${reasons[state.reason]}. Update it manually in ${repoRoot}.`;
}

export default function (pi: ExtensionAPI) {
  let startupCheckStarted = false;
  let promptOpen = false;

  const runner: CommandRunner = async (command, args, options = {}) => {
    return pi.exec(
      "env",
      ["GIT_TERMINAL_PROMPT=0", "AGENT_CONFIG_NONINTERACTIVE=1", command, ...args],
      { cwd: options.cwd, timeout: options.timeout },
    );
  };

  async function getRepositoryRoot(): Promise<string> {
    return findRepositoryRoot(extensionDirectory, runner);
  }

  async function applyUpdate(ctx: ExtensionCommandContext, repoRoot: string): Promise<void> {
    ctx.ui.setStatus("agent-config-updater", "Updating agent-config...");
    let commit: string;
    try {
      commit = (await applyRepositoryUpdate(repoRoot, runner)).commit;
    } catch (error) {
      ctx.ui.setStatus("agent-config-updater", undefined);
      ctx.ui.notify(`agent-config update failed: ${error instanceof Error ? error.message : String(error)}`, "error");
      return;
    }

    ctx.ui.setStatus("agent-config-updater", undefined);
    ctx.ui.notify(`agent-config updated to ${commit.slice(0, 8)}. Reloading resources...`, "info");
    await ctx.reload();
    return;
  }

  async function offerUpdate(
    ctx: ExtensionContext,
    state: Extract<RepositoryState, { kind: "update-available" }>,
  ): Promise<boolean> {
    if (!ctx.hasUI || promptOpen) return false;
    promptOpen = true;
    try {
      const choice = await ctx.ui.select(
        `agent-config is ${plural(state.behind, "commit")} behind origin/main`,
        ["Update now", "Skip"],
      );
      return choice === "Update now";
    } finally {
      promptOpen = false;
    }
  }

  async function check(
    ctx: ExtensionContext,
    options: { reportErrors: boolean; commandContext?: ExtensionCommandContext },
  ): Promise<void> {
    let repoRoot: string;
    let state: RepositoryState;
    try {
      repoRoot = await getRepositoryRoot();
      state = await inspectRepository(repoRoot, runner);
    } catch (error) {
      if (options.reportErrors && ctx.hasUI) {
        ctx.ui.notify(`Could not check agent-config: ${error instanceof Error ? error.message : String(error)}`, "warning");
      }
      return;
    }

    if (state.kind === "up-to-date") {
      if (options.reportErrors && ctx.hasUI) ctx.ui.notify("agent-config is up to date.", "info");
      return;
    }

    if (state.kind === "blocked") {
      if (ctx.hasUI) ctx.ui.notify(formatBlockedMessage(repoRoot, state), "warning");
      return;
    }

    const accepted = await offerUpdate(ctx, state);
    if (!accepted) return;

    if (options.commandContext) {
      await applyUpdate(options.commandContext, repoRoot);
      return;
    }

    pi.sendUserMessage("/config-update --apply");
  }

  pi.on("session_start", (event, ctx) => {
    if (event.reason === "reload" || event.reason === "fork" || startupCheckStarted) return;
    startupCheckStarted = true;
    void check(ctx, { reportErrors: false });
  });

  pi.registerCommand("config-update", {
    description: "Check for agent-config updates and safely install them",
    handler: async (args, ctx) => {
      if (args.trim() === "--apply") {
        try {
          await applyUpdate(ctx, await getRepositoryRoot());
        } catch (error) {
          ctx.ui.notify(`Could not locate agent-config: ${error instanceof Error ? error.message : String(error)}`, "error");
        }
        return;
      }
      await check(ctx, { reportErrors: true, commandContext: ctx });
    },
  });
}

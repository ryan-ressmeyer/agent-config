/**
 * agent-bell — ring the terminal bell when pi settles and wants input.
 *
 * The tmux config (dotfiles/tmux.conf, "Agent turn indicator") renders the
 * per-window bell flag in red with a `!`, so a backgrounded pi window
 * announces itself in the tab line the moment it stops working. Claude Code
 * gets the same behaviour from a `Stop` hook in ~/.claude/settings.json; this
 * extension is pi's half of that contract.
 *
 * `agent_settled` is the right event, not `turn_end`: pi fires turn_end after
 * every turn in the agent loop, including the tool-call turns it takes on its
 * own, which would beep continuously while it works. agent_settled fires once,
 * after the run has fully settled with no automatic retry, compaction, or
 * queued continuation pending — i.e. exactly when the ball is back in your court.
 *
 * The BEL goes to /dev/tty rather than stdout so it cannot interleave with the
 * TUI's own rendering of stdout, and so it still reaches the terminal when pi's
 * stdout is redirected.
 */

import { closeSync, openSync, writeSync } from "node:fs";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

function ringBell(): void {
	let fd: number | undefined;
	try {
		fd = openSync("/dev/tty", "w");
		writeSync(fd, "\x07");
	} catch {
		// No controlling terminal (piped, --print mode, CI). Nothing to ring.
	} finally {
		if (fd !== undefined) {
			try {
				closeSync(fd);
			} catch {
				/* ignore */
			}
		}
	}
}

export default function (pi: ExtensionAPI) {
	pi.on("agent_settled", () => {
		ringBell();
	});
}

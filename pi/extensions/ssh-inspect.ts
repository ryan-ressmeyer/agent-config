import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { truncateHead } from "@earendil-works/pi-coding-agent";
import { StringEnum } from "@earendil-works/pi-ai";
import { Type } from "typebox";

const parameters = Type.Object({
  host: Type.String({ description: "SSH alias, DNS/IP address, or user@host (no URI, port or options)." }),
  operation: StringEnum(["read", "ls", "find", "grep"] as const),
  path: Type.String({ description: "Literal remote path; relative to login directory. ~/ uses remote HOME. No shell expansion." }),
  pattern: Type.Optional(Type.String({ description: "Required literal single-line text for grep; optional basename glob for find (default *)." })),
  offset: Type.Optional(Type.Integer({ minimum: 1, maximum: 10000000, description: "read only: first line, 1-based (default 1)." })),
  limit: Type.Optional(Type.Integer({ minimum: 1, maximum: 2000, description: "read only: maximum lines (default 200)." })),
  maxDepth: Type.Optional(Type.Integer({ minimum: 0, maximum: 100, description: "find only: maximum depth (default 5)." })),
  timeout: Type.Optional(Type.Integer({ minimum: 1, maximum: 60, description: "Remote execution seconds (default 20); local SSH deadline adds 3 seconds." })),
}, { additionalProperties: false });

// SSH joins command arguments into a shell string: JSON quoting is NOT shell quoting.
const quote = (value: string) => `'${value.replaceAll("'", "'\\''")}'`;
const hostSyntax = /^(?:[A-Za-z0-9_][A-Za-z0-9_.-]*@)?(?:[A-Za-z0-9_][A-Za-z0-9_.:%-]*|\[[A-Fa-f0-9:]+(?:%[A-Za-z0-9_.-]+)?\])$/;
const sshOptions = [
  "BatchMode=yes", "PreferredAuthentications=publickey", "PasswordAuthentication=no",
  "KbdInteractiveAuthentication=no", "StrictHostKeyChecking=yes", "UpdateHostKeys=no",
  "ForwardAgent=no", "ForwardX11=no", "ClearAllForwardings=yes", "Tunnel=no",
  "PermitLocalCommand=no", "RemoteCommand=none", "RequestTTY=no", "SessionType=default",
  "ControlMaster=no", "ControlPath=none", "ControlPersist=no", "ForkAfterAuthentication=no",
  "ConnectionAttempts=1", "ConnectTimeout=10", "ServerAliveInterval=5", "ServerAliveCountMax=2",
  "EscapeChar=none", "LogLevel=ERROR",
];

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "ssh_inspect",
    label: "SSH inspect",
    description: "Read-only SSH discovery on any destination/path: read regular-file line pages, ls including dotfiles, find basename globs without following symlinks, or recursive literal grep (binary files/devices skipped). Requires trusted SSH config/keys/known hosts, a POSIX login shell and GNU timeout, sed, ls, find, grep remotely. No arbitrary commands/flags. Captures at most 64 KiB combined stdout/stderr; returns at most 48 KiB/1900 lines plus explicit status. Truncated output is discarded; narrow the search or paginate read. This is not a sandbox; readable secrets are accessible.",
    promptSnippet: "Inspect remote files using fixed read, ls, find, or literal grep over SSH",
    parameters,
    async execute(_id, params, signal) {
      // Recheck trust-boundary constraints even after Pi schema validation/tool-call hooks.
      const allowed = ["host", "operation", "path", "timeout"];
      if (params.operation === "read") allowed.push("offset", "limit");
      if (params.operation === "find") allowed.push("pattern", "maxDepth");
      if (params.operation === "grep") allowed.push("pattern");
      if (Object.keys(params).some(key => !allowed.includes(key))) throw new Error("Unsupported or irrelevant argument for operation");
      if (typeof params.host !== "string" || params.host.length > 512 || !hostSyntax.test(params.host)) throw new Error("Invalid SSH destination");
      if (typeof params.path !== "string" || !params.path || params.path.length > 16384 || params.path.includes("\0")) throw new Error("Invalid remote path");
      if (params.pattern !== undefined && (typeof params.pattern !== "string" || params.pattern.length > 16384 || /[\0\n\r]/.test(params.pattern))) throw new Error("Invalid single-line pattern");
      if (params.operation === "grep" && params.pattern === undefined) throw new Error("Pattern is required for grep");
      for (const [key, min, max] of [["offset", 1, 10000000], ["limit", 1, 2000], ["maxDepth", 0, 100], ["timeout", 1, 60]] as const) {
        const value = params[key];
        if (value !== undefined && (!Number.isInteger(value) || value < min || value > max)) throw new Error(`Invalid ${key}: expected integer ${min}..${max}`);
      }

      const offset = params.offset ?? 1;
      const end = offset + (params.limit ?? 200) - 1;
      let command: string;
      switch (params.operation) {
        case "read":
          command = `[ -f "$p" ] && [ -r "$p" ] || { printf '%s\\n' 'Not a readable regular file' >&2; exit 2; }; exec sed -n '${offset},${end}p;${end}q' -- "$p"`;
          break;
        case "ls":
          command = 'exec ls -lab --quoting-style=shell-escape-always -- "$p"';
          break;
        case "find":
          command = `exec find -P "$p" -maxdepth ${params.maxDepth ?? 5} -name ${quote(params.pattern ?? "*")} -print`;
          break;
        case "grep":
          command = `exec grep -r -n -H -I -F --devices=skip --color=never -e ${quote(params.pattern!)} -- "$p"`;
          break;
        default:
          throw new Error("Unsupported operation");
      }
      // Prefix relative paths so even '-' and find expression-like names remain operands.
      const script = `LC_ALL=C; export LC_ALL; p=${quote(params.path)}; case "$p" in '~') p=$HOME ;; '~/'*) p="$HOME/\${p#??}" ;; /*) ;; *) p="./$p" ;; esac; ${command}`;
      const seconds = params.timeout ?? 20;
      const remote = `exec timeout -k 1s ${seconds}s sh -c ${quote(script)}`;
      if (signal?.aborted) return { content: [{ type: "text", text: "Cancelled before SSH started." }], details: { cancelled: true }, isError: true };
      const result = await pi.exec("ssh", ["-T", "-n", ...sshOptions.flatMap(option => ["-o", option]), "--", params.host, remote], {
        signal, timeout: (seconds + 3) * 1000, maxBuffer: 64 * 1024,
      });
      const cancelled = signal?.aborted ?? false;
      const timedOut = !cancelled && !result.truncated && (result.killed || result.code === 124 || result.code === 137);
      const noMatches = params.operation === "grep" && result.code === 1 && !result.killed && !result.stderr;
      const isError = cancelled || timedOut || result.killed || (result.code !== 0 && !noMatches);
      let output = (result.stderr ? `[stderr]\n${result.stderr}\n[stdout]\n` : "") + result.stdout;
      // Byte-bound first: truncateHead otherwise discards useful oversized lines.
      const bytes = Buffer.from(output);
      const prefix = new TextDecoder().decode(bytes.subarray(0, 48 * 1024), { stream: true });
      const clipped = truncateHead(prefix, { maxBytes: 48 * 1024, maxLines: 1900 });
      output = clipped.content;
      const truncated = result.truncated || bytes.length > 48 * 1024 || clipped.truncated;
      const status = cancelled ? "Cancelled; partial output follows." : timedOut ? "SSH/remote execution timed out; partial output follows." : isError ? `SSH operation failed (exit ${result.code}); partial output follows.` : "";
      if (status) output = `${status}\n${output}`;
      if (noMatches) output += "\nNo matches found.";
      if (truncated) output += "\n[Output truncated; remainder discarded, not saved. Narrow path/pattern or use smaller read pages.]";
      if (params.operation === "read" && !isError) output += `\n[Requested lines ${offset}-${end}; continue with offset=${end + 1} if needed. EOF may have been reached.]`;
      return {
        content: [{ type: "text", text: output || "(no output)" }],
        details: { code: result.code, truncated, cancelled, timedOut },
        isError,
      };
    },
  });
}

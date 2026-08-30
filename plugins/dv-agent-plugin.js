/**
 * DV Agent v0.1.0 OpenCode plugin.
 *
 * Responsibilities:
 *   1. Initialize PWD/.knowledge/{knowledge,sources,candidates}
 *   2. Block direct RTL access through OpenCode tool execution
 *   3. Trigger knowledge-learning once when a session becomes idle
 *
 * No external dependencies are required.
 */

const RTL_PATH_SEGMENTS = [
  "/rtl/",
  "/rtl_asic/",
  "/rtl_design/",
];

const RTL_COMMAND_PATTERNS = [
  /\b(?:cat|less|more|head|tail|sed|awk|grep|rg|find|xargs)\b[^\n]*(?:\/rtl\/|\/rtl_asic\/|\/rtl_design\/)/i,
  /\b(?:cp|mv|tar|zip|unzip)\b[^\n]*(?:\/rtl\/|\/rtl_asic\/|\/rtl_design\/)/i,
];

function normalizePath(value) {
  if (typeof value !== "string") return "";
  return value.replaceAll("\\", "/").toLowerCase();
}

function looksLikeRtlPath(value) {
  const normalized = normalizePath(value);
  if (!normalized) return false;

  if (RTL_PATH_SEGMENTS.some((segment) => normalized.includes(segment))) return true;

  return false;
}

function containsRtlReference(value) {
  if (typeof value === "string") {
    return looksLikeRtlPath(value);
  }

  if (Array.isArray(value)) {
    return value.some(containsRtlReference);
  }

  if (value && typeof value === "object") {
    return Object.values(value).some(containsRtlReference);
  }

  return false;
}

function isRtlShellCommand(command) {
  if (typeof command !== "string") return false;
  return RTL_COMMAND_PATTERNS.some((pattern) => pattern.test(command));
}

function isRtlToolInvocation(input, args) {
  const tool = String(input?.tool ?? "").toLowerCase();

  if (tool === "read" || tool === "edit" || tool === "write") {
    return containsRtlReference(args);
  }

  if (tool === "bash" || tool === "shell") {
    if (isRtlShellCommand(args?.command)) return true;
    return containsRtlReference(args);
  }

  return containsRtlReference(args);
}

function knowledgeRoot(directory) {
  return `${directory}/.knowledge`;
}

async function ensureKnowledgeRepository($, directory) {
  await $`mkdir -p ${knowledgeRoot(directory)}/knowledge ${knowledgeRoot(directory)}/sources ${knowledgeRoot(directory)}/candidates`;
}

function learningPrompt(directory) {
  return `
You are performing the automatic Knowledge-learning pass for the completed
OpenCode session.

Current Knowledge scope:
${knowledgeRoot(directory)}

Run the knowledge-learning Skill now.

Rules:
- Analyze only this session and the current PWD-scoped Knowledge repository.
- Never read or access RTL.
- Preserve original evidence in .knowledge/sources/.
- Put AI proposals in .knowledge/candidates/.
- Do not promote candidates directly into confirmed Knowledge.
- Do not create Knowledge for trivial or temporary information.
- Look for reusable DV knowledge, especially DUT behavior, corner cases,
  limitations, known issues, Designer Q&A, debug findings, and reusable DV
  experience.
- Check existing Knowledge for duplicates and contradictions before proposing
  a Candidate.
- If there is nothing worth learning, do nothing.

Do not produce a user-facing explanation unless necessary. This is a background
Knowledge-learning pass.
`.trim();
}

export const DVAgentPlugin = async ({ client, $, directory }) => {
  await ensureKnowledgeRepository($, directory);

  const processedSessions = new Set();
  const learningSessions = new Set();

  return {
    "tool.execute.before": async (input, output) => {
      if (isRtlToolInvocation(input, output?.args)) {
        throw new Error(
          "DV Agent policy violation: RTL access is forbidden. " +
          "The DV Agent must use specification, Designer Q&A, debug records, " +
          "and approved DV Knowledge instead."
        );
      }
    },

    event: async ({ event }) => {
      if (event.type !== "session.idle") return;

      const sessionId = event.properties?.sessionID ?? event.properties?.id;
      if (!sessionId) return;
      if (processedSessions.has(sessionId)) return;
      if (learningSessions.has(sessionId)) return;

      processedSessions.add(sessionId);
      learningSessions.add(sessionId);

      try {
        await client.session.prompt({
          path: { id: sessionId },
          body: {
            parts: [{ type: "text", text: learningPrompt(directory) }],
          },
        });
      } finally {
        learningSessions.delete(sessionId);
      }
    },
  };
};

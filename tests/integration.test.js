import assert from "node:assert/strict";
import test from "node:test";
import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { KnowledgeLearningPlugin } from "../plugins/knowledge-learning-plugin.js";

test("plugin triggers notifications when new candidates are created", async () => {
  // Setup temp directory
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "dv-agent-test-"));
  const knowledgeDir = path.join(tmpDir, ".knowledge");

  let toasts = [];
  let osNotifications = [];

  const mockClient = {
    emit: async (event, data) => {
      if (event === "tui.toast.show") toasts.push(data.message);
    },
    session: {
      prompt: async () => {
        // Simulate background skill creating a candidate
        await fs.writeFile(path.join(knowledgeDir, "candidates", "K-CAND-TEST.md"), "test content");
      }
    }
  };

  const mock$ = async (pieces, ...args) => {
    let cmd = pieces[0];
    for (let i = 0; i < args.length; i++) {
      cmd += args[i] + pieces[i + 1];
    }
    
    if (cmd.includes("mkdir")) {
      await fs.mkdir(path.join(knowledgeDir, "knowledge"), { recursive: true });
      await fs.mkdir(path.join(knowledgeDir, "sources"), { recursive: true });
      await fs.mkdir(path.join(knowledgeDir, "candidates"), { recursive: true });
    } else if (cmd.includes("notify-send") || cmd.includes("osascript") || cmd.includes("powershell")) {
      osNotifications.push(cmd);
    }
    return { quiet: () => {} };
  };

  try {
    const plugin = await KnowledgeLearningPlugin({
      client: mockClient,
      $: mock$,
      directory: tmpDir
    });

    // Trigger session.idle
    await plugin.event({
      event: {
        type: "session.idle",
        properties: { id: "test-session-1" }
      }
    });

    assert.equal(toasts.length, 1, "Should have 1 toast notification");
    assert.match(toasts[0], /1 new Knowledge Candidate\(s\) require review/, "Toast message should match expected format");
    assert.equal(osNotifications.length, 1, "Should have 1 OS notification");

  } finally {
    // Cleanup
    await fs.rm(tmpDir, { recursive: true, force: true });
  }
});

test("plugin warns on startup if candidates already exist", async () => {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "dv-agent-test-"));
  const knowledgeDir = path.join(tmpDir, ".knowledge");
  
  // Pre-create directory and candidate
  await fs.mkdir(path.join(knowledgeDir, "candidates"), { recursive: true });
  await fs.writeFile(path.join(knowledgeDir, "candidates", "PRE-EXISTING.md"), "test content");

  let toasts = [];
  const mockClient = {
    emit: async (event, data) => {
      if (event === "tui.toast.show") toasts.push(data.message);
    }
  };
  
  const mock$ = async () => ({ quiet: () => {} });

  try {
    await KnowledgeLearningPlugin({
      client: mockClient,
      $: mock$,
      directory: tmpDir
    });

    assert.equal(toasts.length, 1, "Should have 1 startup toast notification");
    assert.match(toasts[0], /You have 1 Knowledge Candidate\(s\) waiting for review/, "Startup toast message should match");
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true });
  }
});

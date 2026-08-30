# DV Agent

DV Agent Knowledge system for OpenCode.

## Features

1. **PWD-scoped Knowledge**: Stores knowledge at `$PWD/.knowledge/`
2. **Knowledge Repository**: Structured directories (`knowledge/`, `sources/`, `candidates/`)
3. **Skills**: `knowledge-learning` and `knowledge-review`
4. **Plugin**: `knowledge-learning-plugin.js`
5. **RTL Guard**: Blocks RTL access during OpenCode tool execution
6. **Automation**: Triggers Knowledge-learning on `session.idle`
7. **Notifications**: TUI and OS notifications for pending review queues

*Note: This system is deliberately minimal and operates purely on the local filesystem. It does not implement databases, embeddings, or cross-workspace synchronization.*

## Runtime Layout

```text
PWD/
├── .opencode/
│   ├── plugins/
│   │   └── knowledge-learning-plugin.js
│   └── skills/
│       ├── knowledge-learning/
│       └── knowledge-review/
│
└── .knowledge/
    ├── knowledge/
    ├── sources/
    └── candidates/
```

## Installation

Link the plugin and skills into your OpenCode project directory:

```bash
mkdir -p $PWD/.opencode/plugins $PWD/.opencode/skills

ln -s /path/to/dv-agent/plugins/knowledge-learning-plugin.js $PWD/.opencode/plugins/
ln -s /path/to/dv-agent/skills/knowledge-learning $PWD/.opencode/skills/
ln -s /path/to/dv-agent/skills/knowledge-review $PWD/.opencode/skills/
```

OpenCode automatically loads local plugins and skills from `.opencode/`.

## RTL Guard Limitation

The RTL guard is a policy enforcement layer for direct OpenCode tool calls. It blocks obvious RTL file/path access and RTL-related shell commands. It cannot prove that an arbitrary executable or script will not read RTL internally. For a hard security boundary, RTL must also be inaccessible at the OS/filesystem permission level.

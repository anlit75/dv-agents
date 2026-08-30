# DV Agent

Minimal first version of the DV Agent Knowledge system for OpenCode.

## Scope

v0.1.0 implements only:

1. PWD-scoped Knowledge at `$PWD/.knowledge/`
2. Knowledge repository directories: `knowledge/`, `sources/`, `candidates/`
3. `knowledge-learning` Skill
4. `knowledge-learning-plugin`
5. RTL access guard for OpenCode tool execution
6. Automatic Knowledge-learning trigger on `session.idle`

The plugin deliberately does not implement a database, embeddings, OpenViking,
company-wide retrieval, Jira/Teams/Confluence connectors, or cross-workspace
Knowledge.

## Runtime layout

```text
PWD/
├── .opencode/
│   ├── plugins/
│   │   └── knowledge-learning-plugin.js -> central plugin
│   └── skills/ -> central skills
│
└── .knowledge/
    ├── knowledge/
    ├── sources/
    └── candidates/
```

## Installation

The central deployment system should link the plugin into:

```text
$PWD/.opencode/plugins/knowledge-learning-plugin.js
```

and the Skill into:

```text
$PWD/.opencode/skills/knowledge-learning/
```

OpenCode automatically loads local plugins from `.opencode/plugins/`.

## Important v0.1.0 limitation

The RTL guard is a policy enforcement layer for direct OpenCode tool calls.
It blocks obvious RTL file/path access and RTL-related shell commands. It cannot
prove that an arbitrary executable or script will not read RTL internally.
For a hard security boundary, RTL must also be inaccessible at the OS/filesystem
permission level.

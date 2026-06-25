# Sources

This directory mirrors the Sources area of a ChatGPT Web project.

Start new ChatGPT-Lab sessions by reading these files in order:

1. `sources/SOURCE_INDEX.md`
2. `sources/source-manifest.json`
3. `sources/control-plane/OPERATING_CONTRACT.md`
4. `sources/control-plane/CURRENT_STATE.md`
5. `sources/control-plane/REVIEW_RUBRIC.md`
6. `sources/control-plane/DECISIONS.md`
7. `sources/PROJECT_INSTRUCTIONS.md`

Use `chats/` for conversation context and `docs/research/` for supporting background material. When sources disagree, follow the precedence in `sources/SOURCE_INDEX.md`.

## Browser Oracle

This repository registers the default `$browser-oracle` project in `.ask/browser-oracles.yaml`:

- project name: `chatgpt-lab`
- backend: `webgpt`
- stored binding: `/home/graham/.projects/browser-oracle/webgpt/chatgpt-lab.json`

The current binding points at the ChatGPT-Lab conversation tab supplied by the user. Runtime desktop/window metadata is stored outside Git by the `$browser-oracle` skill.

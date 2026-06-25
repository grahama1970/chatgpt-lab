# Migration Notes

This package was prepared from the ChatGPT-Lab bootstrap control plane formerly held at:

- Repository: `grahama1970/snippets`
- Branch: `chatgpt-lab`
- Path: `chatgpt-lab/`

## Add to the dedicated repository

1. Extract `chatgpt-lab-repo-ready.zip`.
2. Copy the contents of `chatgpt-lab-repo-ready/` into the root of `grahama1970/chatgpt-lab`.
3. Commit and push to `main`.
4. Open the Actions tab and verify **ChatGPT-Lab Source Check** passes.
5. Download the `chatgpt-lab-control-plane-validation` artifact.
6. Change `control_plane.status` in `source-manifest.json` from `BOOTSTRAP_PACKAGE` to `ACTIVE`.
7. Update `sources/control-plane/CURRENT_STATE.md` with the pushed commit and workflow run.
8. Paste or retain `PROJECT_INSTRUCTIONS.md` in the ChatGPT-Lab Project instructions.

## Important

Do not treat the included local validation receipt as proof of the GitHub repository. Only the GitHub Actions run for the pushed commit establishes repository execution evidence.

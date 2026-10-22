# Project Instructions

## Project Context

- Read `README.md` before making changes.
- Read `VNR_GUIDE.md` before implementing or modifying Veneerio GUI code. (Not supported yet)
- This project uses Veneerio, a Python-first desktop GUI framework powered by HTML and CSS.

## Veneerio Development

- Prefer Veneerio's documented public API.
- Follow the API usage examples in `VNR_GUIDE.md`.
- Treat the guide as a starting point, not as proof that an API exists in the installed version.
- If an API, parameter, or behavior is unclear, inspect the installed package's public interface and the corresponding source or tests before using it.
- Do not invent APIs or depend on undocumented internals.
- If the installed version does not support a required feature, explain the limitation instead of silently introducing a workaround that depends on internals.

## Application Design

- Keep application logic and GUI code separate where practical.
- Prefer reusing existing application logic over rewriting it inside GUI callbacks.
- Respect the existing project structure and intent.
- Avoid unnecessary dependencies and unrelated changes.

## Verification

- Read `README.md` for the documented development and verification workflow.
- After changes, run the applicable documented tests and checks, if any.
- Do not assume undocumented commands exist.
- Report which checks were run and any that could not be completed.

# Veneerio — Agent Instructions

## 1. Project Identity

Veneerio is a Python-first desktop GUI framework powered by HTML and CSS.

Its purpose is to help developers add a GUI to existing Python programs without requiring them to build the UI directly with HTML and CSS.

Core principles:

- **Python-first:** Application logic and UI composition should remain accessible through Python.
- **Developer freedom:** The framework should support integration with existing Python code rather than forcing users into an unnecessarily restrictive architecture.
- **Clear APIs:** Public APIs should be explicit, understandable, and predictable.
- **Extensibility:** Add abstractions only when they solve a concrete problem and fit the existing design.
- **Fast feedback:** Development tools should help developers identify problems and iterate efficiently.
- **Honest behavior:** Implementations and documentation must accurately describe what the framework actually supports.

These principles guide implementation decisions but do not override explicit requirements or established contracts.

## 2. Source of Truth

Before making changes, read and follow the relevant sources in this order:

1. The specific GitHub issue and its acceptance criteria define the requested task.
2. This file defines repository-wide agent instructions.
3. `README.md` describes the documented project behavior and usage.
4. Existing source code, tests, and configuration establish the current implementation and verifiable contracts.
5. Relevant documentation, commit history, and issue discussions provide additional context.

If these sources conflict, do not silently choose an interpretation that could introduce a breaking change. Explain the conflict and ask for clarification when necessary.

Do not assume that a planned, discussed, or documented future feature has already been implemented.

## 3. Mandatory Repository Inspection

Before implementation:

1. Read this file and any applicable nested `AGENTS.md` instructions.
2. Read `README.md`.
3. Read the relevant GitHub issue, including its acceptance criteria.
4. Inspect the relevant source files and their callers.
5. Inspect existing tests covering the affected behavior.
6. Inspect `pyproject.toml` and relevant CI or test configuration when determining how to validate changes.
7. Identify public APIs, existing behavior, and compatibility requirements that the change could affect.

Trace behavior through the existing implementation instead of inferring it from names or examples alone.

Do not begin a substantial implementation while important requirements or architectural constraints remain unclear.

## 4. Architecture and Public API

Preserve Veneerio's existing architecture unless the task explicitly requires a design change.

The current project includes:

- `src/vnr/__init__.py`: top-level public exports.
- `src/vnr/`: framework implementation and CLI.
- `src/vnr/ui/`: composable UI primitives.
- `src/vnr/templates/scaffold/`: files used to generate new projects.

Verify the current source tree before relying on this overview. It is not an exhaustive directory specification.

### Public API rules

- Prefer existing public APIs over introducing new ones.
- Inspect the implementation and tests before changing API behavior.
- Do not introduce new public names, parameters, return types, or semantics without a concrete requirement.
- Preserve existing public behavior unless the issue requires a change.
- Update public exports deliberately when adding or changing a public API.
- Keep internal implementation details internal unless there is a justified need to expose them.
- Do not add compatibility layers, aliases, or abstractions without a demonstrated need.
- Do not silently change documented behavior to match an implementation shortcut.

A public API change should include appropriate tests and documentation updates.

If the task requires a significant architectural change not already authorized by the issue, explain the proposed design and obtain approval before proceeding.

## 5. Correctness and Honest Contracts

Never invent APIs, commands, configuration options, or supported behavior.

Before using an API or command:

1. Verify that it exists in the current implementation or configuration.
2. Check its signature and actual behavior.
3. Check whether it is public, internal, experimental, or unsupported.
4. Prefer behavior verified by tests and existing working examples.

Treat the following as distinct:

- **Implemented:** Present in the source code.
- **Verified:** Confirmed by relevant tests or direct execution.
- **Documented:** Described in project documentation.
- **Planned:** Intended for future development.

Do not treat these categories as interchangeable.

When an API's behavior is uncertain, investigate it rather than guessing. If the evidence remains insufficient, report the uncertainty and ask for clarification when it affects the design.

### Known behavioral contract

`State` stores Python-side component values. Changing a stored value does not automatically rerender an already mounted component or update its visible UI.

Do not introduce assumptions about reactive rendering unless a separate, explicitly scoped change establishes that behavior.

Similarly, do not claim that arbitrary Python objects, asynchronous functions, custom renderers, or other planned capabilities are supported unless the current implementation verifies that claim.

## 6. Scope Control and Change Discipline

Implement only what is necessary to satisfy the requested issue.

- Do not perform unrelated refactoring.
- Do not rename or reorganize modules merely for aesthetic consistency.
- Do not rewrite working code when a focused change is sufficient.
- Do not modify unrelated tests, documentation, templates, or configuration.
- Do not change dependency versions or add dependencies without justification.
- Do not introduce new architectural patterns without a concrete need.
- Do not weaken or delete existing tests merely to obtain a passing test suite.
- Do not overwrite user changes or revert unrelated work.

When a requirement can be satisfied within the existing architecture, prefer that solution.

If the requested behavior cannot be implemented correctly without expanding the scope, explain why before proceeding with the expansion.

## 7. Implementation Quality

Follow the conventions established by the surrounding code.

- Prefer simple, explicit implementations over unnecessary indirection.
- Keep responsibilities clear and consistent with the existing architecture.
- Handle errors consistently with neighboring code.
- Preserve useful error information instead of silently swallowing failures.
- Consider platform-specific behavior when modifying process management, filesystem operations, or desktop integration.
- Avoid unnecessary dependencies when the standard library or existing implementation is sufficient.
- Add comments to explain non-obvious reasoning, not to restate the code.
- Avoid speculative generalization for hypothetical future requirements.

Do not optimize or generalize code without a concrete benefit relevant to the task.

## 8. Tests and Verification

Discover the project's actual test and validation procedures before running them.

Use `README.md`, `pyproject.toml`, CI configuration, and existing project conventions to determine which commands are supported.

Do not invent test, lint, formatting, or type-checking commands.

For behavior changes:

- Add tests that cover the new behavior.
- Add regression tests when existing behavior could be affected.
- Test relevant edge cases and error paths.
- Update existing tests when an explicitly authorized contract changes.
- Preserve the intent of existing tests.

Run the relevant tests and, when practical, the broader test suite.

Report exactly which checks were executed and their results. If a check could not be run, explain why. Never claim that unexecuted checks passed.

Inspect the final diff for unintended changes, missing tests, accidental API changes, and unrelated modifications.

## 9. Documentation and Project Templates

Documentation is part of the public contract.

When behavior or public usage changes:

- Update the relevant documentation and examples.
- Verify examples against the actual implementation.
- Do not document unsupported APIs or planned features as available.
- Keep descriptions of limitations accurate.
- Avoid contradictory examples across documentation files.

Pay particular attention to `src/vnr/templates/scaffold/`.

Changes to scaffold templates affect newly generated projects and must be evaluated separately from changes to Veneerio itself.

When changing generated instructions such as `AGENTS.md`, ensure that they describe the public API available to users of the generated project. Do not expose internal implementation assumptions as user-facing API guarantees.

## 10. CLI and Development Workflow

The documented CLI includes `vnr --help`, `vnr --version`, `vnr new`, and `vnr dev`.

Verify the current parser and implementation before modifying CLI behavior.

The current `vnr dev` implementation:

- Uses `main.py` as the project entry point.
- Runs the application in a separate Python process.
- Watches relevant project files for changes and restarts the application.
- Manages the application process lifecycle.

Keep development-server responsibilities separate from framework UI and application APIs.

Do not modify the framework's public API merely to accommodate development-server implementation details.

Do not document planned commands, such as build or packaging commands, as working features unless they have actually been implemented.

## 11. Dependencies and Compatibility

The project currently declares Python `>=3.10` and `pywebview>=6.0` in `pyproject.toml`.

Verify the current configuration before making compatibility or dependency decisions.

- Preserve the declared Python compatibility range unless the task explicitly changes it.
- Avoid introducing dependencies without a clear technical justification.
- Consider Windows, macOS, and Linux behavior when relevant.
- Do not claim cross-platform support based solely on platform-independent-looking code.
- Verify platform-specific changes with available tests and report untested platforms honestly.

## 12. Handling Ambiguity

Ask for clarification before implementation when:

- Acceptance criteria permit materially different API designs.
- A requirement conflicts with an established public contract.
- The task requires an unapproved architectural change.
- An implementation decision could introduce a breaking change.
- Required behavior cannot be established from the issue and repository evidence.

Do not ask questions that can be answered by inspecting the repository.

For minor implementation choices that do not affect public contracts or architecture, use the simplest solution consistent with existing conventions and explain non-obvious decisions in the completion report.

## 13. Completion Report

When the task is complete, report:

### Implemented
Summarize the behavior added or changed.

### Files Changed
List the relevant files and explain why they changed.

### Verification
List the actual commands executed and their results.

### Design Decisions
Explain important implementation decisions and their relationship to existing architecture.

### Limitations
Describe unresolved requirements, unverified behavior, and checks that could not be performed.

### Scope Deviations
Disclose any changes beyond the original issue and explain why they were necessary.

Do not claim full completion if acceptance criteria remain unsatisfied.

Do not commit, push, merge, or publish changes unless explicitly requested.

## 14. Final Principle

The agent is responsible for implementing the requested change, not redefining the project.

Preserve the developer's design intent, respect existing contracts, verify before assuming, and make the smallest correct change that satisfies the issue.
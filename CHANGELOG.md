# Changelog

All notable changes to Veneerio are documented in this file.

This project is under active development. The entries below summarize
the repository's commit history through October 15, 2026. Entries are grouped
by development date, not by release version, because the commits do not
correspond to formal published releases.

## Project Rename

-   Renamed the project from Kayat to Veneerio and updated project branding
    and repository references in the project documentation.
    ([`13ade6d`](https://github.com/nslookup255-pixel/Veneerio/commit/13ade6d2f0d551cb65a92cbe1eaff48e871986b9))

## \[Unreleased\]

### Added

-   Added `vnr dev` with project validation, file polling, and application
    restarts when project files change.
    ([`9471ed3`](https://github.com/nslookup255-pixel/Veneerio/commit/9471ed3ced5f9a33c7e4ac6d55e95f14e375df72))
-   Added the `kayat` CLI with help and version options.
    ([`820b1ff`](https://github.com/nslookup255-pixel/Kayat/commit/820b1ffc069f013bd0e45c5f7de56881121da6b7))
-   Added project creation with template-based scaffolding.
    ([`3a9476a`](https://github.com/nslookup255-pixel/Kayat/commit/3a9476a99a1141b9d4ad08c978931fef5777285a))
-   Added support for Python callables as event handlers. The commit
    reported 67 non-GUI tests.
    ([`6dc0375`](https://github.com/nslookup255-pixel/Kayat/commit/6dc0375f4bf8911442fad4a6dbc55c4802a8c307))
-   Added `to_display_text` and integrated it into `HTMLRenderer` to
    render Python values.
    ([`69facaf`](https://github.com/nslookup255-pixel/Kayat/commit/69facafbbaf7daea8b91b96d19048f16b4dc9f89))
-   Added alert, confirm, and prompt dialogs, plus an example.
    ([`a5deebe`](https://github.com/nslookup255-pixel/Kayat/commit/a5deebe8c0c767b3ebc36351ab5a26b893afb52a),
    [`3000531`](https://github.com/nslookup255-pixel/Kayat/commit/3000531c6db2e481a928f0ab5a53bf7eeca85a1b))
-   Added application icon support and validation in `App` and
    PyWebView.
    ([`eeb25b9`](https://github.com/nslookup255-pixel/Kayat/commit/eeb25b9c592fb745801318f715319bd99f3194df))
-   Added a GitHub Actions workflow for testing and building Python
    packages.
    ([`1555f5c`](https://github.com/nslookup255-pixel/Kayat/commit/1555f5c19de25e1ba11f7021636f67e9745bdb66))

### Changed

-   Updated the package version in `pyproject.toml` to `0.2.0`.
    ([`76c1bfd`](https://github.com/nslookup255-pixel/Kayat/commit/76c1bfdee04b1bbdb63531b65eca9fd44fb7a547))
-   Updated the README to identify `0.3.0` as the planned PyPI release
    version.
    ([`449cdfe`](https://github.com/nslookup255-pixel/Kayat/commit/449cdfe4bce8df3912cf818b0c2a965885cff637))
-   Replaced the README's development-status section with a roadmap and
    later introduced a revised README structure.
    ([`1a8f4f1`](https://github.com/nslookup255-pixel/Kayat/commit/1a8f4f157e923dca99530ac554343e86c2d84679),
    [`27cdcbc`](https://github.com/nslookup255-pixel/Kayat/commit/27cdcbcba6fa28496841258a431aaa51ff0fb0cd))
-   Reorganized core and UI modules and cleaned up project structure and
    documentation.
    ([`a697c97`](https://github.com/nslookup255-pixel/Kayat/commit/a697c97c08ff139643207e052edb191c231ebe1c),
    [`4c5365d`](https://github.com/nslookup255-pixel/Kayat/commit/4c5365de81a06928c10e0ce6a06729ece763a57e))

### Fixed

-   Updated scaffold documentation to use the current Veneerio branding instead of Kayat.
-   Fixed column layout and text rendering.
    ([`05a6d90`](https://github.com/nslookup255-pixel/Kayat/commit/05a6d90d1fbb4fe4593bd03f104bdbaa09bd3faf))
-   Resolved optional-member access warnings in the WebView integration.
    ([`678fc88`](https://github.com/nslookup255-pixel/Kayat/commit/678fc88c80163828f11cf9e29b5e345d3cf37ace))
-   Fixed module mocking in `PyWebViewTest`.
    ([`be6e0fb`](https://github.com/nslookup255-pixel/Kayat/commit/be6e0fba5ad5ffad298606fc812056c9a2394798))

## Development history

### 2026-10-15

-   Implemented project creation with template scaffolding.
    ([`3a9476a`](https://github.com/nslookup255-pixel/Kayat/commit/3a9476a99a1141b9d4ad08c978931fef5777285a))

### 2026-10-08 to 2026-10-10

-   Added CLI help and version options.
    ([`820b1ff`](https://github.com/nslookup255-pixel/Kayat/commit/820b1ffc069f013bd0e45c5f7de56881121da6b7))
-   Updated the planned PyPI release version to `0.3.0` in the README
    and set the project version to `0.2.0`.
    ([`449cdfe`](https://github.com/nslookup255-pixel/Kayat/commit/449cdfe4bce8df3912cf818b0c2a965885cff637),
    [`76c1bfd`](https://github.com/nslookup255-pixel/Kayat/commit/76c1bfdee04b1bbdb63531b65eca9fd44fb7a547))
-   Fixed PyWebView test module mocking and added CI for testing and
    package builds.
    ([`be6e0fb`](https://github.com/nslookup255-pixel/Kayat/commit/be6e0fba5ad5ffad298606fc812056c9a2394798),
    [`1555f5c`](https://github.com/nslookup255-pixel/Kayat/commit/1555f5c19de25e1ba11f7021636f67e9745bdb66))
-   Added Python callable event handlers.
    ([`6dc0375`](https://github.com/nslookup255-pixel/Kayat/commit/6dc0375f4bf8911442fad4a6dbc55c4802a8c307))

### 2026-09-24 to 2026-09-28

-   Added alert, confirm, and prompt dialogs, with a usage example.
    ([`a5deebe`](https://github.com/nslookup255-pixel/Kayat/commit/a5deebe8c0c767b3ebc36351ab5a26b893afb52a),
    [`3000531`](https://github.com/nslookup255-pixel/Kayat/commit/3000531c6db2e481a928f0ab5a53bf7eeca85a1b))
-   Added a helper for converting Python values to display text and used
    it in the HTML renderer.
    ([`69facaf`](https://github.com/nslookup255-pixel/Kayat/commit/69facafbbaf7daea8b91b96d19048f16b4dc9f89))

### 2026-09-19 to 2026-09-20

-   Added application icon support and validation; resolved WebView
    optional-member warnings.
    ([`eeb25b9`](https://github.com/nslookup255-pixel/Kayat/commit/eeb25b9c592fb745801318f715319bd99f3194df),
    [`678fc88`](https://github.com/nslookup255-pixel/Kayat/commit/678fc88c80163828f11cf9e29b5e345d3cf37ace))
-   Updated project documentation with a roadmap and a revised README
    structure.
    ([`1a8f4f1`](https://github.com/nslookup255-pixel/Kayat/commit/1a8f4f157e923dca99530ac554343e86c2d84679),
    [`27cdcbc`](https://github.com/nslookup255-pixel/Kayat/commit/27cdcbcba6fa28496841258a431aaa51ff0fb0cd))

### 2026-09-16

-   Added the Python--JavaScript bridge.
    ([`64944f0`](https://github.com/nslookup255-pixel/Kayat/commit/64944f038201a4648c93903cc53fb275389c0291))

### 2026-09-12 to 2026-09-13

-   Implemented HTML rendering and connected the WebView runtime.
    ([`58745e1`](https://github.com/nslookup255-pixel/Kayat/commit/58745e18c222ce34a43d5ca1ae0af87c25e45915),
    [`b06360e`](https://github.com/nslookup255-pixel/Kayat/commit/b06360e77ce5ed57a6dce41c193c30f585eac830))
-   Implemented element and UI components, updated component progress
    documentation, and reorganized core/UI modules.
    ([`eafc06f`](https://github.com/nslookup255-pixel/Kayat/commit/eafc06f0b663654828a0d86cf28ee4fc79f71997),
    [`1705f87`](https://github.com/nslookup255-pixel/Kayat/commit/1705f87b75625dfc69e44bad9d301416429a3b9d),
    [`a697c97`](https://github.com/nslookup255-pixel/Kayat/commit/a697c97c08ff139643207e052edb191c231ebe1c))
-   Configured Dependabot.
    ([`9a75f0f`](https://github.com/nslookup255-pixel/Kayat/commit/9a75f0f749efb7d243449756e8d56b83d10cad94))
-   Fixed column layout and text rendering.
    ([`05a6d90`](https://github.com/nslookup255-pixel/Kayat/commit/05a6d90d1fbb4fe4593bd03f104bdbaa09bd3faf))

### 2026-09-11

-   Implemented the component system and added app mounting, updating
    the Hello example.
    ([`6e8bc23`](https://github.com/nslookup255-pixel/Kayat/commit/6e8bc23d44c0b7e7613f5c7e13fc79388264cd51),
    [`0d3c26f`](https://github.com/nslookup255-pixel/Kayat/commit/0d3c26f619cb8d14ea3cb78b5a87ea44cca698b4))

### 2026-09-10

-   Implemented state management.
    ([`2b6ac02`](https://github.com/nslookup255-pixel/Kayat/commit/2b6ac025226b050eb5d7ca7e39c1994f08241f0e))

### 2026-09-08

-   Implemented the event system and JavaScript bridge; updated the
    bridge implementation and registered bridge functions.
    ([`c06617e`](https://github.com/nslookup255-pixel/Kayat/commit/c06617e76aaae71151426405e9ee16fed6ff1553),
    [`7bd6540`](https://github.com/nslookup255-pixel/Kayat/commit/7bd654000b003ad9d07ab2137c1c4ec7f61c76b9),
    [`627db21`](https://github.com/nslookup255-pixel/Kayat/commit/627db2117a564e18c41459fc7553b64d4481a003),
    [`4bbde1f`](https://github.com/nslookup255-pixel/Kayat/commit/4bbde1fb8fc1c9223815bef5531dc7b58edaf419))
-   Cleaned up project structure and documentation.
    ([`4c5365d`](https://github.com/nslookup255-pixel/Kayat/commit/4c5365de81a06928c10e0ce6a06729ece763a57e))

### 2026-09-06

-   Established the initial project structure, basic `App` and Hello
    example, window abstraction, PyWebView backend, and app integration.
    ([`0ab3757`](https://github.com/nslookup255-pixel/Kayat/commit/0ab37576fe89e2f207b6043ea0016c9c1ed6fcff),
    [`b20b1c1`](https://github.com/nslookup255-pixel/Kayat/commit/b20b1c1c8c57f3aa9cdbd4324d803b0def9e0cb9),
    [`65422bd`](https://github.com/nslookup255-pixel/Kayat/commit/65422bd82a4305e0f0b39fac387243ad14ae1a68),
    [`1fd55c8`](https://github.com/nslookup255-pixel/Kayat/commit/1fd55c83920c1a6e869c076596861c23e3cb5d5e),
    [`1d7b5da`](https://github.com/nslookup255-pixel/Kayat/commit/1d7b5da624f9095bd8ea174b162555e5b4f29a2b))
-   Recorded the initial repository commits.
    ([`47c34f5`](https://github.com/nslookup255-pixel/Kayat/commit/47c34f514c5f2bc7c182fdd52d4451682c258bd7),
    [`fdcbab4`](https://github.com/nslookup255-pixel/Kayat/commit/fdcbab4de30b49368313d95d1cdf302d10efe025))

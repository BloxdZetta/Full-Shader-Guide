# Bloxd Shader Packs — The Engineering Guide

**A complete, data-backed guide to building shader packs for Bloxd.io (WebGPU renderer).**
Built from measured engine data, a full numeric block-id table, dissections of shipped
community packs, and a local validation toolchain — not from guesswork.

> Unofficial. Not affiliated with Bloxd.io. The API may change without notice.
> Portions assembled with AI assistance; verify against in-game behavior.
> Inspired by the multilingual format of
> [imu31465/Bloxd.io-How-To-Make-Shader-Packs](https://github.com/imu31465/Bloxd.io-How-To-Make-Shader-Packs) — with several layers of additional hard data.

## Why this guide is different

| Most guides | This guide |
|---|---|
| “skyLight is brightness 0–1” | skyLight is **tone-mapped**; real thresholds measured (0.45/0.98 ↔ 0.4/0.9 pre-curve) |
| “check the block name” | **Full numeric block-id table** (0 → 3254+) with live annex from a shipped pack |
| “use the hooks” | Hook contract incl. **surface→light private-var channel**, `bloxdFaceBlock`, `bloxdOpaqueBehind`, `skyLightColour`, `litColour` — all proven in a shipped pack |
| folklore fog | fog internals (band width, default colour, mode-0 black) with provenance labels |
| no tooling | a **local 8-variant naga validation** method that predicts in-game acceptance |

## The guide

| Part | File | Content |
|---|---|---|
| I | [01-making](en/01-making.md) | pack format, minimal pack, multi-file loading, caps, distribution |
| II | [02-api](en/02-api.md) | complete hook & struct contract, engine functions, hard rules |
| III | [03-recipes](en/03-recipes.md) | 12 production recipes with WGSL snippets |
| IV | [04-realism](en/04-realism.md) | measured numbers: light units, fog, water optics, tone curves |
| V | [05-troubleshooting](en/05-troubleshooting.md) | every failure mode we have hit or dissected |
| VI | [06-implementation](en/06-implementation.md) | local validation pipeline & packaging QA |
| VII | [07-internals](en/07-internals.md) | engine internals with provenance labels |
| VIII | [08-block-ids](en/08-block-ids.md) | the numeric block-id table (unique asset) |
| IX | [09-sources](en/09-sources.md) | how we know all this — instruments, provenance policy, open questions |
| X | [10-constants](en/10-constants.md) | every constant in this repo & the dissected packs — **423**, generated from source, each with its role |

## Languages

| Language | Status |
|---|---|
| English | ✅ full |
| Français | ✅ full ([fr/](fr/README.md)) |
| Deutsch · Español · Português · Italiano · Русский · 日本語 · 한국어 · 简体中文 | landing pages (deep content currently EN/FR — translations welcome) |

## License

MIT. Snippets are original; constants quoted from dissected packs are credited in place
(Ellie/whoisEllie, Crownix/Breeze, workshop authors).

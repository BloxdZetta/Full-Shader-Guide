# Bloxd Shader Packs — The Complete Guide

**Everything known about Bloxd.io shader packs, explained as simply as possible:**
how the web renderer draws the picture, how shaders work, what a pack can do,
what it cannot do, and how to build one — backed by measured engine data,
a full numeric block-id table, dissected community packs, and local validation
in all 8 engine variants.

> Unofficial. Not affiliated with Bloxd.io. The API may change without notice.

## 🚪 Start here (pick your door)

| You are… | Start with |
|---|---|
| **New to shaders** (or to code) | ⭐ [Part 0 — Start from zero](en/00-start.md) — how rendering works, what a shader is, your first pack in 5 steps |
| **A coder** who wants the contract | [Part II — The API contract](en/02-api.md), then [Part III — Recipes](en/03-recipes.md) |
| **Looking up one number** | [Part VIII — Block ids](en/08-block-ids.md) · [Part X — Constants](en/10-constants.md) · [Part IV — Measured numbers](en/04-realism.md) |
| **Debugging a broken pack** | [Part V — Troubleshooting](en/05-troubleshooting.md) |

## 📚 The guide (English, deep version)

| Part | File | Content |
|---|---|---|
| 0 | [00-start](en/00-start.md) | **start from zero**: web rendering, the GPU pipeline, what a shader is, everything possible/impossible, first pack |
| I | [01-making](en/01-making.md) | pack format, minimal pack, multi-file loading, caps, distribution |
| II | [02-api](en/02-api.md) | complete hook & struct contract, engine functions, hard rules |
| III | [03-recipes](en/03-recipes.md) | 12 production recipes with WGSL snippets |
| IV | [04-realism](en/04-realism.md) | measured numbers: light units, fog, water optics, tone curves |
| V | [05-troubleshooting](en/05-troubleshooting.md) | every known failure mode and its fix |
| VI | [06-implementation](en/06-implementation.md) | local validation pipeline (8 variants) & packaging QA |
| VII | [07-internals](en/07-internals.md) | engine internals: time, light pipeline, sky, loader |
| VIII | [08-block-ids](en/08-block-ids.md) | the full numeric block-id table (0 → 3254+) |
| IX | [09-sources](en/09-sources.md) | how every fact was established — instruments, provenance, open questions |
| X | [10-constants](en/10-constants.md) | every constant (551), generated from source, each with its role |

## 🌍 Languages

English and French carry the full 11-part deep guide. Every other language below is a
**complete single-page guide**: the full Part 0 (rendering, shaders, hooks, limits,
first pack, rules, glossary) translated in full, with links into the deep chapters.

| Language | Guide |
|---|---|
| English | ✅ full deep guide (this page) |
| Français | ✅ [guide complet, 11 parties](fr/README.md) |
| Deutsch | [Kompletter Leitfaden](de/README.md) |
| Español | [Guía completa](es/README.md) |
| Português | [Guia completo](pt/README.md) |
| Italiano | [Guida completa](it/README.md) |
| Nederlands | [Volledige gids](nl/README.md) |
| Polski | [Kompletny przewodnik](pl/README.md) |
| Türkçe | [Eksiksiz kılavuz](tr/README.md) |
| Русский | [Полное руководство](ru/README.md) |
| Українська | [Повний посібник](uk/README.md) |
| العربية | [الدليل الكامل](ar/README.md) |
| हिन्दी | [पूर्ण मार्गदर्शिका](hi/README.md) |
| Bahasa Indonesia | [Panduan lengkap](id/README.md) |
| Tiếng Việt | [Hướng dẫn đầy đủ](vi/README.md) |
| 日本語 | [完全ガイド](ja/README.md) |
| 한국어 | [완전 가이드](ko/README.md) |
| 简体中文 | [完整指南](zh-CN/README.md) |

## Why this guide is different

| Most guides | This guide |
|---|---|
| "skyLight is brightness 0–1" | skyLight is **tone-mapped**; real thresholds measured (0.45/0.98 ↔ 0.4/0.9 pre-curve) |
| "check the block name" | **full numeric block-id table** (0 → 3254+) with live annex from a shipped pack |
| "use the hooks" | full hook contract incl. the surface→light private-var channel, `bloxdFaceBlock`, `bloxdOpaqueBehind`, `skyLightColour`, `litColour` |
| folklore fog | fog internals (32-block band, default colour, mode-0 black) with provenance labels |
| no tooling | a **local 8-variant naga validation** method that predicts in-game acceptance |

Every fact carries a provenance label — measured, proven in a shipped pack, or restored
from engine code (Part IX). If something is unknown, the guide says so.

## License

MIT. Code snippets are original; constants quoted from community packs are credited in
place (Parts IX–X).

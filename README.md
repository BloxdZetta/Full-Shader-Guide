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
| **New to shaders** (or to code) | ⭐ [Part 0 — Start from zero](GUIDE-EN.md#part-0--start-from-zero-how-rendering-and-bloxd-shaders-work) — how rendering works, what a shader is, your first pack in 5 steps |
| **A coder** who wants the contract | [Part II — The API contract](GUIDE-EN.md#part-ii--the-api-contract), then [Part III — Recipes](GUIDE-EN.md#part-iii--recipes) |
| **Looking up one number** | [Part VIII — Block ids](GUIDE-EN.md#part-viii--the-numeric-block-id-table) · [Part X — Constants](GUIDE-EN.md#part-x--the-constants-register-en) · [Part IV — Measured numbers](GUIDE-EN.md#part-iv--measured-numbers-realism-that-survives-contact-with-the-game) |
| **Debugging a broken pack** | [Part V — Troubleshooting](GUIDE-EN.md#part-v--troubleshooting) |

## 📚 The guide (English, deep version)

| Part | File | Content |
|---|---|---|
| 0 | [00-start](GUIDE-EN.md#part-0--start-from-zero-how-rendering-and-bloxd-shaders-work) | **start from zero**: web rendering, the GPU pipeline, what a shader is, everything possible/impossible, first pack |
| I | [01-making](GUIDE-EN.md#part-i--making-a-pack) | pack format, minimal pack, multi-file loading, caps, distribution |
| II | [02-api](GUIDE-EN.md#part-ii--the-api-contract) | complete hook & struct contract, engine functions, hard rules |
| III | [03-recipes](GUIDE-EN.md#part-iii--recipes) | 12 production recipes with WGSL snippets |
| IV | [04-realism](GUIDE-EN.md#part-iv--measured-numbers-realism-that-survives-contact-with-the-game) | measured numbers: light units, fog, water optics, tone curves |
| V | [05-troubleshooting](GUIDE-EN.md#part-v--troubleshooting) | every known failure mode and its fix |
| VI | [06-implementation](GUIDE-EN.md#part-vi--implementation--local-validation) | local validation pipeline (8 variants) & packaging QA |
| VII | [07-internals](GUIDE-EN.md#part-vii--engine-internals) | engine internals: time, light pipeline, sky, loader |
| VIII | [08-block-ids](GUIDE-EN.md#part-viii--the-numeric-block-id-table) | the full numeric block-id table (0 → 3254+) |
| IX | [09-sources](GUIDE-EN.md#part-ix--where-this-knowledge-comes-from-and-what-we-dont-know) | how every fact was established — instruments, provenance, open questions |
| X | [10-constants](GUIDE-EN.md#part-x--the-constants-register-en) | every constant (551), generated from source, each with its role |

## 🌍 Languages

English and French carry the full 11-part deep guide. Every other language below is a
**complete single-page guide**: the full Part 0 (rendering, shaders, hooks, limits,
first pack, rules, glossary) translated in full, with links into the deep chapters.

| Language | Guide |
|---|---|
| English | ✅ full deep guide (this page) |
| Français | ✅ [guide complet, 11 parties](GUIDE-FR.md) |
| Deutsch | [Kompletter Leitfaden](GUIDE-DE.md) |
| Español | [Guía completa](GUIDE-ES.md) |
| Português | [Guia completo](GUIDE-PT.md) |
| Italiano | [Guida completa](GUIDE-IT.md) |
| Nederlands | [Volledige gids](GUIDE-NL.md) |
| Polski | [Kompletny przewodnik](GUIDE-PL.md) |
| Türkçe | [Eksiksiz kılavuz](GUIDE-TR.md) |
| Русский | [Полное руководство](GUIDE-RU.md) |
| Українська | [Повний посібник](GUIDE-UK.md) |
| العربية | [الدليل الكامل](GUIDE-AR.md) |
| हिन्दी | [पूर्ण मार्गदर्शिका](GUIDE-HI.md) |
| Bahasa Indonesia | [Panduan lengkap](GUIDE-ID.md) |
| Tiếng Việt | [Hướng dẫn đầy đủ](GUIDE-VI.md) |
| 日本語 | [完全ガイド](GUIDE-JA.md) |
| 한국어 | [완전 가이드](GUIDE-KO.md) |
| 简体中文 | [完整指南](GUIDE-ZH-CN.md) |

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

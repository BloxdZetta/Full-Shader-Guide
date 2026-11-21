# Bloxd Shader Packs — Guides and API Research

This repository contains a deep, **historical API v2** shader-pack manual and a new
[French API v5 field guide](GUIDE-API-V5-FR.md) based on public research checked on
**21 November 2026**. The v5 guide is the starting point for new packs; the older
manuals remain useful for understanding and migrating v2 projects, but their code,
macros, limits and validation matrix must not be assumed to describe the current API.

> Unofficial. Not affiliated with Bloxd.io. The API v5 update is a documented community
> research summary, not an independent extraction of the live client. Always validate a
> migrated pack in the current WebGPU renderer.

## 🚪 Start here (pick your door)

| You are… | Start with |
|---|---|
| **Building a new pack** | [API v5 field guide](GUIDE-API-V5-FR.md) — current contract summary, breaking changes and migration checklist |
| **New to shaders** (or to code) | ⭐ [Part 0 — Start from zero](GUIDE-EN.md#part-0--start-from-zero-how-rendering-and-bloxd-shaders-work) — concepts and renderer overview; use the v5 guide for current pack code |
| **Maintaining an API v2 pack** | [Part II — The API contract](GUIDE-EN.md#part-ii--the-api-contract), then [Part III — Recipes](GUIDE-EN.md#part-iii--recipes) — historical v2 reference |
| **Looking up one number** | [Part VIII — Block ids](GUIDE-EN.md#part-viii--the-numeric-block-id-table) · [Part X — Constants](GUIDE-EN.md#part-x--the-constants-register-en) · [Part IV — Measured numbers](GUIDE-EN.md#part-iv--measured-numbers-realism-that-survives-contact-with-the-game) |
| **Debugging a broken pack** | [Part V — Troubleshooting](GUIDE-EN.md#part-v--troubleshooting) |

## 📚 Deep reference (historical API v2)

The English and French manuals are a detailed snapshot for `apiVersion: 2`. Their old
validation matrix, IDs and exact importer/runtime claims are not a v5 specification.

| Part | File | Content |
|---|---|---|
| 0 | [00-start](GUIDE-EN.md#part-0--start-from-zero-how-rendering-and-bloxd-shaders-work) | rendering, GPU pipeline, shader basics, first pack |
| I | [01-making](GUIDE-EN.md#part-i--making-a-pack) | v2 pack format, importer, caps, distribution |
| II | [02-api](GUIDE-EN.md#part-ii--the-api-contract) | v2 six-hook contract, structs, defines and variants |
| III | [03-recipes](GUIDE-EN.md#part-iii--recipes) | WGSL recipes written for v2 |
| IV | [04-realism](GUIDE-EN.md#part-iv--measured-numbers-realism-that-survives-contact-with-the-game) | measurements recorded for the v2-era renderer |
| V | [05-troubleshooting](GUIDE-EN.md#part-v--troubleshooting) | v2-era troubleshooting |
| VI | [06-implementation](GUIDE-EN.md#part-vi--implementation--local-validation) | v2-era validation and packaging QA |
| VII | [07-internals](GUIDE-EN.md#part-vii--engine-internals) | v2-era engine notes |
| VIII | [08-block-ids](GUIDE-EN.md#part-viii--the-numeric-block-id-table) | historical numeric block-id table |
| IX | [09-sources](GUIDE-EN.md#part-ix--where-this-knowledge-comes-from-and-what-we-dont-know) | provenance labels, instruments, open questions |
| X | [10-constants](GUIDE-EN.md#part-x--the-constants-register-en) | constants harvested from the local v2-era pack corpus |

## 🌍 Languages

The English and French deep manuals and the translated single-page guides below are
**historical API v2** references. They are not current API v5 specifications. The new
[API v5 guide is currently available in French](GUIDE-API-V5-FR.md); please preserve its
source links, audit date and confidence notes when translating it.

| Language | Guide |
|---|---|
| Français | [Référence API v5](GUIDE-API-V5-FR.md) · [manuel détaillé v2](GUIDE-FR.md) |
| English | [Deep manual, historical API v2](GUIDE-EN.md) |
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

## What the v2 manual contains — and what it does not

The deep manual preserves a documented API v2 snapshot: its six-hook contract, block-ID
table, measured lighting figures, importer observations and local eight-variant checks.
Those details are useful for understanding v2 packs and the evolution of the renderer;
they are **not evidence that the current client still accepts v2**. For current v5 hooks,
model shading, flags, runtime lighting and migration changes, start with the [v5 research
note](GUIDE-API-V5-FR.md) and recheck its linked sources before publishing.

## License

MIT. Code snippets are original; constants quoted from community packs are credited in
place (Parts IX–X).

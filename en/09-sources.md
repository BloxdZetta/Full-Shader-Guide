# Part IX — Where this knowledge comes from (and what we don't know)

Every claim in this guide carries a provenance label. This page is the method behind the labels —
because a guide that tells you *how it knows* is worth ten that just assert.

## The three provenance classes

| Label | Meaning | Trust policy |
|---|---|---|
| **[measured]** | produced by local instruments: probe packs that write engine quantities into colour channels, screenshot pipelines with fixed camera/world setups, curve fitting on captured frames | trust within the measured envelope |
| **[shipped]** | proven by a released community pack running in the live game (e.g. Breeze v1, dissected file-by-file) | trust — the game itself accepted it |
| **[3rd-party]** | restored from production JS by community analysis (the imu31465 internals, npm type dumps, wiki) | never load-bearing until measured; cited because they guided our probes |

## The instruments

- **8-variant naga harness** — the engine’s prelude stubbed per variant (strict/allow × lit/unlit
  × terrain/liquid). Every local release compiles 8/8 before it ships; that record has predicted
  in-game acceptance across dozens of releases.
- **42-case WGSL fuzz** — malformed shapes fed through the compiler to map what breaks naga vs
  what breaks the browser Tint (two different compilers; the game uses the browser’s).
- **Probe packs** (never shipped) — skyLight→red, blockLight→green, fog→blue; read back with a
  colour picker in controlled worlds. This is where the tone-mapping thresholds and the shadow
  band (13.6–14.95/15) come from.
- **Curve fitting** — capture frames at known setups, regress log–log luminance pairs, get the
  actual response curve instead of a guessed gamma.
- **Reverse-oracle dissection** — compile a *shipped* pack through our harness: every failure is
  our harness being wrong, not the pack (that is how `bloxdFaceBlock`, `bloxdOpaqueBehind`,
  `skyLightColour`, `litColour` and multi-file loading were confirmed).
- **Cross-source triangulation** — a fact is only promoted when independent sources agree
  (community manual + wiki + client dumps + our probes). Disagreements are kept and labelled
  (see the fog ramp open question in Part IV).

## Honest open questions

1. **Fog ramp shape** — linear 32×D [3rd-party] vs EXP2 (older wiki note). Production-JS figure
   favoured; sonde measurement pending.
2. **Light hooks in unlit builds** — do they run at all? Not yet measured; write hooks that don’t care.
3. **Loader hygiene details** — exact error messages and recovery paths of the in-game loader
   (the client bundle exists in public archives; a dedicated read is planned).
4. **New-id names** — ids up to 3254 are *used* by a shipped pack; official names await a fresh
   `api.blockIdToBlockName` dump.

## Numbers behind this guide

Full numeric id table (0 → 3254+) · dozens of validated releases across two production packs ·
4 engine APIs first documented here from shipped-pack usage · 2 shipped packs dissected to the
constant · every constant quoted carries its author credit.

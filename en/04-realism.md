# Part IV — Measured numbers (realism that survives contact with the game)

Labels: **[measured]** from our screenshot/sonde pipelines · **[shipped]** proven in a released
pack · **[3rd-party]** restored from production JS by the community, sanity-check before relying.

## Light units

- Sky light propagates 0–15 (flood fill); **open sky = 15**. One level lost under a canopy is
  still ≈ **0.995 after tone-mapping** — a “lost level” is visible, darkness is not linear.
- skyLight arrives **tone-mapped** to packs. Worked thresholds: full sky ≈ ≥0.98; cave/night
  rejection below ≈ 0.45; a canopy’s one lost level ≈ 0.995 **[shipped]**.
- Packed light colours have a **35 % per-channel floor** relative to the brightest channel
  **[3rd-party]** — pure red lifts to (1.0, 0.35, 0). This is why lamps look washed-out pink.
- `l.ambient` = material.ambient × sceneAmbient; the scene side follows the user’s graphics
  setting (default 0.5). Never hardcode its default **[3rd-party]**.

## Sun, moon, sky

- Default worlds: sun direction static ≈ **(−0.56, 0.81, −0.18)** **[3rd-party]**; day/night
  worlds update it; **moon = −sun exactly**; night ⇔ `sun.y < 0`.
- Non-earth skyboxes (gloomy/interstellar/space): `bloxdSunDirection()` = **(0,0,0)** — gate
  every sun effect with a `sun.y`-based day factor and it self-disables **[shipped]**.
- Terrain directional light is two lamps with fixed direction/intensity — **terrain brightness
  does not follow the sun by itself**; time-of-day looks are 100 % your job.

## Fog

- Visibility is a **linear ramp**: `fogVisibility = (fogEnd − dist)/(fogEnd − fogStart)`,
  `fogStart = 32×D`, `fogEnd = 32×(D+1)` (D = player’s distance setting; D=0 ⇒ end 5) — the
  gradient band is only **32 blocks wide** **[3rd-party]**. Our older “EXP2” note came from a
  wiki; trust the production-JS figure, verify with a probe pack if your effect cares.
- Default fog colour `rgb(183, 191, 195)`; world owners can override it; **fog mode 0 (NONE)
  delivers fogColour as black** — hence always `mix(fogColour, col, fogVisibility)` via
  `bloxdApplyFog`, which is safe at visibility 1. Player “showFog off” pushes the band to
  3200–3328 **[3rd-party]**.
- **Open question, labelled honestly**: one community source says the ramp is linear
  (32×D→32×(D+1)); our older wiki note said EXP2. The linear figure comes from production-JS
  restoration and is more credible — but the definitive sonde measurement is pending. Neither
  affects thresholds that test `fogVisibility` directly.
- Fine checker patterns at chunk borders during loading = the engine’s Bayer 4×4 chunk fade,
  **not your bug**.

## Water optics (shipped-pack proven values)

- Beer–Lambert depth darkening `1 − exp(−0.32·d)` (≈⅓ at 1 block) **[shipped]**; the local P0
  plan used 0.45/0.08/0.03 (r/g/b) — both work, the single-scalar is friendlier.
- Schlick Fresnel with F0 = 0.02; broad sheen `0.05·pow(nDotH, 24)·sunUp` **[shipped]**.
- Registered water colour (0.5, 0.5, 0.8) / alpha 0.9 — rebuild alpha from it, don’t hardcode.

## Grading

- Lift curve `c·B/(1+c·(B−1))`: slope **B at black, exactly 1.0 at white** — white never clips.
  Breeze ships B = 1.45 **[shipped]**; our cinematic pack tuned B per-channel after fitting a
  tone curve to real frames.
- Vibrance with a chroma guard (`1 − chroma`) saturates dull pixels without oversaturating
  already-colourful ones.

## Why measure at all

Every shipped pack we dissected tunes by eye. Fitting your curve to actual captured frames
(linear regression on log–log luminance pairs) takes an afternoon and is the difference between
“vibes” and reproducible looks. See Part VI.

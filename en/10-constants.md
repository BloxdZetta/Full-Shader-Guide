# Part X — The constants register (EN)

## Engine-exposed variables (what the game gives you)

| Variable | Type / value | Meaning |
|---|---|---|
| `surface.colour` | vec3f | incoming material colour (pre-shading) |
| `surface.alpha` | f32 | incoming alpha; drives cutout discard & liquid blend |
| `surface.position` | vec3f | world position of the fragment |
| `surface.normal` | vec3f | face normal |
| `surface.blockId` | u32 | numeric block id (Part VIII) |
| `out.emission` | vec3f | self-glow, surface hook only |
| `light.skyLight` | f32 0..1 | sky light, **tone-mapped** (open sky ≈1, one lost canopy level ≈0.995) |
| `light.blockLight` | vec3f | block light colour (35% channel floor) |
| `light.heldLight` | vec3f | handheld light (≤15 blocks, dist^0.75) |
| `light.skyLightColour` | vec3f | sky tint; darkens at night |
| `light.litColour` | vec3f | surface's own lit colour |
| `light.fogVisibility` | f32 | engine fog factor (linear band 32×D per 3rd-party) |
| `light.fogColour` | vec3f | fog colour; **black when fog mode is NONE** |
| `light.blockId` | u32 | numeric block id in the light hook |
| `bloxdTimeWrap` | f32 = **3600** | the wrap period of `bloxdTime()` (seconds) |
| `bloxdOriginOffset()` | vec3i | floating-origin rebase; inject into world hashes |
| `bloxdSunDirection()` | vec3f | unit sun vector; zero on sunless skies; moon = −this |
| `bloxdFaceBlock(p,n)` | vec3i | cell (block coordinates) of the current face — per-block hash input; the id itself is `surface.blockId` / `light.blockId` |
| `bloxdOpaqueBehind()` | {found,position} | first opaque block behind a liquid fragment |
| `bloxdEyePosition()` | vec3f | camera position |
| `bloxdApplyFog(c,l)` | vec3f | mix(fogColour, c, fogVisibility) |

## Engine-internal figures every pack author needs

| Figure | Value | Provenance |
|---|---|---|
| time wrap | 3600 s | [3rd-party + shipped usage] |
| light scale | 0–15, open sky = 15 | [3rd-party + measured] |
| tone curve family | ≈ 45·b/(1+2b) (saturating) | [measured] |
| terrain shadow band | skyLight 13.6–14.95 / 15 | [measured] |
| packed-light channel floor | 35 % of max channel | [3rd-party] |
| fog band | start 32×D, end 32×(D+1) (linear per 3rd-party; EXP2 legacy note — open question) | [3rd-party] |
| default fog colour | rgb(183, 191, 195) | [3rd-party] |
| showFog off | band pushed to 3200–3328 | [3rd-party] |
| scene ambient default | 0.5 (user setting) | [3rd-party] |
| loader cap | 256 KB total .wgsl | [3rd-party] |
| scene directional lamps | 2, fixed direction/intensity | [3rd-party] |



## cinematic-v5 (local pack — frozen baseline) — 183 constants

| Constant | Value | Role |
|---|---|---|
| `TR_ALT_HAZE` | 0.15 | altitude haze: veil strength above 55 blocks |
| `TR_AURORA_WATER` | 0.08 | water: night aurora reflection strength (in our reflection only) |
| `TR_BACKLIGHT` | 0.18 | backlight: strength of vegetation against-sun glow |
| `TR_BACKLIGHT_COL` | vec3f(1.0, 0.62, 0.28) | backlight: warm glow colour |
| `TR_BAT_CHANCE` | 0.12 | bats: share of air cells at dusk |
| `TR_BAT_COL` | vec3f(0.10, 0.09, 0.08) | bats: dark silhouette colour |
| `TR_BAT_ROAM` | 0.8 | bats: erratic roaming radius |
| `TR_BAT_SIZE` | 0.09 | bats: body size |
| `TR_BAT_T_WING` | 9.424778 | bats: fast wing-beat speed (wrap-locked) |
| `TR_BFLY_BODY` | 0.012 | butterflies: body sliver half-width |
| `TR_BFLY_CHANCE` | 0.25 | butterflies: share of air cells holding one |
| `TR_BFLY_COL1` | vec3f(0.95, 0.93, 0.85) | butterflies: white variant |
| `TR_BFLY_COL2` | vec3f(0.98, 0.85, 0.30) | butterflies: yellow variant |
| `TR_BFLY_COL3` | vec3f(0.90, 0.55, 0.25) | butterflies: orange variant |
| `TR_BFLY_GAP` | 0.035 | butterflies: half-separation of the two wings |
| `TR_BFLY_ROAM` | 0.4 | butterflies: roaming radius around the cell |
| `TR_BFLY_SIZE` | 0.05 | butterflies: body size |
| `TR_BFLY_TALL` | 1.35 | butterflies: wing-disc height ratio |
| `TR_BFLY_T_WING` | 3.1415927 | butterflies: wing-beat angular speed (wrap-locked) |
| `TR_BUG_COL` | vec3f(0.72, 0.06, 0.05) | ladybugs: shell red |
| `TR_BUG_SHARE` | 0.12 | butterflies: share that are ladybugs instead |
| `TR_CANOPY_HI` | 0.9995 | tree-effect window: skyLight of open sky (fields stay bare) |
| `TR_CANOPY_LO` | 0.90 | tree-effect window: minimum skyLight (caves stay bare) |
| `TR_CINEMA_BOOST` | 1.6 | cinema mode: multiplier on golden mist and backlight |
| `TR_CINEMA_MODE` | false | cinema mode: false = normal, true = boosted atmosphere |
| `TR_EDGE_AO` | 0.92 | edge AO strength (skyLight-weighted by law) |
| `TR_EMBER_CHANCE` | 0.18 | lava: share of cells emitting rising embers |
| `TR_EMBER_HEIGHT` | 2.2 | lava: ember rise height (blocks) |
| `TR_EMBER_SIZE` | 0.03 | lava: ember angular size at 1 block |
| `TR_EMBER_T_RISE` | 4.0 | lava: ember rise period (must divide 3600) |
| `TR_EPSILON` | 0.0001 | generic epsilon guard |
| `TR_FLY_CHANCE` | 0.18 | fireflies: share of air cells holding one |
| `TR_FLY_COLOUR` | vec3f(1.0, 0.85, 0.45) | fireflies: glow colour |
| `TR_FLY_SIZE` | 0.035 | fireflies: glow dot radius |
| `TR_FLY_W_BLINK` | 0.0698132 | fireflies: blink angular speed (wrap-locked) |
| `TR_FLY_W_BOB` | 0.7853981 | fireflies: hover bobbing angular speed (wrap-locked) |
| `TR_GLASS_MIRROR` | 0.30 | glass: sky reflection strength (fresnel) |
| `TR_GLASS_RIM` | 0.22 | glass: grazing-angle edge brightening |
| `TR_GOLDEN_GAIN` | 0.50 | golden-hour gain |
| `TR_GOLDEN_TINT` | vec3f(1.06, 1.005, 0.90) | golden-hour tint |
| `TR_GRAIN` | 0.0 | film grain amount (distance-faded) |
| `TR_HZN_CLOUD_STR` | 0.45 | horizon cloud bank strength |
| `TR_LAMP_FLICKER` | 0.10 | lamp flicker: spill modulation depth (0 = off) |
| `TR_LAMP_SOFT_AO` | 0.55 | lamp softening: edge-AO kept near lamps |
| `TR_LAMP_SOFT_GAIN` | 2.5 | lamp softening: blockLight to wash-factor gain |
| `TR_LAMP_SOFT_GRAIN` | 0.5 | lamp softening: grain kept near lamps |
| `TR_LAVA_FLOW_SCALE` | 0.55 | lava: viscous flow texture scale (much slower than water) |
| `TR_LEAF_AUTUMN` | 0.12 | falling leaves: share of autumn-tinted leaves |
| `TR_LEAF_AUTUMN_GOLD` | vec3f(0.87, 0.60, 0.16) | falling leaves: autumn golden tint |
| `TR_LEAF_AUTUMN_RUST` | vec3f(0.62, 0.28, 0.09) | falling leaves: autumn rust tint |
| `TR_LEAF_BACKLIT` | 0.35 | falling leaves: backlit glow when sun is behind |
| `TR_LEAF_CELL` | 3.0 | falling leaves: air-cell size (one leaf max per cell) |
| `TR_LEAF_CHANCE` | 0.3 | falling leaves: share of cells holding a leaf |
| `TR_LEAF_DRIFT` | 0.06 | falling leaves: downwind drift (cloud direction) |
| `TR_LEAF_FADE_LO` | 5.0 | falling leaves: distance where fading starts |
| `TR_LEAF_FALL` | 0.6 | falling leaves: fall speed (must equal WRAP*CELL/3600 exactly) |
| `TR_LEAF_FLUTTER` | 0.15 | falling leaves: vertical flutter amplitude |
| `TR_LEAF_GUST` | 0.5 | falling leaves: sway boost during gusts |
| `TR_LEAF_LEN` | 1.7 | falling leaves: leaf length/width aspect |
| `TR_LEAF_LOD_SHRINK` | 0.45 | falling leaves: distant shrink share |
| `TR_LEAF_ON` | true | feature toggle: falling leaves |
| `TR_LEAF_RANGE` | 10.0 | falling leaves: draw distance from the eye |
| `TR_LEAF_RIM` | 0.22 | falling leaves: centre rim-light strength |
| `TR_LEAF_SIZE` | 0.09 | falling leaves: leaf half-width |
| `TR_LEAF_SIZE_VAR` | 0.30 | falling leaves: per-leaf size variation (+/-) |
| `TR_LEAF_STEPS` | 6 | falling leaves: ray-march samples along the view line |
| `TR_LEAF_TIP` | 0.55 | falling leaves: pointed-tip taper strength |
| `TR_LEAF_TWOTONE` | 0.18 | falling leaves: per-leaf two-tone variation |
| `TR_LEAF_WRAP` | 720 | falling leaves: y-cell wrap for a seamless 3600 s loop |
| `TR_LEAF_W_FLIP` | 2.199115 | falling leaves: flip angular speed (wrap-locked) |
| `TR_LEAF_W_GUST` | 0.1047197 | falling leaves: gust cycle angular speed (wrap-locked) |
| `TR_LEAF_W_SPIN` | 1.600467 | falling leaves: spin angular speed (wrap-locked) |
| `TR_LEAF_W_SWAY_A` | 1.300270 | falling leaves: sway angular speed x (wrap-locked) |
| `TR_LEAF_W_SWAY_B` | 0.900590 | falling leaves: sway angular speed z (wrap-locked) |
| `TR_LITTER_DENS` | 0.82 | leaf litter: share of cells left bare |
| `TR_LITTER_MIX` | 0.22 | leaf litter: ground blend strength under canopy |
| `TR_LITTER_SCALE` | 3.0 | leaf litter: speckle cells per block |
| `TR_MIST_GOLDEN` | 0.10 | aerial perspective / mist |
| `TR_MIST_GOLDEN_COL` | vec3f(0.93, 0.96, 1.0) | aerial perspective / mist |
| `TR_MIST_GROUND` | 0.12 | ground mist: strength at golden hour |
| `TR_MIST_GROUND_BAND` | 3.5 | ground mist: height band around the eye (blocks) |
| `TR_MIST_GROUND_COL` | vec3f(0.93, 0.96, 1.0) | ground mist: veil colour |
| `TR_MIST_GROUND_HI` | 90.0 | ground mist: distance fade end (blocks) |
| `TR_MIST_GROUND_LO` | 16.0 | ground mist: distance fade start (blocks) |
| `TR_MOONLIGHT` | vec3f(0.30, 0.38, 0.55) | moonlight tint |
| `TR_MOON_COLUMN` | 0.10 | water: moonlight column strength on the river |
| `TR_MOON_GAIN` | 0.30 | moonlight gain |
| `TR_MOTE_CHANCE` | 0.2 | air motes: share of cells holding one (cave spores / day pollen) |
| `TR_MOTE_COL` | vec3f(0.55, 0.75, 1.0) | air motes: cave spore colour |
| `TR_MOTE_SIZE` | 0.035 | air motes: angular size at 1 block |
| `TR_POLLEN_COL` | vec3f(1.0, 0.85, 0.45) | air motes: golden pollen colour |
| `TR_RELIEF_EPS` | 0.30 | relief-mapping step epsilon |
| `TR_RELIEF_GAIN` | 1.6 | relief lighting gain |
| `TR_RELIEF_HEIGHT` | 0.16 | relief heightfield amplitude |
| `TR_RELIEF_SCALE` | 1.7 | relief-mapping height scale |
| `TR_SCOTO` | 0.5 | scotopic (rod-vision) mixing strength |
| `TR_SKY2_BAND_A` | -0.22 | sun elevation: full night below this |
| `TR_SKY2_BAND_B` | -0.04 | sun elevation: twilight begins here |
| `TR_SKY2_BAND_C` | 0.10 | sun elevation: day begins here |
| `TR_SKY2_BAND_D` | 0.30 | sun elevation: full day above this |
| `TR_SKY2_GLOW_DAWN` | vec3f(1.0, 0.70, 0.38) | dawn sun-glow colour |
| `TR_SKY2_GLOW_DUSK` | vec3f(1.0, 0.50, 0.26) | dusk sun-glow colour |
| `TR_SKY2_GLOW_NIGHT` | vec3f(0.50, 0.62, 0.92) | moon-glow colour |
| `TR_SKY2_NIGHT_LOW` | vec3f(0.07, 0.10, 0.20) | night sky horizon colour (deep blue) |
| `TR_SKY2_NIGHT_TOP` | vec3f(0.01, 0.02, 0.06) | night sky zenith colour |
| `TR_SKY2_TWI_LOW` | vec3f(0.98, 0.62, 0.42) | twilight sky horizon colour (peach-gold) |
| `TR_SKY2_TWI_TOP` | vec3f(0.34, 0.34, 0.62) | twilight sky zenith colour (mauve) |
| `TR_SKYF_CURVE` | 1.6 | sky-fog: elevation-curve steepness (Blocky Day proven) |
| `TR_SKYF_FOG_MIX` | 0.9 | sky-fog: share of the engine fog colour replaced by the sky gradient |
| `TR_SKYF_GLOW` | 0.55 | sky-fog: sun-glow strength (Blocky Day HORIZON_GLOW) |
| `TR_SKYF_GLOW_COL` | vec3f(1.00, 0.78, 0.50) | sky-fog: sun-glow colour inside the fake sky |
| `TR_SKYF_HAZE_DESAT` | 0.10 | aerial-haze grey desaturation (lower = bluer sky feel) |
| `TR_SKYF_HORIZON_MIX` | 0.85 | sky-fog: horizon haze blend into the fake sky |
| `TR_SKYF_LOW` | vec3f(0.70, 0.80, 0.96) | sky-fog: fake-sky horizon colour (Blocky Day proven) |
| `TR_SKYF_TOP` | vec3f(0.25, 0.45, 0.85) | sky-fog: fake-sky zenith colour (Blocky Day proven) |
| `TR_SOFTEN_AMOUNT` | 0.0 | face-speckle smoothing strength (anti-seam) |
| `TR_SOFTEN_GRAIN_NEAR` | 14.0 | distance where the fine grain layer stops |
| `TR_SOFTEN_LEVEL` | 0.5 | brightness smoothed faces settle towards |
| `TR_SOFTEN_MIST` | 0.0 | soft cloud-blotch strength on faces |
| `TR_SOFTEN_MIST_FAR` | 48.0 | distance where blotches fade out |
| `TR_SOFTEN_MIST_SIZE` | 5.0 | blotch frequency per block |
| `TR_SPLASH_BRIGHT` | 1.6 | lava: droplet brightness |
| `TR_SPLASH_CHANCE` | 0.35 | lava: share of cells with an active splash source |
| `TR_SPLASH_COL` | vec3f(1.0, 0.55, 0.15) | lava: droplet colour |
| `TR_SPLASH_HEIGHT` | 0.45 | lava: droplet apex height |
| `TR_SPLASH_SIZE` | 0.045 | lava: droplet angular size at 1 block |
| `TR_SPLASH_TRAIL` | 0.05 | lava: trail spacing behind the drop (fraction of cycle) |
| `TR_SPLASH_T_RISE` | 3.0 | lava: rise-and-fall period (must divide 3600) |
| `TR_SWAY_FLOWER_HI` | 163u | flower id range end (sway gate) |
| `TR_SWAY_FLOWER_LO` | 151u | flower id range start (sway gate) |
| `TR_SWAY_VINE_W` | 0.5 | vine sway weight (id 219) |
| `TR_VIBRANCE` | 0.16 | pre-fog grade (lift + chroma-guarded vibrance) |
| `TR_WATER_CLARITY` | 0.82 | water clarity (view-through) |
| `TR_WATER_DAY_TINT` | vec3f(0.34, 0.78, 0.82) | water tint, day band |
| `TR_WATER_DUSK_TINT` | vec3f(0.20, 0.48, 0.66) | water tint, dusk band |
| `TR_WATER_GLINT` | 0.82 | sun glint strength |
| `TR_WATER_MIRROR_CAP` | 1.05 | water optics |
| `TR_WATER_MIRROR_CHROMA` | 0.80 | water optics |
| `TR_WATER_MIRROR_PRESS` | 1.60 | water optics |
| `TR_WATER_MOON_GLINT` | vec3f(0.48, 0.66, 0.88) | water optics |
| `TR_WATER_NIGHT_TINT` | vec3f(0.075, 0.19, 0.34) | water tint, night band |
| `TR_WATER_REFLECTIVITY` | 0.78 | water reflectivity |
| `TR_WATER_RIPPLE` | 0.105 | ripple amplitude |
| `TR_WATER_TINT` | 0.48 | water tint mix strength |
| `TR_WAVE_OMEGA_A` | 0.502655 | wave band A angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_B` | 0.726057 | wave band B angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_C` | 0.949459 | wave band C angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_D` | 1.605703 | wave band D angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_E` | 1.982694 | wave band E angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_F` | 2.415536 | wave band F angular frequency (frozen R17) |
| `TR_WAVE_SWELL_AMP` | 0.15 | water: long swell normal amplitude |
| `TR_WAVE_SWELL_FOAM` | 0.20 | water: foam strength on swell crests |
| `TR_WAVE_SWELL_SCALE` | 0.10 | water: swell spatial frequency (radians per block) |
| `bloom_spill` | 0.5 | bloom bleed amount |
| `cloud_height` | 100.0 | cv5 cloud layer altitude |
| `cloud_scale` | 0.006 | cv5 cloud noise scale |
| `cloud_speed` | vec2f(1.2, 0.7) | cv5 cloud drift speed (x,y) |
| `cloud_strength` | 0.3 | cv5 2D cloud layer strength |
| `grade_contrast` | 0.16 | final contrast offset |
| `grade_saturation` | 1.2 | final saturation multiplier |
| `grass_id` | 150u | the decorative grass PLANT block id (per-block sway gate) |
| `haze_base_height` | 40.0 | fog reference altitude |
| `haze_density` | 0.006 | height-fog density |
| `haze_height_falloff` | 0.012 | fog altitude falloff |
| `haze_strength` | 0.48 | height-fog strength |
| `hot_glow_strength` | 0.2 | lava/hot-emitter glow |
| `leaf_glow` | 0.6 | leaf translucency glow |
| `luma` | vec3f(0.299, 0.587, 0.114) | Rec.709 luminance weights |
| `ray_sky_max` | 0.90 | god-ray sky exposure gate high |
| `ray_sky_min` | 0.60 | god-ray sky exposure gate low |
| `ray_strength` | 0.3 | god-ray strength |
| `shadow_ambient_drop` | 0.55 | ambient loss inside shadow |
| `shadow_softness` | 0.04 | shadow edge softness |
| `shadow_strength` | 0.85 | directional shadow strength |
| `shadow_threshold` | 0.95 | skyLight threshold where shadows start |
| `shadow_tint` | vec3f(0.62, 0.74, 1.0) | shadow cool tint |
| `sun_fallback` | vec3f(0.42, 0.85, 0.0) | sun tint when skyLightColour is unavailable |
| `sway_amount` | 0.3 | sway amplitude factor |
| `sway_mode` | 2 | sway implementation selector; 2 = colour-only (runs everywhere) |
| `sway_speed` | 1.0 | sway time multiplier |
| `tall_grass_id` | 1109u | Tall Grass plant id (same gate) |
| `tall_grass_top_id` | 1110u | Tall Grass top-half block id (sway gate) |
| `underwater_strength` | 0.30 | underwater colour grade strength |

## titan-bsl-ultra-v2 (local pack — sky/cloud/water showcase) — 288 constants

| Constant | Value | Role |
|---|---|---|
| `TR_AERIAL_DESAT` | 0.55 | aerial perspective / mist |
| `TR_AERIAL_SCALE` | 46.0 | aerial perspective / mist |
| `TR_AERIAL_SLANT` | 1.35 | aerial perspective / mist |
| `TR_AERIAL_STRENGTH` | 0.22 | aerial perspective / mist |
| `TR_AIR_SCATTER` | 0.055 | aerial perspective / mist |
| `TR_AMBIENT_HUE_AMOUNT` | 0.45 | bounce/ambient hue shaping |
| `TR_AO_EDGE_MIN` | 0.10 | ambient-occlusion system (skyLight-weighted) |
| `TR_AO_EDGE_SOFT` | 2.60 | ambient-occlusion system (skyLight-weighted) |
| `TR_AO_LEVEL_HIGH` | 14.60 | ambient-occlusion system (skyLight-weighted) |
| `TR_AO_LEVEL_LOW` | 3.00 | ambient-occlusion system (skyLight-weighted) |
| `TR_AO_SHADE_FLOOR` | 0.34 | ambient-occlusion system (skyLight-weighted) |
| `TR_AURORA_A` | vec3f(0.22, 0.95, 0.55) | night-sky features (stars/milky way/aurora/meteors) |
| `TR_AURORA_B` | vec3f(0.85, 0.30, 0.95) | night-sky features (stars/milky way/aurora/meteors) |
| `TR_AURORA_GAIN` | 0.34 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_AURORA_HIGH` | 0.62 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_AURORA_LOW` | 0.06 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_BACKLIGHT` | 0.30 | backlight: strength of vegetation against-sun glow |
| `TR_BLOCK_AMBIENT` | 0.55 | block-light ambient & roughness response |
| `TR_BLOCK_ROUGH_SPREAD` | 0.06 | block-light ambient & roughness response |
| `TR_BLOCK_VARIATION` | 0.018 | per-block / per-cell brightness variation |
| `TR_BOUNCE_AMBIENT_HUE` | vec3f(1.05, 0.99, 0.925) | bounce/ambient hue shaping |
| `TR_BUMP_STRENGTH` | 0.85 | micro-detail & terrain normal work |
| `TR_CANOPY_DAPPLE` | 0.55 | tree-canopy shadow (lost skyLight level) |
| `TR_CANOPY_OPEN_HI` | 0.85 | tree-canopy shadow (lost skyLight level) |
| `TR_CANOPY_OPEN_LO` | 0.35 | tree-canopy shadow (lost skyLight level) |
| `TR_CANOPY_SCALE` | 0.36 | tree-canopy shadow (lost skyLight level) |
| `TR_CANOPY_SWIRL` | 0.351111 | tree-canopy shadow (lost skyLight level) |
| `TR_CAUSTIC_COLOUR` | vec3f(0.62, 0.94, 0.86) | water caustics on flooded ground |
| `TR_CAUSTIC_DISP_B` | 0.80 | water caustics on flooded ground |
| `TR_CAUSTIC_DISP_R` | 1.25 | water caustics on flooded ground |
| `TR_CAUSTIC_FALLOFF` | 0.22 | water caustics on flooded ground |
| `TR_CAUSTIC_FAST` | 0.30 | water caustics on flooded ground |
| `TR_CAUSTIC_SCALE` | 0.22 | water caustics on flooded ground |
| `TR_CAUSTIC_SPIN` | 0.508889 | water caustics on flooded ground |
| `TR_CIRRUS_DENSITY` | 0.62 | cirrus layer |
| `TR_CIRRUS_GAIN` | 0.30 | cirrus layer |
| `TR_CIRRUS_HEIGHT` | 420.0 | cirrus layer |
| `TR_CIRRUS_SCALE` | 0.0022 | cirrus layer |
| `TR_CLOUD_AMBIENT_DIM` | 0.22 | ambient dimming under cloud shadow |
| `TR_CLOUD_BOTTOM_COLOUR` | vec3f(0.40, 0.45, 0.58) | volumetric clouds (marching & lighting) |
| `TR_CLOUD_COVERAGE` | 0.46 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_FILL` | vec3f(0.26, 0.33, 0.46) | volumetric clouds (marching & lighting) |
| `TR_CLOUD_HEIGHT` | 190.0 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_MIN_SUN` | 0.06 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_OPACITY` | 0.88 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_POWDER` | 1.60 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_POWDER_GAIN` | 0.35 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_RAY_MAX` | 6000.0 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SCALE` | 0.0086 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SELF_SHADOW` | 0.70 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SHADOW_DRIFT` | 0.022222 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SHADOW_GAPS` | 0.85 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SHADOW_SCALE` | 0.026 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SHADOW_STEP` | 34.0 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SHADOW_STRENGTH` | 0.62 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SILVER` | 0.45 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SOFTNESS` | 0.16 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_SPEED` | 0.55 | volumetric clouds (marching & lighting) |
| `TR_CLOUD_TOP_COLOUR` | vec3f(1.00, 0.99, 0.96) | volumetric clouds (marching & lighting) |
| `TR_CLOUD_WIND` | vec2f(0.82, 0.57) | volumetric clouds (marching & lighting) |
| `TR_CLUMP_SCALE` | 0.034 | foliage clumping |
| `TR_CLUMP_STRENGTH` | 1.00 | foliage clumping |
| `TR_CLUMP_TINT` | 0.55 | foliage clumping |
| `TR_DEBUG_MODE` | 0 | debug visualisation selector (0 = off) |
| `TR_DETAIL_FAR` | 0.45 | dither & LOD detail fades |
| `TR_DETAIL_NEAR` | 0.06 | dither & LOD detail fades |
| `TR_DITHER` | 0.0035 | dither & LOD detail fades |
| `TR_DIVE_MIRROR` | vec3f(0.020, 0.110, 0.150) | underwater mirror pass strength |
| `TR_EDGE_CREASE` | 0.26 | micro-detail & terrain normal work |
| `TR_EDGE_WIDTH` | 0.18 | micro-detail & terrain normal work |
| `TR_EMISSION_AMBER_HI` | 0.50 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_AMBER_LO` | 0.30 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_BRIGHT` | 0.88 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_DARK_LO` | 0.38 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_DIM` | 0.58 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_FIERY_HI` | 0.85 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_FIERY_LO` | 0.65 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_GOLD_HI` | 2.20 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_GOLD_LO` | 1.40 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_SAT_HI` | 0.80 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_SAT_LO` | 0.30 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_SELF_LIGHT` | 0.45 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_STRENGTH` | 1.25 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_UNCONFIRMED` | 0.15 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_WARM_HI` | 1.62 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EMISSION_WARM_LO` | 1.16 | emissive-block system (torch/lamp/gold/amber/fiery gates) |
| `TR_EPSILON` | 0.000001 | generic epsilon guard |
| `TR_EXPOSURE` | 0.96 | tone mapping & grade |
| `TR_F0_DIELECTRIC` | 0.04 | PBR material set (GGX F0/roughness/sheen) |
| `TR_FACE_CONTRAST` | 0.30 | per-face variation phases |
| `TR_FACE_PHASE_A` | 0.6180339887 | per-face variation phases |
| `TR_FACE_PHASE_B` | 0.7548776662 | per-face variation phases |
| `TR_FIRE_FLICKER` | 0.16 | fire flicker animation |
| `TR_FIRE_PHASE` | 41.0 | fire flicker animation |
| `TR_FOLIAGE_NORMAL_HIGH` | 0.85 | animated foliage normals |
| `TR_FOLIAGE_NORMAL_LOW` | 0.25 | animated foliage normals |
| `TR_GLARE_DESAT` | 0.70 | bloom glare shaping |
| `TR_GLARE_FULL` | 1.05 | bloom glare shaping |
| `TR_GLARE_KNEE` | 0.55 | bloom glare shaping |
| `TR_GRADE_CONTRAST` | 0.45 | tone mapping & grade |
| `TR_GRADE_FILMIC` | 0.45 | tone mapping & grade |
| `TR_GRADE_HIGHLIGHT_DESAT` | 0.25 | tone mapping & grade |
| `TR_GRADE_NIGHT` | vec3f(0.60, 0.80, 1.14) | tone mapping & grade |
| `TR_GRADE_NIGHT_MIX` | 0.45 | tone mapping & grade |
| `TR_GRADE_SATURATION` | 1.10 | tone mapping & grade |
| `TR_GRADE_SHADOW_RANGE` | 0.38 | tone mapping & grade |
| `TR_GRADE_SHADOW_TINT` | vec3f(0.93, 0.975, 1.08) | tone mapping & grade |
| `TR_GRADE_VIBRANCE` | 0.38 | pre-fog grade (lift + chroma-guarded vibrance) |
| `TR_GRASS_GLINT_F0` | 0.045 | specular glint on grass |
| `TR_GRASS_GLINT_GAIN` | 0.55 | specular glint on grass |
| `TR_GRASS_GLINT_ROUGH` | 0.40 | specular glint on grass |
| `TR_GUST_BREATHE` | 0.675556 | wind gust field |
| `TR_GUST_SCALE` | 0.020 | wind gust field |
| `TR_GUST_SHADE` | 0.26 | wind gust field |
| `TR_GUST_SPEED` | 1.500000 | wind gust field |
| `TR_LAMP_WOBBLE` | 0.05 | lamp light wobble |
| `TR_LEAF_NORMAL_FLUTTER` | 1.240000 | animated foliage normals |
| `TR_LEAF_NORMAL_RATE` | 0.42 | animated foliage normals |
| `TR_LEAF_NORMAL_STRENGTH` | 0.60 | animated foliage normals |
| `TR_LEAF_NORMAL_TIME` | 0.413333 | animated foliage normals |
| `TR_LOCAL_KEEP` | 0.85 | lighting framework (keep/unlit/night/shelter) |
| `TR_LOOP_CELLS` | 8.0 | wrap-lock (time/precision loops) |
| `TR_LOOP_SECONDS` | 3600.0 | wrap-lock (time/precision loops) |
| `TR_MAGMA_CORE` | vec3f(1.000, 0.800, 0.300) | magma/lava material & LOD |
| `TR_MAGMA_CRUST` | vec3f(0.030, 0.006, 0.001) | magma/lava material & LOD |
| `TR_MAGMA_GAIN` | 1.30 | magma/lava material & LOD |
| `TR_MAGMA_HOT` | vec3f(1.000, 0.250, 0.030) | magma/lava material & LOD |
| `TR_MAGMA_LOD_FAR` | 80.0 | magma/lava material & LOD |
| `TR_MAGMA_LOD_NEAR` | 12.0 | magma/lava material & LOD |
| `TR_MAGMA_SCALE` | 0.30 | magma/lava material & LOD |
| `TR_MAGMA_WARP` | 4.00 | magma/lava material & LOD |
| `TR_MAT_GRASS_F0` | 0.042 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_GRASS_ROUGH` | 0.90 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_MOSS_F0` | 0.035 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_MOSS_ROUGH` | 0.92 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SAND_F0` | 0.045 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SAND_ROUGH` | 0.94 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SHEEN` | 0.032 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SHEEN_POWER` | 3.0 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SNOW_F0` | 0.030 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_SNOW_ROUGH` | 0.72 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_STONE_F0` | 0.040 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_STONE_ROUGH` | 0.92 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_WET_F0` | 0.055 | PBR material set (GGX F0/roughness/sheen) |
| `TR_MAT_WET_ROUGH` | 0.24 | PBR material set (GGX F0/roughness/sheen) |
| `TR_METEOR_GAIN` | 1.60 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_METEOR_PERIOD` | 48.0 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_METEOR_TRAIL` | 90.0 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_MICRO_DETAIL_SCALE` | 1.35 | micro-detail & terrain normal work |
| `TR_MICRO_DETAIL_STRENGTH` | 0.20 | micro-detail & terrain normal work |
| `TR_MICRO_ROUGHNESS` | 0.14 | micro-detail & terrain normal work |
| `TR_MIE_OPEN_HI` | 0.80 | aerial perspective / mist |
| `TR_MIE_OPEN_LO` | 0.30 | aerial perspective / mist |
| `TR_MIE_STRENGTH` | 0.22 | aerial perspective / mist |
| `TR_MIST_BASE` | 56.0 | aerial perspective / mist |
| `TR_MIST_SCALE` | 9.0 | aerial perspective / mist |
| `TR_MIST_STRENGTH` | 0.10 | aerial perspective / mist |
| `TR_MIST_SUN` | 0.30 | aerial perspective / mist |
| `TR_MOON_COLOUR` | vec3f(0.62, 0.72, 1.00) | night/moon ambient system |
| `TR_MOON_DIFFUSE` | 0.30 | night/moon ambient system |
| `TR_MOON_DISC_GAIN` | 4.20 | moon disc & ring render |
| `TR_MOON_DISC_HI` | 0.99975 | moon disc & ring render |
| `TR_MOON_DISC_LO` | 0.99920 | moon disc & ring render |
| `TR_MOON_OPEN_HI` | 0.70 | night/moon ambient system |
| `TR_MOON_OPEN_LO` | 0.25 | night/moon ambient system |
| `TR_MOON_REDDEN` | 0.80 | night/moon ambient system |
| `TR_MOON_RING_GAIN` | 0.32 | moon disc & ring render |
| `TR_MOON_RING_HI` | 0.99920 | moon disc & ring render |
| `TR_MOON_RING_LO` | 0.99780 | moon disc & ring render |
| `TR_MW_GAIN` | 0.10 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_MW_SCALE` | 2.60 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_MW_TILT` | vec3f(0.42, 0.86, -0.28) | night-sky features (stars/milky way/aurora/meteors) |
| `TR_NIGHT_AMBIENT` | 0.46 | night/moon ambient system |
| `TR_NIGHT_AMBIENT_LIFT` | 1.00 | night/moon ambient system |
| `TR_NIGHT_DIM` | 0.92 | lighting framework (keep/unlit/night/shelter) |
| `TR_NOISE_ORIGIN` | vec2f(31.7, 71.3) | hash origin salt |
| `TR_NOISE_WRAP` | 256.0 | maths/noise plumbing |
| `TR_NOISE_WRAP_INV` | 0.00390625 | maths/noise plumbing |
| `TR_ORE_GLOW` | 0.22 | ore sparkle & spec boost |
| `TR_ORE_ROUGHNESS_DROP` | 0.12 | ore sparkle & spec boost |
| `TR_ORE_SPEC_BOOST` | 0.35 | ore sparkle & spec boost |
| `TR_PI` | 3.14159265359 | maths/noise plumbing |
| `TR_PLANT_ROOT` | 0.10 | plant-root detection tolerance |
| `TR_PLANT_TOL` | 0.045 | plant-root detection tolerance |
| `TR_RELIEF_SHADE` | 0.45 | relief shading |
| `TR_RELIEF_SIGN` | 1.0 | relief shading |
| `TR_RELIEF_STRENGTH` | 0.55 | relief shading |
| `TR_SAND_RIPPLE_AMP` | 0.18 | sand ripples |
| `TR_SAND_RIPPLE_FREQ` | 5.80 | sand ripples |
| `TR_SAND_RIPPLE_WANDER` | 0.14 | sand ripples |
| `TR_SHADE_DUSK` | vec3f(0.58, 0.58, 0.88) | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADE_SKY` | vec3f(0.84, 0.89, 0.98) | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_DUSK_SOFT` | 0.03 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_DUSK_WIDEN` | 0.05 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_SOFTNESS` | 0.040 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_SUN_FLOOR` | 0.10 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_THRESHOLD` | 0.95 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHADOW_TINT_COOL` | 0.50 | shadow shaping (thresholds, dusk widening, cool tint) |
| `TR_SHELTER_SINK` | 0.26 | lighting framework (keep/unlit/night/shelter) |
| `TR_SHOULDER` | 0.80 | tone mapping & grade |
| `TR_SHOULDER_KNEE` | 0.66 | tone mapping & grade |
| `TR_SKYSPEC_ROUGH_HIGH` | 0.75 | sky specular on water |
| `TR_SKYSPEC_ROUGH_LOW` | 0.35 | sky specular on water |
| `TR_SKYSPEC_STRENGTH` | 0.18 | sky specular on water |
| `TR_SKY_AMBIENT_HUE` | vec3f(0.90, 0.965, 1.07) | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_DUSK` | vec3f(1.00, 0.45, 0.20) | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_DUSK_FADE` | 7.0 | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_DUSK_GAIN` | 0.90 | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_DUSK_POW` | 3.0 | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_HAZE_GAIN` | 0.42 | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_HORIZON` | vec3f(0.66, 0.79, 0.93) | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_ZENITH` | vec3f(0.16, 0.36, 0.80) | sky gradient (zenith/horizon/dusk) |
| `TR_SKY_ZENITH_POW` | 0.45 | sky gradient (zenith/horizon/dusk) |
| `TR_SNELL_HI` | 0.72 | Snell window underwater |
| `TR_SNELL_LO` | 0.58 | Snell window underwater |
| `TR_SNELL_SKY` | 0.85 | Snell window underwater |
| `TR_SNELL_SUN` | 2.20 | Snell window underwater |
| `TR_SPARKLE_DENSITY` | 0.10 | water sparkle glints |
| `TR_SPARKLE_SCALE` | 1.30 | water sparkle glints |
| `TR_SPARKLE_STRENGTH` | 0.26 | water sparkle glints |
| `TR_SPEC_AA` | 0.10 | specular system & anti-aliasing |
| `TR_SPEC_STRENGTH` | 0.55 | specular system & anti-aliasing |
| `TR_SSS_BIAS` | 0.85 | subsurface scattering on foliage |
| `TR_SSS_FLOOR` | 0.18 | subsurface scattering on foliage |
| `TR_SSS_STRENGTH` | 0.42 | subsurface scattering on foliage |
| `TR_STAR_DENSITY` | 0.0022 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_STAR_GAIN` | 1.30 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_STAR_SCALE` | 190.0 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_STAR_TWINKLE` | 0.35 | night-sky features (stars/milky way/aurora/meteors) |
| `TR_SUNSET_BAND` | 0.30 | sun/sunset response |
| `TR_SUN_AIRMASS` | 0.26 | sun airmass reddening (sky model) |
| `TR_SUN_AIRMASS_MAX` | 9.00 | sun airmass reddening (sky model) |
| `TR_SUN_AIRMASS_NORM` | 1.16413 | sun airmass reddening (sky model) |
| `TR_SUN_AIR_RGB` | vec3f(0.34, 0.62, 1.00) | sun airmass reddening (sky model) |
| `TR_SUN_BUDGET_GAIN` | 0.20 | sun/sunset response |
| `TR_SUN_DIRECTION_BLEND` | 0.60 | sun/sunset response |
| `TR_SUN_DISC_GAIN` | 26.0 | sun disc & glow render |
| `TR_SUN_DISC_HI` | 0.99970 | sun disc & glow render |
| `TR_SUN_DISC_LO` | 0.99880 | sun disc & glow render |
| `TR_SUN_GLOW_GAIN` | 0.90 | sun disc & glow render |
| `TR_SUN_GLOW_HI` | 0.9992 | sun disc & glow render |
| `TR_SUN_GLOW_LO` | 0.9920 | sun disc & glow render |
| `TR_SUN_HUE` | vec3f(1.00, 0.98, 0.95) | sun airmass reddening (sky model) |
| `TR_SUN_REDDEN` | 0.85 | sun airmass reddening (sky model) |
| `TR_SUN_STRENGTH` | 0.85 | sun/sunset response |
| `TR_SWAY_ANGLE` | 0.55 | sway angle cap |
| `TR_TAU` | 6.28318530718 | maths/noise plumbing |
| `TR_TERRAIN_ROUGHNESS` | 1.05 | micro-detail & terrain normal work |
| `TR_TONEMAP_STRENGTH` | 1.0 | tone mapping & grade |
| `TR_TORCH_PIERCE_GAIN` | 1.40 | torch warm tint & pierce |
| `TR_TORCH_PIERCE_TINT` | 0.60 | torch warm tint & pierce |
| `TR_TORCH_WARM_TINT` | vec3f(1.10, 0.86, 0.62) | torch warm tint & pierce |
| `TR_UNDERWATER_ABSORB` | vec3f(0.32, 0.055, 0.022) | underwater grade when camera submerged |
| `TR_UNDERWATER_BLUE_HI` | 0.30 | underwater grade when camera submerged |
| `TR_UNDERWATER_BLUE_LO` | 0.10 | underwater grade when camera submerged |
| `TR_UNDERWATER_CAUSTIC` | 0.55 | underwater grade when camera submerged |
| `TR_UNDERWATER_DEEP` | vec3f(0.020, 0.130, 0.190) | underwater grade when camera submerged |
| `TR_UNDERWATER_RATIO` | 1.333 | underwater grade when camera submerged |
| `TR_UNDERWATER_RATIO_HI` | 2.80 | underwater grade when camera submerged |
| `TR_UNDERWATER_RATIO_LO` | 2.00 | underwater grade when camera submerged |
| `TR_UNDERWATER_STRENGTH` | 0.85 | underwater grade when camera submerged |
| `TR_UNLIT_GAIN` | 1.0 | lighting framework (keep/unlit/night/shelter) |
| `TR_VERTEX_GUST` | 0.45 | vertex displacement hooks (few-game feature) |
| `TR_VERTEX_LIFT` | 0.35 | vertex displacement hooks (few-game feature) |
| `TR_VERTEX_ROOT` | 0.15 | vertex displacement hooks (few-game feature) |
| `TR_VERTEX_SWAY` | 0.140 | vertex displacement hooks (few-game feature) |
| `TR_WATER_CLARITY` | 0.82 | water clarity (view-through) |
| `TR_WATER_DAY_TINT` | vec3f(0.34, 0.78, 0.82) | water tint, day band |
| `TR_WATER_DUSK_TINT` | vec3f(0.20, 0.48, 0.66) | water tint, dusk band |
| `TR_WATER_GLINT` | 0.82 | sun glint strength |
| `TR_WATER_MIRROR_CAP` | 1.05 | water optics |
| `TR_WATER_MIRROR_CHROMA` | 0.80 | water optics |
| `TR_WATER_MIRROR_PRESS` | 1.60 | water optics |
| `TR_WATER_MOON_GLINT` | vec3f(0.48, 0.66, 0.88) | water optics |
| `TR_WATER_NIGHT_TINT` | vec3f(0.075, 0.19, 0.34) | water tint, night band |
| `TR_WATER_REFLECTIVITY` | 0.78 | water reflectivity |
| `TR_WATER_RIPPLE` | 0.105 | ripple amplitude |
| `TR_WATER_TINT` | 0.48 | water tint mix strength |
| `TR_WAVE_OMEGA_A` | 0.502655 | wave band A angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_B` | 0.726057 | wave band B angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_C` | 0.949459 | wave band C angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_D` | 1.605703 | wave band D angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_E` | 1.982694 | wave band E angular frequency (frozen R17) |
| `TR_WAVE_OMEGA_F` | 2.415536 | wave band F angular frequency (frozen R17) |
| `TR_WIND_FIELD_BASE` | 0.5 | wind field for foliage |
| `TR_WIND_FIELD_SCALE` | 0.012 | wind field for foliage |
| `TR_WIND_FIELD_SPEED` | 0.551111 | wind field for foliage |
| `TR_WIND_SPEED_STEP` | 0.013889 | wind master settings |

## PROBE-DIAG-v2 (measurement probe, modes 0-15) — 19 constants

| Constant | Value | Role |
|---|---|---|
| `MODE_0_SKYLIGHT_RAW` | 0 | probe mode 0 — raw skyLight to all channels |
| `MODE_10_DIRECTIONAL_GRAY` | 10 | probe mode 10 — terrain directional light as grey |
| `MODE_11_DEPTH_DEFINE` | 11 | probe mode 11 — is BLOXD_SCENE_DEPTH active (green/red) |
| `MODE_12_DEPTH_FOUND` | 12 | probe mode 12 — bloxdOpaqueBehind().found (green/red) |
| `MODE_13_DEPTH_PATH_BANDS` | 13 | probe mode 13 — water path depth colour bands |
| `MODE_14_DEPTH_VERTICAL_BANDS` | 14 | probe mode 14 — vertical depth colour bands |
| `MODE_15_DEPTH_BED_ANCHOR` | 15 | probe mode 15 — bed anchor visualisation (fract bed.y) |
| `MODE_1_SKY_LEVEL_0_15` | 1 | probe mode 1 — skyLight rescaled 0-15 |
| `MODE_2_BLOCKLIGHT_RGB` | 2 | probe mode 2 — blockLight RGB as colour |
| `MODE_3_HELDLIGHT_RGB_X4` | 3 | probe mode 3 — heldLight ×4 (visibility boost) |
| `MODE_4_SKYLIGHTCOLOUR_NORM` | 4 | probe mode 4 — skyLightColour normalised |
| `MODE_5_AMBIENTCOLOUR_NORM` | 5 | probe mode 5 — ambient colour normalised |
| `MODE_6_FOGVISIBILITY_GRAY` | 6 | probe mode 6 — fogVisibility as grey |
| `MODE_7_FOGCOLOUR_RAW` | 7 | probe mode 7 — raw fogColour (reveals black in mode NONE) |
| `MODE_8_SUNDIRECTION_RGB` | 8 | probe mode 8 — sun direction as RGB |
| `MODE_9_SUNLENGTH_GRAY` | 9 | probe mode 9 — |sunDir| as grey (0 on sunless skies) |
| `MODE_SECONDS` | 60.0 | probe seconds-per-mode before rotating |
| `PROBE_MODE` | -1 | probe channel selector; >=0 freezes a measurement mode |
| `TR_EPS` | 0.0001 | probe epsilon |

## Breeze v1 (shipped pack, dissected — Crownix after Ellie) — 61 constants

| Constant | Value | Role |
|---|---|---|
| `BLOCK_VARIATION` | 0.04 | per-block / per-cell brightness variation |
| `BRIGHTEN` | 1.45 | pre-fog grade (lift + chroma-guarded vibrance) |
| `CANOPY_SPREAD` | 0.0035 | tree-canopy shadow (lost skyLight level) |
| `CANOPY_STRENGTH` | 1.0 | tree-canopy shadow (lost skyLight level) |
| `CANOPY_TINT` | vec3f(0.5, 0.56, 0.7) | tree-canopy shadow (lost skyLight level) |
| `CELLS_PER_BLOCK` | 8 | shading-cell lattice plumbing |
| `CELL_FAR` | 40.0 | per-block / per-cell brightness variation |
| `CELL_VARIATION` | 0.06 | per-block / per-cell brightness variation |
| `COARSE_SHIFT` | vec2i(117, 44) | rotated-integer-lattice wave octaves & LOD |
| `COARSE_STRIDE` | 2000 | rotated-integer-lattice wave octaves & LOD |
| `CREST_GAIN` | 0.02 | wave-crest lighting |
| `DEEP_OPACITY` | 0.97 | depth-driven opacity ramp |
| `DEEP_TINT` | vec3f(0.05, 0.18, 0.5) | Beer-Lambert depth colouring |
| `DEPTH_DARKEN` | 0.32 | Beer-Lambert depth colouring |
| `FALLING_LEAVES` | true | painted falling-leaf raymarch |
| `FINE_FAR` | 40.0 | rotated-integer-lattice wave octaves & LOD |
| `FINE_NEAR` | 24.0 | rotated-integer-lattice wave octaves & LOD |
| `FINE_SHIFT` | vec2i(459, 312) | rotated-integer-lattice wave octaves & LOD |
| `FINE_STRIDE` | 3700 | rotated-integer-lattice wave octaves & LOD |
| `FOAM_COLOUR` | vec3f(0.97, 0.99, 1.0) | shoreline foam edge |
| `FOAM_SOLID` | 0.1 | shoreline foam edge |
| `FOAM_WIDTH` | 0.45 | shoreline foam edge |
| `GLINT_COLOUR` | vec3f(1.0, 0.97, 0.88) | broad sun sheen colour |
| `GRAIN_NEAR` | 14.0 | near grain cutoff |
| `GRASS_GUSTS` | 0.16 | wind gusts rolling over grass tops |
| `GUST_DIRECTION` | vec2f(0.92, 0.39) | wind gusts rolling over grass tops |
| `HASH_PERIOD` | 289 | shading-cell lattice plumbing |
| `LANDING_RINGS` | true | feature toggle: leaf-landing rings |
| `LEAF_CELL` | 3.0 | painted falling-leaf raymarch |
| `LEAF_CHANCE` | 0.3 | painted falling-leaf raymarch |
| `LEAF_FALL` | 0.6 | painted falling-leaf raymarch |
| `LEAF_RANGE` | 10.0 | painted falling-leaf raymarch |
| `LEAF_SHIMMER` | 0.3 | gust shimmer on leaves |
| `LEAF_SIZE` | 0.09 | painted falling-leaf raymarch |
| `LEAF_STEPS` | 6 | painted falling-leaf raymarch |
| `MIST` | 0.16 | blotch strength |
| `MIST_FAR` | 48.0 | drifting world-fixed blotches |
| `MIST_SIZE` | 5.0 | drifting world-fixed blotches |
| `REFLECTIVITY` | 0.45 | Schlick sky reflection |
| `RING_CELL` | 4 | leaf-landing rings on water |
| `RING_CHANCE` | 0.45 | leaf-landing rings on water |
| `RING_EVERY` | 5.0 | leaf-landing rings on water |
| `RING_SIZE` | 1.1 | leaf-landing rings on water |
| `RING_STRENGTH` | 0.4 | leaf-landing rings on water |
| `SHADE_FROM` | -0.1 | face-direction sun tint bounds |
| `SHADE_TINT` | vec3f(0.76, 0.8, 0.88) | face-direction sun tint bounds |
| `SHALLOW_OPACITY` | 0.3 | depth-driven opacity ramp |
| `SHALLOW_TINT` | vec3f(0.58, 0.92, 0.92) | Beer-Lambert depth colouring |
| `SKY_REFLECTION_COLOUR` | vec3f(0.68, 0.79, 0.94) | Schlick sky reflection |
| `SOFTEN` | 0.12 | texture speckle smoothing (soft look) |
| `SOFT_LEVEL` | 0.5 | texture speckle smoothing (soft look) |
| `SUNSPOTS` | 0.45 | drifting sunspots through canopy shadow |
| `SUNSPOT_SPEED` | 0.3 | drifting sunspots through canopy shadow |
| `SUN_FROM` | 0.35 | face-direction sun tint bounds |
| `SUN_TINT` | vec3f(1.1, 1.04, 0.94) | face-direction sun tint bounds |
| `TAU` | 6.2831853 | 2π constant |
| `VIBRANCE` | 0.22 | pre-fog grade (lift + chroma-guarded vibrance) |
| `WATER_ALPHA` | 0.9 | water's engine-registered values (rebuilt from) |
| `WATER_COLOUR` | vec3f(0.5, 0.5, 0.8) | water's engine-registered values (rebuilt from) |
| `WIND_SPEED` | 0.8 | wind master settings |
| `WIND_STRENGTH` | 1.0 | wind master settings |

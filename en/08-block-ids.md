# Part VIII — The numeric block-id table

The render pipeline’s `blockId: u32` is the key to per-block shading. This table is curated for
shading work; regenerate the full list any time in-game:

```
for (i = 2; i < 3400; i++) api.log(i + " = " + api.blockIdToBlockName(i))
```

(paste into a Code Block; the id space grows with updates — a 2026 dump already ends at 2089
while shipped packs target ids up to 3254.)

## Shading-relevant groups (read-verified entries)

| Group | Ids |
|---|---|
| **Natural** | 2 Dirt · 3 Messy Dirt · 4 **Grass Block** · 5 Sand · 6 Clay · 7 Gravel · 8 Snow · 28 Stone · 29 Messy Stone · 31 Smooth Stone · 32-37 Diorite/Andesite/Granite (+smooth) · 38 Sandstone · 39 Yellowstone · 139 Ice · 140 Obsidian · 147 Bedrock · 650 Red Sand · 652 Rocky Dirt · 472 Useless Soil · 1295 Melting Ice |
| **Magma** | 471 **Magma** (the solid lava block) |
| **Ore / metals** | 40 Coal · 41 Iron · 42 Gold · 43 Lapis · 44 Emerald · 45 Diamond · 465 Moonstone Ore · blocks 46-50 · 172 Diamond · 470 Moonstone |
| **Leaves** | 100 Pine · 101 Aspen · 102 Maple · 103 Elm · 491 Plum · 492 Cedar · 493 Palm · 911 Pear · 653 Autumn Maple · 1226 Cherry · canopies 208-211, 494-496, 938, 654, 1259 |
| **Logs** | 9 Maple · 10 Pine · 11 Plum · 12 Cedar · 13 Aspen · 14 Elm · 502 Palm · 909 Pear · 1222 Cherry · stripped 21-26, 1112-1121 |
| **Plants** | **150 Grass** (the plant) · 151-163 flowers · **1109 Tall Grass** · 1110 Tall Grass\|Top · 149 Cactus · 213 Fat Cactus · 219 Vines · 105 Watermelon · 975 Pumpkin · 957 Cobweb |
| **Liquids** | **126 Water** · **1491 Lava** |
| **Light** | 124 Dim Lamp On · 125 Off · 143 Beacon · 164 Furnace · 168 Workbench · 980 Jack o’Lantern · 145 Golden Decoration · 146 Moonstone Explosive |
| **Glass** | 106 Glass · 107-122 the 16 tints · 992-1007 Patterned |
| **Coloured** | 51-66 Wool · 67-83 Baked Clay · 84-99 Concrete · 228-243 Planks · 245-308 Ceramic · 1040-1055 Carpet |
| **Special** | 0 Air · 1 Unloaded · 127 Invisible Solid · 1510 Code Block · 1512 worldedit-ghost |

## Live annex — ids beyond the 2026 dump (proven by a shipped pack)

A released pack (Breeze v1) targets these, none of which exist in the 2089-id dump — the game
grew; exact names pending a fresh dump:

- **Leaves** (their `isLeaf`): **1636 · 1969 · 2019 · 2020 · 2021 · 2022 · 2023 · 2024 · 2025 · 2085**
- **Grass Blocks** (their `isGrassBlock`): **1694 · 1955 · 3071 · 3072 · 3073 · 3253 · 3254**

## Gotchas

- **Two namespaces**: scripting uses string ids (`api.setBlock(...)`) — the shader’s u32 is the
  render id. Map via `api.blockIdToBlockName(i)` loops, never by guessing.
- Prefer **group switches** over equality: new biome variants arrive as new ids in the same
  family (see the annex).
- Id 4 = the grass **block** (top-face effects); 150 = the grass **plant** (unreachable — its
  sway is engine-side). Both have shipped-pack precedent.

# Partie VIII — La table numérique des ids de blocs (FR)

Le `blockId : u32` du rendu est la clé du shading par bloc. Table curée pour le shading ;
régénérer la liste complète en jeu :

```
for (i = 2; i < 3400; i++) api.log(i + " = " + api.blockIdToBlockName(i))
```

(dans un Code Block ; l'espace d'ids grandit — un dump 2026 finissait à 2089 alors qu'un pack
publié cible jusqu'à 3254.)

## Groupes pertinents pour le shading (entrées vérifiées à la lecture)

| Groupe | Ids |
|---|---|
| **Naturels** | 2 Dirt · 3 Messy Dirt · 4 **Grass Block** · 5 Sand · 6 Clay · 7 Gravel · 8 Snow · 28 Stone · 29 Messy Stone · 31 Smooth Stone · 32-37 Diorite/Andesite/Granite (+smooth) · 38 Sandstone · 39 Yellowstone · 139 Ice · 140 Obsidian · 147 Bedrock · 650 Red Sand · 652 Rocky Dirt · 472 Useless Soil · 1295 Melting Ice |
| **Magma** | 471 **Magma** (le bloc lave solide) |
| **Minerai / métaux** | 40 Coal · 41 Iron · 42 Gold · 43 Lapis · 44 Emerald · 45 Diamond · 465 Moonstone Ore · blocs 46-50 · 172 Diamond · 470 Moonstone |
| **Feuilles** | 100 Pine · 101 Aspen · 102 Maple · 103 Elm · 491 Plum · 492 Cedar · 493 Palm · 911 Pear · 653 Autumn Maple · 1226 Cherry · canopées 208-211, 494-496, 938, 654, 1259 |
| **Bois** | 9 Maple · 10 Pine · 11 Plum · 12 Cedar · 13 Aspen · 14 Elm · 502 Palm · 909 Pear · 1222 Cherry · écorcés 21-26, 1112-1121 |
| **Plantes** | **150 Grass** (la plante) · 151-163 fleurs · **1109 Tall Grass** · 1110 Tall Grass\|Top · 149 Cactus · 213 Fat Cactus · 219 Vines · 105 Watermelon · 975 Pumpkin · 957 Cobweb |
| **Liquides** | **126 Water** · **1491 Lava** |
| **Lumière** | 124 Dim Lamp On · 125 Off · 143 Beacon · 164 Furnace · 168 Workbench · 980 Jack o'Lantern · 145 Golden Decoration · 146 Moonstone Explosive |
| **Vitres** | 106 Glass · 107-122 les 16 teintées · 992-1007 Patterned |
| **Colorés** | 51-66 Wool · 67-83 Baked Clay · 84-99 Concrete · 228-243 Planks · 245-308 Ceramic · 1040-1055 Carpet |
| **Spéciaux** | 0 Air · 1 Unloaded · 127 Invisible Solid · 1510 Code Block · 1512 worldedit-ghost |

## Annexe live — ids au-delà du dump 2026 (prouvés par un pack publié)

Un pack publié (Breeze v1) cible ces ids, absents du dump à 2089 — le jeu a grandi ; noms
exacts en attente d'un dump frais :

- **Feuilles** (leur `isLeaf`) : **1636 · 1969 · 2019 · 2020 · 2021 · 2022 · 2023 · 2024 · 2025 · 2085**
- **Grass Blocks** (leur `isGrassBlock`) : **1694 · 1955 · 3071 · 3072 · 3073 · 3253 · 3254**

## Pièges

- **Deux espaces de noms** : scripting = ids string ; le u32 du shader = id de rendu. Mapper via
  des boucles `api.blockIdToBlockName(i)`, jamais en devinant.
- Préférer des **switch de groupes** aux égalités : les variantes de biome arrivent comme de
  nouveaux ids dans la même famille (voir l'annexe).
- Id 4 = le **bloc** d'herbe (effets sur la face du dessus) ; 150 = la **plante** (inatteignable,
  sway côté moteur). Les deux ont un précédent dans des packs publiés.

# Partie II — Le contrat API (FR)

Provenances : **[publié]** = prouvé dans un pack en production · **[nôtre]** = exercé par nos
packs validés.

## Les quatre hooks

| Hook | Rôle |
|---|---|
| `bloxdTerrainSurface(BloxdSurfaceIn) -> BloxdSurface` | recolorie/alpha du terrain opaque |
| `bloxdTerrainLight(BloxdSurface, BloxdLightIn) -> BloxdLight` | couleur finale éclairée (fog via `bloxdApplyFog`) |
| `bloxdLiquidSurface(BloxdSurfaceIn) -> BloxdSurface` | couleur/alpha des liquides |
| `bloxdLiquidLight(BloxdSurface, BloxdLightIn) -> BloxdLight` | couleur finale des liquides |

Faits structurants :

- **Surface puis light, dans le même fragment** : passe de données par `var<private>` de scope
  module **[publié]**.
- Surface tourne **avant l'alphaTest** : `out.alpha` pilote le discard des cutouts (plantes,
  feuilles) et est la vraie transparence des liquides ; sans effet sur l'opaque simple.
- **`out.emission` appartient au hook surface**.
- Toujours repartir de `bloxdDefault*` ; paramètres inutilisés → forme nue `_ = param;`.

## Structs (champs prouvés en usage)

```wgsl
BloxdSurfaceIn { colour, alpha, position, normal, blockId: u32, /* … */ }
BloxdSurface   { colour, alpha, emission, /* … */ }
BloxdLightIn   { position, normal, blockId, skyLight, blockLight, heldLight,
                 skyLightColour, litColour, fogVisibility, fogColour /* … */ }
BloxdLight     { colour /* … */ }
```

- `blockId : u32` — **l'id numérique** (table Partie VIII) = la clé du shading par bloc.
- `skyLight` — **tone-mappé** (Partie IV) ; ciel ouvert ≈ 1 ; un niveau perdu sous canopée ≈ 0.995.
- `blockLight` / `heldLight` — canaux couleur (lampes colorées possibles).
- `skyLightColour` — teinte du ciel, s'assombrit la nuit **[publié]**.
- `litColour` — la couleur éclairée propre de la surface **[publié]**.
- `fogColour` arrive **noir** quand le fog est en mode NONE.

## Fonctions moteur

| Fonction | Rôle |
|---|---|
| `bloxdDefaultSurface` / `bloxdDefaultLight` | point de départ obligatoire |
| `bloxdApplyFog(colour, light)` | mix(fogColour, colour, fogVisibility) — en dernier, après ton grade |
| `bloxdSunDirection()` | vecteur soleil ; **(0,0,0) sans ciel de type terre** ; lune = −soleil ; statique en monde défaut |
| `bloxdTime()` / `bloxdTimeWrap` | secondes, wrap 3600 — animer en **cycles entiers** |
| `bloxdEyePosition()` | caméra (distances, LOD, vecteurs de vue) |
| `bloxdOriginOffset()` | rebase floating-origin — **à injecter dans tout hash monde** |
| `bloxdFaceBlock(pos, normal)` | id du bloc de la face courante (hook surface) **[publié]** |
| `bloxdOpaqueBehind()` | `{found, position}` — épaisseur d'eau, approx réfraction **[publié]** |

## Règles dures

1. Jamais de `#define BLOXD_*` (macros owned par le moteur, par variante).
2. Jamais de construction littérale des structs — toujours `bloxdDefault*`.
3. `mod` est **réservé** — utiliser `%`.
4. Pas de textures, samplers, builtins, UV écran, `discard` en strict.
5. Liquides : alpha écrit dans toutes les variantes (reconstruit depuis l'alpha enregistré).
6. `let _ =` rejeté — forme nue `_ = expr;`.
7. Total `.wgsl` ≤ 256 Ko.
8. Viser le compilateur Tint du navigateur, pas juste naga : parenthéser les chaînes
   bitwise/décalages.

## Les 8 variantes à survivre

strict × lit × {terrain, liquide} et allow × lit × {terrain, liquide} (+ variantes unlit).
« Strict » = serveurs durcis : pas de discard, features réduites. Sans « Lighting », le jeu
n'envoie **aucun skyLight** : la logique d'ombre s'éteint silencieusement (prouvé par un pack
publié). Le comportement des hooks light en unlit n'est **pas encore mesuré** — écrire des hooks
indifférents à cette question. Tout hook doit compiler dans les 8 variantes (Partie VI).

## Capacités & frontières — la matrice définitive

| Les packs PEUVENT | Les packs NE PEUVENT PAS |
|---|---|
| recolorier terrain & liquides **par blockId** (Partie VIII) | toucher plantes/fleurs (chemin moteur inaccessible **[publié]**) |
| régler l'alpha des cutouts (discard) et des liquides (blend) | post-traiter l'image (aucun accès écran) |
| auto-luminance via `out.emission` (hook surface) | lire la profondeur de scène — sauf `bloxdOpaqueBehind()` à travers un liquide |
| grader, teinter, agir avant le fog, termes ciel | vrai shadow-mapping ou SSAO au-delà de ce que skyLight encode |
| effets procéduraux ancrés monde (hash + rebase) | ajouter objets/particules au monde (peindre des surmontes, R14) |
| données `var<private>` surface→light par fragment | textures/samplers/binds supplémentaires |
| déformation de sommets | en dépendre — **quelques jeux seulement** **[publié]** |
| réagir à blockLight/heldLight, soleil, temps | connaître la direction du faisceau tenu ; avoir une UI de config par monde |

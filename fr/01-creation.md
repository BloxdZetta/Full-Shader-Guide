# Partie I — Créer un pack (FR)

## Ce qu'est un pack

Un **.zip** contenant `pack.json` (métadonnées) + un ou plusieurs `.wgsl`, n'importe quelle
arborescence.

```json
{ "apiVersion": 2, "name": "Mon Pack", "author": "toi" }
```

- `apiVersion` doit être le **nombre** 2 — les packs v1 sont rejetés par le jeu actuel.
- Aucune liste de fichiers dans pack.json (voir multi-fichiers).

## Installation (ce que feront tes utilisateurs)

Bloxd → `O` Réglages → Graphismes → cocher **Use New WebGPU Renderer** → Shader Pack →
**Choose .zip** → **Apply**. Navigateur WebGPU récent requis ; certains jeux désactivent les packs.

## Ce qu'un pack peut toucher

**Blocs, eau et lave uniquement** (+ quelques chemins de couleur exposés par le hook light).
Les plantes/fleurs sont dessinées par une partie du moteur **inaccessible aux packs** (prouvé
par dissection). La déformation de sommets existe mais **ne tourne que dans quelques jeux**.

## Multi-fichiers — IMPORTANT (prouvé sur le terrain)

Le loader **globbe tous les `*.wgsl` du zip et les concatène**. Aucun `shader.wgsl` racine
requis : le pack n°1 du workshop envoie 10 fichiers en sous-dossiers sans racine. Le scope
module WGSL étant indépendant de l'ordre, l'ordre des fichiers est libre. Les deux layouts sont
valides ; le multi-fichiers est plus maintenable, le mono-fichier plus facile à partager.

## Caps

- **256 Ko** de `.wgsl` total après concaténation (cap loader).
- WGSL uniquement, pas de `#include`, pas de préprocesseur maison.
- Le coût par fragment est à ta charge : gate les effets coûteux (distance / blockId, Partie III).

## Distribution

- **Le workshop bloxdhub** est la vitrine de fait ; chaque page item expose un lien zip direct
  `media.bloxdhub.com/workshop-files/<token>.zip`. Liens Drive/GitHub également valables.
- Les utilisateurs retéléchargent manuellement à chaque mise à jour (cadence « hot »).

## Pack minimal qui marche

`shader.wgsl` :

```wgsl
fn bloxdTerrainSurface(surface: BloxdSurfaceIn) -> BloxdSurface {
    var out = bloxdDefaultSurface(surface);
    out.colour = out.colour * vec3f(1.02, 1.0, 0.96);
    return out;
}

fn bloxdTerrainLight(surface: BloxdSurface, light: BloxdLightIn) -> BloxdLight {
    var out = bloxdDefaultLight(surface, light);
    _ = surface; // forme nue obligatoire en v2
    return out;
}
```

Zip avec pack.json **à la racine du zip**. Ensuite : Partie II.

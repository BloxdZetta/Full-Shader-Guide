# Partie VI — Implémentation & validation locale (FR)

## Layout maintenable

```
mon-pack/
├── pack.json
├── lib/hash.wgsl        # hash + rebase origine (R8/R9)
├── terrain/*.wgsl       # une préoccupation par fichier
├── water/*.wgsl
└── effects/*.wgsl
```

Le loader concatène : dépendances inter-fichiers sans ordre (fonctions pures au scope module,
`var<private>` confiné à une préoccupation).

## Pipeline local (avant chaque release)

1. **Test de concat** — reconstruire la concaténation du loader ; compiler CE fichier aussi.
2. **Compile 8 variantes** — naga local avec prelude moteur stubé par variante :
   strict/allow × lit/unlit × terrain/liquide. 8/8 localement n'a jamais échoué en jeu chez nous.
   Si ton stub manque un symbole (ex. `bloxdOpaqueBehind`), corrige le STUB, pas le pack.
3. **Checks statiques** — mots réservés (`mod`), `#define BLOXD_`, structs littéraux, `let _`,
   marqueurs TODO, taille ≤ 256 Ko.
4. **Audit boucles/logique** — toute boucle par fragment bornée ET gated (distance/blockId) ;
   tout facteur d'assombrissement multiplié par la garde lampes.
5. **Packaging** — zip avec pack.json **à la racine** ; publier le sha256 avec la release.
6. **Smoke test en jeu** — monde jour, nuit, grotte, un arbre, bord d'eau, lampe, monde ciel
   sans soleil ; captures ; comparaison à la release précédente.
7. **Matrice de stress via les options de monde** — les mondes peuvent surcharger ce que les
   packs reçoivent = environnements de test gratuits : override `fogColour`, overrides
   skyLight / lumière ambiante, `lightingOverride`, types de skybox (earth, gloomy,
   interstellar/espace ⇒ **vecteur soleil nul**), mondes jour/nuit, plus mondes Lighting off.
   Un pack qui survit à cette matrice (effets soleil auto-off, fog-sûr, grottes correctes)
   est de qualité release.

## Mesurer plutôt que deviner

- Monde « sonde » (seed fixe, bande horaire fixe) + captures à caméra fixe.
- Cale ta courbe de grade sur des paires log-log de luminance des captures.
- Packs sondes (jamais publiés) : écrire les grandeurs moteur dans les canaux couleur (skyLight
  → rouge, blockLight → vert…) et relire à la pipette — c'est ainsi que les seuils de tone-mapping
  de la Partie IV ont été mesurés.

## Checklist de release

- [ ] `apiVersion: 2` en nombre
- [ ] 8/8 variantes en local + parenthèses paranoïaques Tint
- [ ] pas de `#define BLOXD_`, struct littérale, `let _`, `mod`, discard en chemin strict
- [ ] alpha liquide écrit dans toutes les branches
- [ ] garde lampes sur tout facteur d'assombrissement
- [ ] boucles bornées + gated
- [ ] taille ≤ 256 Ko
- [ ] sha256 du zip publié
- [ ] smoke testé : jour, nuit, grotte, canopée, bord d'eau, lampe, ciel sans soleil

# Bloxd Shader Packs — Le Guide d'Ingénierie (FR)

**Guide complet et fondé sur des données pour créer des shader packs Bloxd.io (rendu WebGPU).**
Construit à partir de données moteur mesurées, d'une table numérique complète des ids de blocs,
de dissections de packs publiés et d'une chaîne de validation locale — pas au feeling.

> Non officiel. Sans affiliation avec Bloxd.io. L'API peut changer sans préavis.
> Portions assemblées avec assistance IA ; vérifiez en jeu. Format multilingue inspiré de
> [imu31465/Bloxd.io-How-To-Make-Shader-Packs](https://github.com/imu31465/Bloxd.io-How-To-Make-Shader-Packs).

## Pourquoi ce guide est différent

| Les autres guides | Celui-ci |
|---|---|
| « skyLight est une luminosité 0-1 » | skyLight est **tone-mappé** ; seuils réels mesurés (0.45/0.98 ↔ 0.4/0.9 avant courbe) |
| « vérifie le nom du bloc » | **Table numérique complète des ids** (0 → 3254+) avec annexe live issue d'un pack publié |
| « utilise les hooks » | Contrat complet : canal `var<private>` surface→light, `bloxdFaceBlock`, `bloxdOpaqueBehind`, `skyLightColour`, `litColour` — prouvés dans un pack publié |
| fog au folklore | internals du fog (bande 32 blocs, couleur défaut, noir en mode 0) avec provenance |
| aucun outil | une **validation locale naga 8 variantes** qui prédit l'acceptation en jeu |

## Le guide

| Partie | Fichier | Contenu |
|---|---|---|
| I | [01-creation](01-creation.md) | format, pack minimal, multi-fichiers, caps, distribution |
| II | [02-api](02-api.md) | hooks, structs, fonctions moteur, règles dures |
| III | [03-recettes](03-recettes.md) | 12 recettes de production avec snippets WGSL |
| IV | [04-realisme](04-realisme.md) | nombres mesurés : lumière, fog, optique de l'eau, courbes |
| V | [05-depannage](05-depannage.md) | tous les modes de défaillance rencontrés ou disséqués |
| VI | [06-implementation](06-implementation.md) | pipeline de validation locale & QA de packaging |
| VII | [07-internes](07-internes.md) | internals moteur avec étiquettes de provenance |
| VIII | [08-ids-blocs](08-ids-blocs.md) | la table numérique des ids de blocs |
| IX | [09-sources](09-sources.md) | comment on sait tout ça — instruments, politique de provenance, questions ouvertes |

## Langues

EN (canonique) et FR complets. Accueils traduits : Deutsch · Español · Português · Italiano ·
Русский · 日本語 · 한국어 · 简体中文 (le fond reste EN/FR — traductions bienvenues).

## Licence

MIT. Snippets originaux ; constantes citées des packs disséqués créditées en place
(Ellie/whoisEllie, Crownix/Breeze).

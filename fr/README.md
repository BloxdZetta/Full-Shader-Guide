# Bloxd Shader Packs — Le Guide Complet (FR)

**Tout ce qu'on sait sur les shader packs Bloxd.io, expliqué le plus simplement
possible :** comment le rendu web dessine l'image, comment les shaders fonctionnent,
ce qu'un pack peut faire, ce qu'il ne peut pas faire, et comment en construire un —
fondé sur des données moteur mesurées, une table numérique complète des ids de
blocs, des packs de la communauté disséqués, et une validation locale dans les 8
variantes du moteur.

> Non officiel. Sans affiliation avec Bloxd.io. L'API peut changer sans préavis.

## 🚪 Commencer ici (choisissez votre porte)

| Vous êtes… | Commencez par |
|---|---|
| **Débutant en shaders** (ou en code) | ⭐ [Partie 0 — Partir de zéro](00-depart.md) — comment le rendu marche, ce qu'est un shader, votre premier pack en 5 étapes |
| **Codeur** qui veut le contrat | [Partie II — L'API](02-api.md), puis [Partie III — Recettes](03-recettes.md) |
| **À la recherche d'un nombre** | [Partie VIII — Ids de blocs](08-ids-blocs.md) · [Partie X — Constantes](10-constantes.md) · [Partie IV — Réalisme](04-realisme.md) |
| **Un pack cassé à réparer** | [Partie V — Dépannage](05-depannage.md) |

## 📚 Le guide (français, version approfondie)

| Partie | Fichier | Contenu |
|---|---|---|
| 0 | [00-depart](00-depart.md) | **partir de zéro** : rendu web, pipeline GPU, ce qu'est un shader, tout le possible/impossible, premier pack |
| I | [01-creation](01-creation.md) | format du pack, pack minimal, chargement multi-fichiers, limites, distribution |
| II | [02-api](02-api.md) | contrat complet hooks et structs, fonctions moteur, règles dures |
| III | [03-recettes](03-recettes.md) | 12 recettes de production avec snippets WGSL |
| IV | [04-realisme](04-realisme.md) | nombres mesurés : lumière, fog, optique de l'eau, courbes |
| V | [05-depannage](05-depannage.md) | tous les modes de défaillance connus et leur réparation |
| VI | [06-implementation](06-implementation.md) | pipeline de validation locale (8 variantes) & QA de packaging |
| VII | [07-internes](07-internes.md) | internes du moteur : temps, pipeline de lumière, ciel, chargeur |
| VIII | [08-ids-blocs](08-ids-blocs.md) | la table numérique complète des ids de blocs (0 → 3254+) |
| IX | [09-sources](09-sources.md) | comment chaque fait a été établi — instruments, provenance, questions ouvertes |
| X | [10-constantes](10-constantes.md) | chaque constante (551), générées depuis les sources, chacune avec son rôle |

## 🌍 Langues

L'anglais et le français portent le guide approfondi complet (11 parties). Seize
autres langues offrent le guide complet en une page (la Partie 0 intégrale :
rendu, shaders, hooks, limites, premier pack, règles, glossaire) :
[Deutsch](../de/README.md) · [Español](../es/README.md) · [Português](../pt/README.md) ·
[Italiano](../it/README.md) · [Nederlands](../nl/README.md) · [Polski](../pl/README.md) ·
[Türkçe](../tr/README.md) · [Русский](../ru/README.md) · [Українська](../uk/README.md) ·
[العربية](../ar/README.md) · [हिन्दी](../hi/README.md) · [Bahasa Indonesia](../id/README.md) ·
[Tiếng Việt](../vi/README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md) ·
[简体中文](../zh-CN/README.md) — sommaire général : [index du guide](../README.md).

## Licence

MIT. Snippets originaux ; constantes citées des packs de la communauté créditées en
place (Parties IX–X).

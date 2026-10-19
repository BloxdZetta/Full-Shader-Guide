# Partie IX — D'où vient cette connaissance (et ce qu'on ne sait pas) (FR)

Chaque affirmation de ce guide porte une étiquette de provenance. Cette page est la méthode
derrière les étiquettes — parce qu'un guide qui dit *comment il sait* vaut dix qui affirment.

## Les trois classes de provenance

| Étiquette | Signification | Politique de confiance |
|---|---|---|
| **[mesuré]** | produit par des instruments locaux : packs sondes écrivant les grandeurs moteur dans les canaux couleur, pipelines de captures à caméra/monde fixés, fits de courbes sur frames réelles | confiance dans l'enveloppe mesurée |
| **[publié]** | prouvé par un pack communautaire publié tournant dans le jeu live (ex. Breeze v1, disséqué fichier par fichier) | confiance — le jeu lui-même l'a accepté |
| **[tierce]** | restauré du JS de production par l'analyse communautaire (internals imu31465, dumps npm, wiki) | jamais porteur tant que non mesuré ; cité car il a guidé nos sondes |

## Les instruments

- **Harnais naga 8 variantes** — prelude moteur stubé par variante (strict/allow × lit/unlit ×
  terrain/liquide). Chaque release compile 8/8 avant de partir ; ce bilan a prédit l'acceptation
  en jeu sur des dizaines de releases.
- **Fuzz WGSL 42 cas** — formes malformées passées au compilateur pour cartographier ce qui
  casse naga vs ce qui casse le Tint du navigateur (deux compilateurs différents ; le jeu
  utilise celui du navigateur).
- **Packs sondes** (jamais publiés) — skyLight→rouge, blockLight→vert, fog→bleu ; relu à la
  pipette dans des mondes contrôlés. C'est de là que viennent les seuils de tone-mapping et la
  bande d'ombre (13.6-14.95/15).
- **Fit de courbes** — captures à dispositifs connus, régression log-log des paires de
  luminance : la vraie courbe de réponse au lieu d'un gamma deviné.
- **Dissection en oracle inversé** — compiler un pack *publié* dans notre harnais : chaque échec
  = notre harnais qui se trompe, pas le pack (c'est ainsi que `bloxdFaceBlock`,
  `bloxdOpaqueBehind`, `skyLightColour`, `litColour` et le multi-fichiers ont été confirmés).
- **Triangulation multi-sources** — un fait n'est promu que si des sources indépendantes
  concordent (manuel communautaire + wiki + dumps client + nos sondes). Les désaccords sont
  gardés et étiquetés (la rampe de fog, Partie IV).

## Questions ouvertes honnêtes

1. **Forme de la rampe de fog** — linéaire 32×D [tierce] vs EXP2 (ancienne note wiki). Figure
   production-JS privilégiée ; mesure sonde en attente.
2. **Hooks light en unlit** — tournent-ils du tout ? Pas encore mesuré ; écrire des hooks
   indifférents.
3. **Hygiène du loader** — messages d'erreur exacts et chemins de récupération du loader in-game
   (le bundle client existe dans des archives publiques ; lecture dédiée prévue).
4. **Noms des nouveaux ids** — les ids jusqu'à 3254 sont *utilisés* par un pack publié ; les noms
   officiels attendent un dump frais de `api.blockIdToBlockName`.

## Les chiffres derrière ce guide

Table numérique complète des ids (0 → 3254+) · dizaines de releases validées sur deux packs de
production · 4 API moteur documentées ici pour la première fois depuis l'usage publié · 2 packs
publiés disséqués jusqu'à la constante · chaque constante citée porte le crédit de son auteur.

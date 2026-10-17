# Partie IV — Nombres mesurés (FR)

Étiquettes : **[mesuré]** (nos pipelines) · **[publié]** (prouvé dans un pack) · **[tierce]**
(restauré du JS de production par la communauté — vérifier avant d'en dépendre).

## Unités de lumière

- skyLight 0-15 (flood-fill) ; **ciel ouvert = 15** ; un niveau perdu sous canopée ≈ **0.995
  après tone-mapping** — la « perte de niveau » est visible, l'échelle n'est pas linéaire.
- **La courbe de tone est saturante** [mesuré] : nos fits de sonde correspondent à une famille
  type `raw = 45·b/(1+2b)` — les niveaux du haut sont comprimés, c'est pourquoi la discrimination
  d'ombre se joue tout en haut de l'échelle.
- **Les ombres de terrain vivent dans skyLight 13.6–14.95 / 15** [mesuré] : toute la bande
  d'ombre du jour = le 1,5 niveau supérieur. Tout test d'ombre sous ≈13,5 est de la logique de
  grotte, pas de soleil.
- skyLight arrive **tone-mappé** aux packs : ciel franc ≥ ≈0.98 ; rejet grotte/nuit < ≈0.45 ;
  niveau perdu de canopée ≈ 0.995 **[publié]**.
- Les couleurs de lumière packées ont un **plancher 35 % par canal** relatif au canal max
  **[tierce]** — un rouge pur arrive (1.0, 0.35, 0) : voilà pourquoi les lampes paraissent roses.
- Propriétés lumineuses des blocs (docs scripting officielles **[tierce-officielle]**):
  `lightEmission` 0-15 et **`lightFilter`** — combien de lumière un bloc retire (1 air / 3
  fluide / 15 opaque). Voilà pourquoi les pièces s'assombrissent et l'eau atténue les dégradés.
- `l.ambient` = material.ambient × sceneAmbient (réglage utilisateur, défaut 0.5). Ne jamais
  coder le défaut en dur **[tierce]**.

## Soleil, lune, ciel

- Mondes défaut : soleil statique ≈ **(−0.56, 0.81, −0.18)** **[tierce]** ; mondes jour/nuit le
  mettent à jour ; **lune = −soleil exactement** ; nuit ⇔ `sun.y < 0`.
- Ciels non-terre (gloomy/interstellar/espace) : `bloxdSunDirection()` = **(0,0,0)** — un facteur
  jour basé sur `sun.y` désactive tout seul tes effets soleil **[publié]**.
- La lumière directionnelle du terrain = 2 lampes figées : **la luminosité du terrain ne suit
  PAS le soleil toute seule** ; le « moment de la journée » est 100 % ton travail.

## Fog

- Rampes **linéaires** : `fogVisibility = (fogEnd−dist)/(fogEnd−fogStart)`, `fogStart = 32×D`,
  `fogEnd = 32×(D+1)` — la bande n'a que **32 blocs** **[tierce]** (notre ancienne note « EXP2 »
  venait du wiki ; priorité à la figure production-JS, à re-vérifier sonde si ton effet en dépend).
- Couleur défaut `rgb(183, 191, 195)` ; overridable par les créateurs de monde ; **mode 0 (NONE)
  → fogColour arrive noir** — d'où `bloxdApplyFog`, sûr à visibilité 1.
- Damier fin aux bords de chunks pendant le chargement = fade Bayer 4×4 du moteur, **pas ton bug**.

## Optique de l'eau (valeurs prouvées)

- Obscurcissement Beer-Lambert `1 − exp(−0.32·d)` (≈⅓ à 1 bloc) **[publié]** ; notre plan P0
  utilisait 0.45/0.08/0.03 par canal — les deux marchent.
- Schlick F0 = 0.02 ; sheen large `0.05·pow(nDotH, 24)·sunUp` **[publié]**.
- Eau enregistrée : couleur (0.5, 0.5, 0.8), alpha 0.9 — reconstruire l'alpha, ne pas coder en dur.

## Grading

- Lift `c·B/(1+c·(B−1))` : pente **B au noir, exactement 1.0 au blanc** — le blanc ne clippe
  jamais. Breeze publie B = 1.45 **[publié]** ; notre pack cinématique cale B par canal sur des
  frames réelles.
- Vibrance avec garde chroma (`1 − chroma`) : les pixels ternes se saturent, les déjà-colorés
  restent intacts.

## Pourquoi mesurer

Tous les packs disséqués règlent à l'œil. Caler ta courbe sur des captures (régression log-log)
prend un après-midi et transforme le « feeling » en reproductible. Voir Partie VI.

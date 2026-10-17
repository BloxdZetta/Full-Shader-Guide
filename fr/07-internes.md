# Partie VII — Internals moteur (FR)

Chaque item porte sa provenance : **[mesuré]** · **[publié]** · **[tierce]** (JS de production
restauré par la communauté — vérifier toute dépendance critique).

## Temps et espace

- `bloxdTime()` = uptime navigateur wrappé à 1 h (`bloxdTimeWrap` = 3600), sans lien avec une
  horloge de jeu **[tierce + usage publié]**.
- **Floating origin** : `bloxdOriginOffset()` rebasse périodiquement les coordonnées monde
  (moteur noa). Tout motif ancré monde doit injecter l'offset dans son hash **[publié]**.
- Le jour/nuit **n'est pas** un changement d'éclairage terrain : 2 lampes directionnelles
  figées à la création de la scène ; seul le ciel et `bloxdSunDirection()` portent le temps
  **[tierce]**.

## Pipeline lumière

- skyLight 0-15 flood-fill ; ciel ouvert = 15 ; **tone-mappé avant les packs** (un niveau perdu
  ≈ 0.995 post-courbe) **[seuils publiés]**.
- Décodage `aPackedLightLevels` : plancher **35 % du canal max** **[tierce]**.
- `heldLight` : portée = canal max, ≤ 15 blocs, distance pré-déformée `^0.75`, valeur
  pré-boost-ambiant **[tierce]**.
- Propriétés lumineuses des blocs (docs scripting officielles **[tierce-officielle]**):
  `lightEmission` 0-15 (alimente le BFS blockLight) et `lightFilter` — 1 air / 3 fluide /
  15 opaque — voilà pourquoi les pièces vont au noir et les fluides atténuent les dégradés.
- `skyLightEmission` (0-15, blocs custom) **injecté dans le canal skyLight lui-même**, hors BFS
  blockLight — les tests soleil/ombre fondés sur skyLight seul peuvent être trompés ; combiner
  avec blockLight **[tierce]**.
- `l.ambient` = material.ambient × sceneAmbient (réglage utilisateur, défaut 0.5) **[tierce]**.

## Surfaces

- Hooks surface **avant alphaTest** : `out.alpha` pilote le discard des cutouts et est le vrai
  facteur de blend des liquides ; sans effet sur l'opaque simple **[tierce]**.
- `out.emission` = sortie du hook surface (ou sommée dans la couleur avant fog) **[publié]**.
- Plantes/fleurs : chemin de rendu **inaccessible aux packs** **[publié]** ; déformation de
  sommets existante mais **certains jeux seulement** **[publié]** → vent « shading only ».
- Fondu de chargement = dither **Bayer 4×4 écran** du moteur **[tierce]**.

## Ids

- Le rendu identifie les blocs par **`blockId : u32` numérique** (Partie VIII) ; le scripting
  utilise des ids string — deux espaces pour les mêmes blocs.
- L'espace d'ids **grandit** : un dump fini à 2089 manque déjà des ids jusqu'à 3254 utilisés par
  un pack publié. Ré-énumérer à chaque release (méthode Partie VIII).

## Ciel

- Mondes défaut : soleil statique ≈ (−0.56, 0.81, −0.18) ; **lune = −soleil** ; ciels sans
  soleil → vecteur nul **[tierce]**.
- Fog : bande linéaire de 32 blocs au bord de chargement ; couleur défaut rgb(183,191,195) ;
  fogColour **noir** en mode NONE **[tierce]**.

## Loader

- Glob `**/*.wgsl` + concaténation ; pas de fichier racine requis ; scope module indépendant de
  l'ordre **[publié]**.
- Cap 256 Ko total ; `apiVersion` v1 rejeté d'office **[tierce]**.

# Part X — The constants register (FR)

## Variables exposées par le moteur (ce que le jeu te donne)

Les identifiants restent en anglais (ce sont les noms réels du code). Signification en contexte
FR dans la Partie II. Valeurs internes clés : wrap temps **3600 s** ; échelle lumière **0-15**,
ciel ouvert = 15 ; courbe de tone ≈ **45·b/(1+2b)** [mesuré] ; bande d'ombre terrain
**13.6-14.95/15** [mesuré] ; plancher des canaux packés **35 %** ; bande de fog **32×D →
32×(D+1)** [tierce, question ouverte] ; couleur fog défaut **rgb(183,191,195)** ; showFog off →
**3200-3328** ; ambient scène défaut **0.5** ; cap loader **256 Ko** ; 2 lampes directionnelles
figées. Détails et provenances : [Partie IV](04-realisme.md) et Partie VII.

## Registre des constantes (packs locaux et packs disséqués)

Généré mécaniquement depuis les sources de ce dépôt (`guide/tools/gen_var_registry.py`) —
valeur exacte du code, rôle par constante (individuel ou par famille), pack d'origine.



## cinematic-v5 (pack local — baseline gelée) — 183 constants

| Constant | Value | Role |
|---|---|---|
| `TR_ALT_HAZE` | 0.15 | brume d'altitude : force du voile au-dessus de 55 blocs |
| `TR_AURORA_WATER` | 0.08 | eau : force de l'aurore nocturne reflétée (dans notre reflet seulement) |
| `TR_BACKLIGHT` | 0.18 | contre-jour : force de la lueur de la végétation dos au soleil |
| `TR_BACKLIGHT_COL` | vec3f(1.0, 0.62, 0.28) | contre-jour : couleur chaude de la lueur |
| `TR_BAT_CHANCE` | 0.12 | chauves-souris : proportion de cellules au crépuscule |
| `TR_BAT_COL` | vec3f(0.10, 0.09, 0.08) | chauves-souris : couleur de la silhouette sombre |
| `TR_BAT_ROAM` | 0.8 | chauves-souris : rayon d'errance saccadée |
| `TR_BAT_SIZE` | 0.09 | chauves-souris : taille du corps |
| `TR_BAT_T_WING` | 9.424778 | chauves-souris : vitesse de battement rapide (verrouillée au wrap) |
| `TR_BFLY_BODY` | 0.012 | papillons : demi-largeur du corps |
| `TR_BFLY_CHANCE` | 0.25 | papillons : proportion de cellules d'air occupées |
| `TR_BFLY_COL1` | vec3f(0.95, 0.93, 0.85) | papillons : variante blanche |
| `TR_BFLY_COL2` | vec3f(0.98, 0.85, 0.30) | papillons : variante jaune |
| `TR_BFLY_COL3` | vec3f(0.90, 0.55, 0.25) | papillons : variante orange |
| `TR_BFLY_GAP` | 0.035 | papillons : demi-séparation des deux ailes |
| `TR_BFLY_ROAM` | 0.4 | papillons : rayon d'errance autour de la cellule |
| `TR_BFLY_SIZE` | 0.05 | papillons : taille du corps |
| `TR_BFLY_TALL` | 1.35 | papillons : ratio de hauteur du disque d'ailes |
| `TR_BFLY_T_WING` | 3.1415927 | papillons : vitesse de battement des ailes (verrouillée au wrap) |
| `TR_BUG_COL` | vec3f(0.72, 0.06, 0.05) | coccinelles : rouge de la carapace |
| `TR_BUG_SHARE` | 0.12 | papillons : part qui sont des coccinelles |
| `TR_CANOPY_HI` | 0.9995 | fenêtre effets d'arbres : skyLight du ciel ouvert (les plaines restent nues) |
| `TR_CANOPY_LO` | 0.90 | fenêtre effets d'arbres : skyLight minimum (les grottes restent nues) |
| `TR_CINEMA_BOOST` | 1.6 | mode cinéma : multiplicateur de brume dorée et contre-jour |
| `TR_CINEMA_MODE` | false | mode cinéma : false = normal, true = atmosphère poussée |
| `TR_EDGE_AO` | 0.92 | force de l'AO d'arête (pondérée skyLight, loi) |
| `TR_EMBER_CHANCE` | 0.18 | lave : proportion de cellules émettant des braises |
| `TR_EMBER_HEIGHT` | 2.2 | lave : hauteur de montée des braises (blocs) |
| `TR_EMBER_SIZE` | 0.03 | lave : taille angulaire d'une braise à 1 bloc |
| `TR_EMBER_T_RISE` | 4.0 | lave : période de montée des braises (doit diviser 3600) |
| `TR_EPSILON` | 0.0001 | garde epsilon générique |
| `TR_FLY_CHANCE` | 0.18 | lucioles : proportion de cellules d'air occupées |
| `TR_FLY_COLOUR` | vec3f(1.0, 0.85, 0.45) | lucioles : couleur de la lueur |
| `TR_FLY_SIZE` | 0.035 | lucioles : rayon du point lumineux |
| `TR_FLY_W_BLINK` | 0.0698132 | lucioles : vitesse angulaire de clignotement (verrouillée au wrap) |
| `TR_FLY_W_BOB` | 0.7853981 | lucioles : vitesse angulaire du flottement (verrouillée au wrap) |
| `TR_GLASS_MIRROR` | 0.30 | verre : force du reflet du ciel (fresnel) |
| `TR_GLASS_RIM` | 0.22 | verre : éclaircissement des bords aux angles rasants |
| `TR_GOLDEN_GAIN` | 0.50 | gain heure dorée |
| `TR_GOLDEN_TINT` | vec3f(1.06, 1.005, 0.90) | teinte heure dorée |
| `TR_GRAIN` | 0.0 | quantité de grain (fondu par distance) |
| `TR_HZN_CLOUD_STR` | 0.45 | force du banc de nuages d'horizon |
| `TR_LAMP_FLICKER` | 0.10 | vacillement lampes : profondeur de modulation (0 = off) |
| `TR_LAMP_SOFT_AO` | 0.55 | adoucissement lampes : AO de bord conservée près des lampes |
| `TR_LAMP_SOFT_GAIN` | 2.5 | adoucissement lampes : gain blockLight → facteur de lavage |
| `TR_LAMP_SOFT_GRAIN` | 0.5 | adoucissement lampes : grain conservé près des lampes |
| `TR_LAVA_FLOW_SCALE` | 0.55 | lave : échelle de la texture de flot visqueux (bien plus lente que l'eau) |
| `TR_LEAF_AUTUMN` | 0.12 | feuilles tombantes : proportion de feuilles teintées automne |
| `TR_LEAF_AUTUMN_GOLD` | vec3f(0.87, 0.60, 0.16) | feuilles tombantes : teinte dorée d'automne |
| `TR_LEAF_AUTUMN_RUST` | vec3f(0.62, 0.28, 0.09) | feuilles tombantes : teinte rouille d'automne |
| `TR_LEAF_BACKLIT` | 0.35 | feuilles tombantes : halo en contre-jour quand le soleil est derrière |
| `TR_LEAF_CELL` | 3.0 | feuilles tombantes : taille des cellules d'air (une feuille max par cellule) |
| `TR_LEAF_CHANCE` | 0.3 | feuilles tombantes : proportion de cellules occupées |
| `TR_LEAF_DRIFT` | 0.06 | feuilles tombantes : dérive sous le vent (direction des nuages) |
| `TR_LEAF_FADE_LO` | 5.0 | feuilles tombantes : distance de début de fondu |
| `TR_LEAF_FALL` | 0.6 | feuilles tombantes : vitesse de chute (= WRAP*CELL/3600 exactement) |
| `TR_LEAF_FLUTTER` | 0.15 | feuilles tombantes : amplitude du flottement vertical |
| `TR_LEAF_GUST` | 0.5 | feuilles tombantes : surcroît de balancement pendant les rafales |
| `TR_LEAF_LEN` | 1.7 | feuilles tombantes : rapport longueur/largeur de la feuille |
| `TR_LEAF_LOD_SHRINK` | 0.45 | feuilles tombantes : rétrécissement au loin |
| `TR_LEAF_ON` | true | interrupteur : feuilles tombantes |
| `TR_LEAF_RANGE` | 10.0 | feuilles tombantes : distance de dessin depuis l'œil |
| `TR_LEAF_RIM` | 0.22 | feuilles tombantes : force du rim-light au centre |
| `TR_LEAF_SIZE` | 0.09 | feuilles tombantes : demi-largeur d'une feuille |
| `TR_LEAF_SIZE_VAR` | 0.30 | feuilles tombantes : variation de taille par feuille (+/-) |
| `TR_LEAF_STEPS` | 6 | feuilles tombantes : échantillons du march de rayon le long de la ligne de vue |
| `TR_LEAF_TIP` | 0.55 | feuilles tombantes : force de la pointe effilée |
| `TR_LEAF_TWOTONE` | 0.18 | feuilles tombantes : variation bicolore par feuille |
| `TR_LEAF_WRAP` | 720 | feuilles tombantes : wrap en y des cellules pour une boucle 3600 s sans saut |
| `TR_LEAF_W_FLIP` | 2.199115 | feuilles tombantes : vitesse angulaire de retournement (verrouillée au wrap) |
| `TR_LEAF_W_GUST` | 0.1047197 | feuilles tombantes : vitesse angulaire du cycle de rafales (verrouillée au wrap) |
| `TR_LEAF_W_SPIN` | 1.600467 | feuilles tombantes : vitesse angulaire de rotation (verrouillée au wrap) |
| `TR_LEAF_W_SWAY_A` | 1.300270 | feuilles tombantes : vitesse angulaire de balancement x (verrouillée au wrap) |
| `TR_LEAF_W_SWAY_B` | 0.900590 | feuilles tombantes : vitesse angulaire de balancement z (verrouillée au wrap) |
| `TR_LITTER_DENS` | 0.82 | litière de feuilles : proportion de cellules laissées nues |
| `TR_LITTER_MIX` | 0.22 | litière de feuilles : force du mélange au sol sous canopée |
| `TR_LITTER_SCALE` | 3.0 | litière de feuilles : cellules de mouchetis par bloc |
| `TR_MIST_GOLDEN` | 0.10 | perspective aérienne / brume |
| `TR_MIST_GOLDEN_COL` | vec3f(0.93, 0.96, 1.0) | perspective aérienne / brume |
| `TR_MIST_GROUND` | 0.12 | brume au sol : force à l'heure dorée |
| `TR_MIST_GROUND_BAND` | 3.5 | brume au sol : bande de hauteur autour de l'œil (blocs) |
| `TR_MIST_GROUND_COL` | vec3f(0.93, 0.96, 1.0) | brume au sol : couleur du voile |
| `TR_MIST_GROUND_HI` | 90.0 | brume au sol : fin du fondu de distance (blocs) |
| `TR_MIST_GROUND_LO` | 16.0 | brume au sol : début du fondu de distance (blocs) |
| `TR_MOONLIGHT` | vec3f(0.30, 0.38, 0.55) | teinte clair de lune |
| `TR_MOON_COLUMN` | 0.10 | eau : force de la colonne de clair de lune sur le fleuve |
| `TR_MOON_GAIN` | 0.30 | gain clair de lune |
| `TR_MOTE_CHANCE` | 0.2 | motes d'air : proportion de cellules occupées (spores de grottes / pollens du jour) |
| `TR_MOTE_COL` | vec3f(0.55, 0.75, 1.0) | motes d'air : couleur des spores de grottes |
| `TR_MOTE_SIZE` | 0.035 | motes d'air : taille angulaire à 1 bloc |
| `TR_POLLEN_COL` | vec3f(1.0, 0.85, 0.45) | motes d'air : couleur des pollens dorés |
| `TR_RELIEF_EPS` | 0.30 | pas epsilon du relief |
| `TR_RELIEF_GAIN` | 1.6 | gain d'éclairage du relief |
| `TR_RELIEF_HEIGHT` | 0.16 | amplitude du champ de hauteur |
| `TR_RELIEF_SCALE` | 1.7 | échelle de hauteur du relief |
| `TR_SCOTO` | 0.5 | force du mix scotopique (vision des bâtonnets) |
| `TR_SKY2_BAND_A` | -0.22 | élévation solaire : nuit complète en dessous |
| `TR_SKY2_BAND_B` | -0.04 | élévation solaire : le crépuscule commence ici |
| `TR_SKY2_BAND_C` | 0.10 | élévation solaire : le jour commence ici |
| `TR_SKY2_BAND_D` | 0.30 | élévation solaire : jour complet au-dessus |
| `TR_SKY2_GLOW_DAWN` | vec3f(1.0, 0.70, 0.38) | couleur du halo solaire à l'aube |
| `TR_SKY2_GLOW_DUSK` | vec3f(1.0, 0.50, 0.26) | couleur du halo solaire au crépuscule |
| `TR_SKY2_GLOW_NIGHT` | vec3f(0.50, 0.62, 0.92) | couleur du halo de lune |
| `TR_SKY2_NIGHT_LOW` | vec3f(0.07, 0.10, 0.20) | couleur d'horizon du ciel de nuit (bleu profond) |
| `TR_SKY2_NIGHT_TOP` | vec3f(0.01, 0.02, 0.06) | couleur zénithale du ciel de nuit |
| `TR_SKY2_TWI_LOW` | vec3f(0.98, 0.62, 0.42) | couleur d'horizon du ciel d'aube/crépuscule (pêche-or) |
| `TR_SKY2_TWI_TOP` | vec3f(0.34, 0.34, 0.62) | couleur zénithale du ciel d'aube/crépuscule (mauve) |
| `TR_SKYF_CURVE` | 1.6 | ciel-brouillard : pente de la courbe d'élévation (prouvée Blocky Day) |
| `TR_SKYF_FOG_MIX` | 0.9 | ciel-brouillard : part de la couleur de brouillard moteur remplacée par le dégradé de ciel |
| `TR_SKYF_GLOW` | 0.55 | ciel-brouillard : force du halo solaire (HORIZON_GLOW de Blocky Day) |
| `TR_SKYF_GLOW_COL` | vec3f(1.00, 0.78, 0.50) | ciel-brouillard : couleur du halo solaire dans le faux ciel |
| `TR_SKYF_HAZE_DESAT` | 0.10 | désaturation grise de la brume aérienne (plus bas = ciel plus bleu) |
| `TR_SKYF_HORIZON_MIX` | 0.85 | ciel-brouillard : fusion de la brume d'horizon dans le faux ciel |
| `TR_SKYF_LOW` | vec3f(0.70, 0.80, 0.96) | ciel-brouillard : couleur d'horizon du faux ciel (prouvée Blocky Day) |
| `TR_SKYF_TOP` | vec3f(0.25, 0.45, 0.85) | ciel-brouillard : couleur zénithale du faux ciel (prouvée Blocky Day) |
| `TR_SOFTEN_AMOUNT` | 0.0 | force du lissage du speckle des faces (anti-séparations) |
| `TR_SOFTEN_GRAIN_NEAR` | 14.0 | distance d'arrêt de la couche de grain fin |
| `TR_SOFTEN_LEVEL` | 0.5 | luminance cible des faces lissées |
| `TR_SOFTEN_MIST` | 0.0 | force des taches nuageuses douces sur les faces |
| `TR_SOFTEN_MIST_FAR` | 48.0 | distance de disparition des taches |
| `TR_SOFTEN_MIST_SIZE` | 5.0 | fréquence des taches par bloc |
| `TR_SPLASH_BRIGHT` | 1.6 | lave : éclat des gouttes |
| `TR_SPLASH_CHANCE` | 0.35 | lave : proportion de cellules avec source d'éclaboussure active |
| `TR_SPLASH_COL` | vec3f(1.0, 0.55, 0.15) | lave : couleur des gouttes |
| `TR_SPLASH_HEIGHT` | 0.45 | lave : hauteur d'apogée des gouttes |
| `TR_SPLASH_SIZE` | 0.045 | lave : taille angulaire d'une goutte à 1 bloc |
| `TR_SPLASH_TRAIL` | 0.05 | lave : espacement de la traînée derrière la goutte (fraction de cycle) |
| `TR_SPLASH_T_RISE` | 3.0 | lave : période montée-descente (doit diviser 3600) |
| `TR_SWAY_FLOWER_HI` | 163u | fin de la plage d'ids des fleurs (gate de sway) |
| `TR_SWAY_FLOWER_LO` | 151u | début de la plage d'ids des fleurs (gate de sway) |
| `TR_SWAY_VINE_W` | 0.5 | poids de sway des vignes (id 219) |
| `TR_VIBRANCE` | 0.16 | grade pré-fog (lift + vibrance à garde chroma) |
| `TR_WATER_CLARITY` | 0.82 | clarté de l'eau |
| `TR_WATER_DAY_TINT` | vec3f(0.34, 0.78, 0.82) | teinte d'eau, bande jour |
| `TR_WATER_DUSK_TINT` | vec3f(0.20, 0.48, 0.66) | teinte d'eau, bande crépuscule |
| `TR_WATER_GLINT` | 0.82 | force du scintillement solaire |
| `TR_WATER_MIRROR_CAP` | 1.05 | optique de l'eau |
| `TR_WATER_MIRROR_CHROMA` | 0.80 | optique de l'eau |
| `TR_WATER_MIRROR_PRESS` | 1.60 | optique de l'eau |
| `TR_WATER_MOON_GLINT` | vec3f(0.48, 0.66, 0.88) | optique de l'eau |
| `TR_WATER_NIGHT_TINT` | vec3f(0.075, 0.19, 0.34) | teinte d'eau, bande nuit |
| `TR_WATER_REFLECTIVITY` | 0.78 | réflectivité de l'eau |
| `TR_WATER_RIPPLE` | 0.105 | amplitude des rides |
| `TR_WATER_TINT` | 0.48 | force du mix de teinte d'eau |
| `TR_WAVE_OMEGA_A` | 0.502655 | fréquence angulaire bande A (gel R17) |
| `TR_WAVE_OMEGA_B` | 0.726057 | fréquence angulaire bande B (gel R17) |
| `TR_WAVE_OMEGA_C` | 0.949459 | fréquence angulaire bande C (gel R17) |
| `TR_WAVE_OMEGA_D` | 1.605703 | fréquence angulaire bande D (gel R17) |
| `TR_WAVE_OMEGA_E` | 1.982694 | fréquence angulaire bande E (gel R17) |
| `TR_WAVE_OMEGA_F` | 2.415536 | fréquence angulaire bande F (gel R17) |
| `TR_WAVE_SWELL_AMP` | 0.15 | eau : amplitude de la houle longue dans la normale |
| `TR_WAVE_SWELL_FOAM` | 0.20 | eau : force de l'écume sur les crêtes de houle |
| `TR_WAVE_SWELL_SCALE` | 0.10 | eau : fréquence spatiale de la houle (radians par bloc) |
| `bloom_spill` | 0.5 | quantité de diffusion bloom |
| `cloud_height` | 100.0 | altitude de la couche nuages cv5 |
| `cloud_scale` | 0.006 | échelle du bruit nuages cv5 |
| `cloud_speed` | vec2f(1.2, 0.7) | vitesse de dérive des nuages cv5 |
| `cloud_strength` | 0.3 | force de la couche nuages 2D cv5 |
| `grade_contrast` | 0.16 | contraste final |
| `grade_saturation` | 1.2 | multiplicateur de saturation final |
| `grass_id` | 150u | l'id du bloc PLANTE herbe (gate de sway par bloc) |
| `haze_base_height` | 40.0 | altitude de référence du brouillard |
| `haze_density` | 0.006 | densité du brouillard de hauteur |
| `haze_height_falloff` | 0.012 | décroissance du brouillard avec l'altitude |
| `haze_strength` | 0.48 | force du brouillard de hauteur |
| `hot_glow_strength` | 0.2 | lueur des émetteurs chauds |
| `leaf_glow` | 0.6 | lueur de translucence des feuilles |
| `luma` | vec3f(0.299, 0.587, 0.114) | poids de luminance Rec.709 |
| `ray_sky_max` | 0.90 | porte d'exposition ciel des god-rays (haut) |
| `ray_sky_min` | 0.60 | porte d'exposition ciel des god-rays (bas) |
| `ray_strength` | 0.3 | force des god-rays |
| `shadow_ambient_drop` | 0.55 | perte ambiante dans l'ombre |
| `shadow_softness` | 0.04 | douceur du bord d'ombre |
| `shadow_strength` | 0.85 | force des ombres directionnelles |
| `shadow_threshold` | 0.95 | seuil skyLight de déclenchement des ombres |
| `shadow_tint` | vec3f(0.62, 0.74, 1.0) | teinte froide des ombres |
| `sun_fallback` | vec3f(0.42, 0.85, 0.0) | teinte soleil de repli |
| `sway_amount` | 0.3 | amplitude du sway |
| `sway_mode` | 2 | sélecteur d'implémentation du sway ; 2 = couleur seule (partout) |
| `sway_speed` | 1.0 | multiplicateur de temps du sway |
| `tall_grass_id` | 1109u | l'id de la plante Tall Grass (même gate) |
| `tall_grass_top_id` | 1110u | id du bloc moitié haute de Tall Grass (gate de sway) |
| `underwater_strength` | 0.30 | force de l'étalonnage sous-marin |

## titan-bsl-ultra-v2 (pack local — vitrine ciel/nuages/eau) — 288 constants

| Constant | Value | Role |
|---|---|---|
| `TR_AERIAL_DESAT` | 0.55 | perspective aérienne / brume |
| `TR_AERIAL_SCALE` | 46.0 | perspective aérienne / brume |
| `TR_AERIAL_SLANT` | 1.35 | perspective aérienne / brume |
| `TR_AERIAL_STRENGTH` | 0.22 | perspective aérienne / brume |
| `TR_AIR_SCATTER` | 0.055 | perspective aérienne / brume |
| `TR_AMBIENT_HUE_AMOUNT` | 0.45 | façonnage de teinte ambiante/rebond |
| `TR_AO_EDGE_MIN` | 0.10 | système d'AO (pondéré skyLight) |
| `TR_AO_EDGE_SOFT` | 2.60 | système d'AO (pondéré skyLight) |
| `TR_AO_LEVEL_HIGH` | 14.60 | système d'AO (pondéré skyLight) |
| `TR_AO_LEVEL_LOW` | 3.00 | système d'AO (pondéré skyLight) |
| `TR_AO_SHADE_FLOOR` | 0.34 | système d'AO (pondéré skyLight) |
| `TR_AURORA_A` | vec3f(0.22, 0.95, 0.55) | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_AURORA_B` | vec3f(0.85, 0.30, 0.95) | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_AURORA_GAIN` | 0.34 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_AURORA_HIGH` | 0.62 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_AURORA_LOW` | 0.06 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_BACKLIGHT` | 0.30 | contre-jour : force de la lueur de la végétation dos au soleil |
| `TR_BLOCK_AMBIENT` | 0.55 | réponse ambiante & rugosité à la lumière de bloc |
| `TR_BLOCK_ROUGH_SPREAD` | 0.06 | réponse ambiante & rugosité à la lumière de bloc |
| `TR_BLOCK_VARIATION` | 0.018 | variation de luminosité par bloc / cellule |
| `TR_BOUNCE_AMBIENT_HUE` | vec3f(1.05, 0.99, 0.925) | façonnage de teinte ambiante/rebond |
| `TR_BUMP_STRENGTH` | 0.85 | micro-détail & normales du terrain |
| `TR_CANOPY_DAPPLE` | 0.55 | ombre de canopée (niveau skyLight perdu) |
| `TR_CANOPY_OPEN_HI` | 0.85 | ombre de canopée (niveau skyLight perdu) |
| `TR_CANOPY_OPEN_LO` | 0.35 | ombre de canopée (niveau skyLight perdu) |
| `TR_CANOPY_SCALE` | 0.36 | ombre de canopée (niveau skyLight perdu) |
| `TR_CANOPY_SWIRL` | 0.351111 | ombre de canopée (niveau skyLight perdu) |
| `TR_CAUSTIC_COLOUR` | vec3f(0.62, 0.94, 0.86) | caustiques de l'eau sur le sol inondé |
| `TR_CAUSTIC_DISP_B` | 0.80 | caustiques de l'eau sur le sol inondé |
| `TR_CAUSTIC_DISP_R` | 1.25 | caustiques de l'eau sur le sol inondé |
| `TR_CAUSTIC_FALLOFF` | 0.22 | caustiques de l'eau sur le sol inondé |
| `TR_CAUSTIC_FAST` | 0.30 | caustiques de l'eau sur le sol inondé |
| `TR_CAUSTIC_SCALE` | 0.22 | caustiques de l'eau sur le sol inondé |
| `TR_CAUSTIC_SPIN` | 0.508889 | caustiques de l'eau sur le sol inondé |
| `TR_CIRRUS_DENSITY` | 0.62 | couche cirrus |
| `TR_CIRRUS_GAIN` | 0.30 | couche cirrus |
| `TR_CIRRUS_HEIGHT` | 420.0 | couche cirrus |
| `TR_CIRRUS_SCALE` | 0.0022 | couche cirrus |
| `TR_CLOUD_AMBIENT_DIM` | 0.22 | atténuation ambiante sous l'ombre des nuages |
| `TR_CLOUD_BOTTOM_COLOUR` | vec3f(0.40, 0.45, 0.58) | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_COVERAGE` | 0.46 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_FILL` | vec3f(0.26, 0.33, 0.46) | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_HEIGHT` | 190.0 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_MIN_SUN` | 0.06 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_OPACITY` | 0.88 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_POWDER` | 1.60 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_POWDER_GAIN` | 0.35 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_RAY_MAX` | 6000.0 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_SCALE` | 0.0086 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_SELF_SHADOW` | 0.70 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_SHADOW_DRIFT` | 0.022222 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_SHADOW_GAPS` | 0.85 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_SHADOW_SCALE` | 0.026 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_SHADOW_STEP` | 34.0 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_SHADOW_STRENGTH` | 0.62 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_SILVER` | 0.45 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_SOFTNESS` | 0.16 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_SPEED` | 0.55 | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_TOP_COLOUR` | vec3f(1.00, 0.99, 0.96) | nuages volumétriques (marching & éclairage) |
| `TR_CLOUD_WIND` | vec2f(0.82, 0.57) | nuages volumétriques (marching & éclairage) |
| `TR_CLUMP_SCALE` | 0.034 | agglomération du feuillage |
| `TR_CLUMP_STRENGTH` | 1.00 | agglomération du feuillage |
| `TR_CLUMP_TINT` | 0.55 | agglomération du feuillage |
| `TR_DEBUG_MODE` | 0 | sélecteur de visualisation debug (0 = off) |
| `TR_DETAIL_FAR` | 0.45 | dither & fondus de détail LOD |
| `TR_DETAIL_NEAR` | 0.06 | dither & fondus de détail LOD |
| `TR_DITHER` | 0.0035 | dither & fondus de détail LOD |
| `TR_DIVE_MIRROR` | vec3f(0.020, 0.110, 0.150) | force du miroir sous-marin |
| `TR_EDGE_CREASE` | 0.26 | micro-détail & normales du terrain |
| `TR_EDGE_WIDTH` | 0.18 | micro-détail & normales du terrain |
| `TR_EMISSION_AMBER_HI` | 0.50 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_AMBER_LO` | 0.30 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_BRIGHT` | 0.88 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_DARK_LO` | 0.38 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_DIM` | 0.58 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_FIERY_HI` | 0.85 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_FIERY_LO` | 0.65 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_GOLD_HI` | 2.20 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_GOLD_LO` | 1.40 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_SAT_HI` | 0.80 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_SAT_LO` | 0.30 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_SELF_LIGHT` | 0.45 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_STRENGTH` | 1.25 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_UNCONFIRMED` | 0.15 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_WARM_HI` | 1.62 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EMISSION_WARM_LO` | 1.16 | système des blocs émissifs (gates torch/lamp/or/ambre/feu) |
| `TR_EPSILON` | 0.000001 | garde epsilon générique |
| `TR_EXPOSURE` | 0.96 | tone mapping & grade |
| `TR_F0_DIELECTRIC` | 0.04 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_FACE_CONTRAST` | 0.30 | phases de variation par face |
| `TR_FACE_PHASE_A` | 0.6180339887 | phases de variation par face |
| `TR_FACE_PHASE_B` | 0.7548776662 | phases de variation par face |
| `TR_FIRE_FLICKER` | 0.16 | animation scintillement du feu |
| `TR_FIRE_PHASE` | 41.0 | animation scintillement du feu |
| `TR_FOLIAGE_NORMAL_HIGH` | 0.85 | normales animées du feuillage |
| `TR_FOLIAGE_NORMAL_LOW` | 0.25 | normales animées du feuillage |
| `TR_GLARE_DESAT` | 0.70 | façonnage de l'éblouissement |
| `TR_GLARE_FULL` | 1.05 | façonnage de l'éblouissement |
| `TR_GLARE_KNEE` | 0.55 | façonnage de l'éblouissement |
| `TR_GRADE_CONTRAST` | 0.45 | tone mapping & grade |
| `TR_GRADE_FILMIC` | 0.45 | tone mapping & grade |
| `TR_GRADE_HIGHLIGHT_DESAT` | 0.25 | tone mapping & grade |
| `TR_GRADE_NIGHT` | vec3f(0.60, 0.80, 1.14) | tone mapping & grade |
| `TR_GRADE_NIGHT_MIX` | 0.45 | tone mapping & grade |
| `TR_GRADE_SATURATION` | 1.10 | tone mapping & grade |
| `TR_GRADE_SHADOW_RANGE` | 0.38 | tone mapping & grade |
| `TR_GRADE_SHADOW_TINT` | vec3f(0.93, 0.975, 1.08) | tone mapping & grade |
| `TR_GRADE_VIBRANCE` | 0.38 | grade pré-fog (lift + vibrance à garde chroma) |
| `TR_GRASS_GLINT_F0` | 0.045 | scintillement spéculaire de l'herbe |
| `TR_GRASS_GLINT_GAIN` | 0.55 | scintillement spéculaire de l'herbe |
| `TR_GRASS_GLINT_ROUGH` | 0.40 | scintillement spéculaire de l'herbe |
| `TR_GUST_BREATHE` | 0.675556 | champ de rafales |
| `TR_GUST_SCALE` | 0.020 | champ de rafales |
| `TR_GUST_SHADE` | 0.26 | champ de rafales |
| `TR_GUST_SPEED` | 1.500000 | champ de rafales |
| `TR_LAMP_WOBBLE` | 0.05 | vacillement des lampes |
| `TR_LEAF_NORMAL_FLUTTER` | 1.240000 | normales animées du feuillage |
| `TR_LEAF_NORMAL_RATE` | 0.42 | normales animées du feuillage |
| `TR_LEAF_NORMAL_STRENGTH` | 0.60 | normales animées du feuillage |
| `TR_LEAF_NORMAL_TIME` | 0.413333 | normales animées du feuillage |
| `TR_LOCAL_KEEP` | 0.85 | cadre d'éclairage (keep/unlit/nuit/abri) |
| `TR_LOOP_CELLS` | 8.0 | verrou de wrap (temps/précision) |
| `TR_LOOP_SECONDS` | 3600.0 | verrou de wrap (temps/précision) |
| `TR_MAGMA_CORE` | vec3f(1.000, 0.800, 0.300) | matériau magma/lave & LOD |
| `TR_MAGMA_CRUST` | vec3f(0.030, 0.006, 0.001) | matériau magma/lave & LOD |
| `TR_MAGMA_GAIN` | 1.30 | matériau magma/lave & LOD |
| `TR_MAGMA_HOT` | vec3f(1.000, 0.250, 0.030) | matériau magma/lave & LOD |
| `TR_MAGMA_LOD_FAR` | 80.0 | matériau magma/lave & LOD |
| `TR_MAGMA_LOD_NEAR` | 12.0 | matériau magma/lave & LOD |
| `TR_MAGMA_SCALE` | 0.30 | matériau magma/lave & LOD |
| `TR_MAGMA_WARP` | 4.00 | matériau magma/lave & LOD |
| `TR_MAT_GRASS_F0` | 0.042 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_GRASS_ROUGH` | 0.90 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_MOSS_F0` | 0.035 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_MOSS_ROUGH` | 0.92 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_SAND_F0` | 0.045 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_SAND_ROUGH` | 0.94 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_SHEEN` | 0.032 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_SHEEN_POWER` | 3.0 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_SNOW_F0` | 0.030 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_SNOW_ROUGH` | 0.72 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_STONE_F0` | 0.040 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_STONE_ROUGH` | 0.92 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_WET_F0` | 0.055 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_MAT_WET_ROUGH` | 0.24 | set matériaux PBR (F0/rugosité/sheen GGX) |
| `TR_METEOR_GAIN` | 1.60 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_METEOR_PERIOD` | 48.0 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_METEOR_TRAIL` | 90.0 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_MICRO_DETAIL_SCALE` | 1.35 | micro-détail & normales du terrain |
| `TR_MICRO_DETAIL_STRENGTH` | 0.20 | micro-détail & normales du terrain |
| `TR_MICRO_ROUGHNESS` | 0.14 | micro-détail & normales du terrain |
| `TR_MIE_OPEN_HI` | 0.80 | perspective aérienne / brume |
| `TR_MIE_OPEN_LO` | 0.30 | perspective aérienne / brume |
| `TR_MIE_STRENGTH` | 0.22 | perspective aérienne / brume |
| `TR_MIST_BASE` | 56.0 | perspective aérienne / brume |
| `TR_MIST_SCALE` | 9.0 | perspective aérienne / brume |
| `TR_MIST_STRENGTH` | 0.10 | perspective aérienne / brume |
| `TR_MIST_SUN` | 0.30 | perspective aérienne / brume |
| `TR_MOON_COLOUR` | vec3f(0.62, 0.72, 1.00) | système ambiant nuit/lune |
| `TR_MOON_DIFFUSE` | 0.30 | système ambiant nuit/lune |
| `TR_MOON_DISC_GAIN` | 4.20 | rendu disque & anneau lunaires |
| `TR_MOON_DISC_HI` | 0.99975 | rendu disque & anneau lunaires |
| `TR_MOON_DISC_LO` | 0.99920 | rendu disque & anneau lunaires |
| `TR_MOON_OPEN_HI` | 0.70 | système ambiant nuit/lune |
| `TR_MOON_OPEN_LO` | 0.25 | système ambiant nuit/lune |
| `TR_MOON_REDDEN` | 0.80 | système ambiant nuit/lune |
| `TR_MOON_RING_GAIN` | 0.32 | rendu disque & anneau lunaires |
| `TR_MOON_RING_HI` | 0.99920 | rendu disque & anneau lunaires |
| `TR_MOON_RING_LO` | 0.99780 | rendu disque & anneau lunaires |
| `TR_MW_GAIN` | 0.10 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_MW_SCALE` | 2.60 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_MW_TILT` | vec3f(0.42, 0.86, -0.28) | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_NIGHT_AMBIENT` | 0.46 | système ambiant nuit/lune |
| `TR_NIGHT_AMBIENT_LIFT` | 1.00 | système ambiant nuit/lune |
| `TR_NIGHT_DIM` | 0.92 | cadre d'éclairage (keep/unlit/nuit/abri) |
| `TR_NOISE_ORIGIN` | vec2f(31.7, 71.3) | sel d'origine du hash |
| `TR_NOISE_WRAP` | 256.0 | plomberie maths/bruit |
| `TR_NOISE_WRAP_INV` | 0.00390625 | plomberie maths/bruit |
| `TR_ORE_GLOW` | 0.22 | étincelle & boost spéculaire des minerais |
| `TR_ORE_ROUGHNESS_DROP` | 0.12 | étincelle & boost spéculaire des minerais |
| `TR_ORE_SPEC_BOOST` | 0.35 | étincelle & boost spéculaire des minerais |
| `TR_PI` | 3.14159265359 | plomberie maths/bruit |
| `TR_PLANT_ROOT` | 0.10 | tolérance de détection des plantes |
| `TR_PLANT_TOL` | 0.045 | tolérance de détection des plantes |
| `TR_RELIEF_SHADE` | 0.45 | ombrage du relief |
| `TR_RELIEF_SIGN` | 1.0 | ombrage du relief |
| `TR_RELIEF_STRENGTH` | 0.55 | ombrage du relief |
| `TR_SAND_RIPPLE_AMP` | 0.18 | rides de sable |
| `TR_SAND_RIPPLE_FREQ` | 5.80 | rides de sable |
| `TR_SAND_RIPPLE_WANDER` | 0.14 | rides de sable |
| `TR_SHADE_DUSK` | vec3f(0.58, 0.58, 0.88) | façonnage des ombres (seuils, crépuscule, teinte froide) |
| `TR_SHADE_SKY` | vec3f(0.84, 0.89, 0.98) | façonnage des ombres (seuils, crépuscule, teinte froide) |
| `TR_SHADOW_DUSK_SOFT` | 0.03 | façonnage des ombres (seuils, crépuscule, teinte froide) |
| `TR_SHADOW_DUSK_WIDEN` | 0.05 | façonnage des ombres (seuils, crépuscule, teinte froide) |
| `TR_SHADOW_SOFTNESS` | 0.040 | façonnage des ombres (seuils, crépuscule, teinte froide) |
| `TR_SHADOW_SUN_FLOOR` | 0.10 | façonnage des ombres (seuils, crépuscule, teinte froide) |
| `TR_SHADOW_THRESHOLD` | 0.95 | façonnage des ombres (seuils, crépuscule, teinte froide) |
| `TR_SHADOW_TINT_COOL` | 0.50 | façonnage des ombres (seuils, crépuscule, teinte froide) |
| `TR_SHELTER_SINK` | 0.26 | cadre d'éclairage (keep/unlit/nuit/abri) |
| `TR_SHOULDER` | 0.80 | tone mapping & grade |
| `TR_SHOULDER_KNEE` | 0.66 | tone mapping & grade |
| `TR_SKYSPEC_ROUGH_HIGH` | 0.75 | spéculaire du ciel sur l'eau |
| `TR_SKYSPEC_ROUGH_LOW` | 0.35 | spéculaire du ciel sur l'eau |
| `TR_SKYSPEC_STRENGTH` | 0.18 | spéculaire du ciel sur l'eau |
| `TR_SKY_AMBIENT_HUE` | vec3f(0.90, 0.965, 1.07) | gradient de ciel (zénith/horizon/crépuscule) |
| `TR_SKY_DUSK` | vec3f(1.00, 0.45, 0.20) | gradient de ciel (zénith/horizon/crépuscule) |
| `TR_SKY_DUSK_FADE` | 7.0 | gradient de ciel (zénith/horizon/crépuscule) |
| `TR_SKY_DUSK_GAIN` | 0.90 | gradient de ciel (zénith/horizon/crépuscule) |
| `TR_SKY_DUSK_POW` | 3.0 | gradient de ciel (zénith/horizon/crépuscule) |
| `TR_SKY_HAZE_GAIN` | 0.42 | gradient de ciel (zénith/horizon/crépuscule) |
| `TR_SKY_HORIZON` | vec3f(0.66, 0.79, 0.93) | gradient de ciel (zénith/horizon/crépuscule) |
| `TR_SKY_ZENITH` | vec3f(0.16, 0.36, 0.80) | gradient de ciel (zénith/horizon/crépuscule) |
| `TR_SKY_ZENITH_POW` | 0.45 | gradient de ciel (zénith/horizon/crépuscule) |
| `TR_SNELL_HI` | 0.72 | fenêtre de Snell sous l'eau |
| `TR_SNELL_LO` | 0.58 | fenêtre de Snell sous l'eau |
| `TR_SNELL_SKY` | 0.85 | fenêtre de Snell sous l'eau |
| `TR_SNELL_SUN` | 2.20 | fenêtre de Snell sous l'eau |
| `TR_SPARKLE_DENSITY` | 0.10 | scintillements de l'eau |
| `TR_SPARKLE_SCALE` | 1.30 | scintillements de l'eau |
| `TR_SPARKLE_STRENGTH` | 0.26 | scintillements de l'eau |
| `TR_SPEC_AA` | 0.10 | système spéculaire & anti-aliasing |
| `TR_SPEC_STRENGTH` | 0.55 | système spéculaire & anti-aliasing |
| `TR_SSS_BIAS` | 0.85 | SSS sur le feuillage |
| `TR_SSS_FLOOR` | 0.18 | SSS sur le feuillage |
| `TR_SSS_STRENGTH` | 0.42 | SSS sur le feuillage |
| `TR_STAR_DENSITY` | 0.0022 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_STAR_GAIN` | 1.30 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_STAR_SCALE` | 190.0 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_STAR_TWINKLE` | 0.35 | traits du ciel nocturne (étoiles/voie lactée/aurores/météores) |
| `TR_SUNSET_BAND` | 0.30 | réponse soleil/crépuscule |
| `TR_SUN_AIRMASS` | 0.26 | rougissement airmass du soleil (modèle ciel) |
| `TR_SUN_AIRMASS_MAX` | 9.00 | rougissement airmass du soleil (modèle ciel) |
| `TR_SUN_AIRMASS_NORM` | 1.16413 | rougissement airmass du soleil (modèle ciel) |
| `TR_SUN_AIR_RGB` | vec3f(0.34, 0.62, 1.00) | rougissement airmass du soleil (modèle ciel) |
| `TR_SUN_BUDGET_GAIN` | 0.20 | réponse soleil/crépuscule |
| `TR_SUN_DIRECTION_BLEND` | 0.60 | réponse soleil/crépuscule |
| `TR_SUN_DISC_GAIN` | 26.0 | rendu disque & halo solaire |
| `TR_SUN_DISC_HI` | 0.99970 | rendu disque & halo solaire |
| `TR_SUN_DISC_LO` | 0.99880 | rendu disque & halo solaire |
| `TR_SUN_GLOW_GAIN` | 0.90 | rendu disque & halo solaire |
| `TR_SUN_GLOW_HI` | 0.9992 | rendu disque & halo solaire |
| `TR_SUN_GLOW_LO` | 0.9920 | rendu disque & halo solaire |
| `TR_SUN_HUE` | vec3f(1.00, 0.98, 0.95) | rougissement airmass du soleil (modèle ciel) |
| `TR_SUN_REDDEN` | 0.85 | rougissement airmass du soleil (modèle ciel) |
| `TR_SUN_STRENGTH` | 0.85 | réponse soleil/crépuscule |
| `TR_SWAY_ANGLE` | 0.55 | angle max de sway |
| `TR_TAU` | 6.28318530718 | plomberie maths/bruit |
| `TR_TERRAIN_ROUGHNESS` | 1.05 | micro-détail & normales du terrain |
| `TR_TONEMAP_STRENGTH` | 1.0 | tone mapping & grade |
| `TR_TORCH_PIERCE_GAIN` | 1.40 | teinte chaude des torches & percée |
| `TR_TORCH_PIERCE_TINT` | 0.60 | teinte chaude des torches & percée |
| `TR_TORCH_WARM_TINT` | vec3f(1.10, 0.86, 0.62) | teinte chaude des torches & percée |
| `TR_UNDERWATER_ABSORB` | vec3f(0.32, 0.055, 0.022) | étalonnage sous-marin caméra immergée |
| `TR_UNDERWATER_BLUE_HI` | 0.30 | étalonnage sous-marin caméra immergée |
| `TR_UNDERWATER_BLUE_LO` | 0.10 | étalonnage sous-marin caméra immergée |
| `TR_UNDERWATER_CAUSTIC` | 0.55 | étalonnage sous-marin caméra immergée |
| `TR_UNDERWATER_DEEP` | vec3f(0.020, 0.130, 0.190) | étalonnage sous-marin caméra immergée |
| `TR_UNDERWATER_RATIO` | 1.333 | étalonnage sous-marin caméra immergée |
| `TR_UNDERWATER_RATIO_HI` | 2.80 | étalonnage sous-marin caméra immergée |
| `TR_UNDERWATER_RATIO_LO` | 2.00 | étalonnage sous-marin caméra immergée |
| `TR_UNDERWATER_STRENGTH` | 0.85 | étalonnage sous-marin caméra immergée |
| `TR_UNLIT_GAIN` | 1.0 | cadre d'éclairage (keep/unlit/nuit/abri) |
| `TR_VERTEX_GUST` | 0.45 | hooks de déplacement de sommets (peu de jeux) |
| `TR_VERTEX_LIFT` | 0.35 | hooks de déplacement de sommets (peu de jeux) |
| `TR_VERTEX_ROOT` | 0.15 | hooks de déplacement de sommets (peu de jeux) |
| `TR_VERTEX_SWAY` | 0.140 | hooks de déplacement de sommets (peu de jeux) |
| `TR_WATER_CLARITY` | 0.82 | clarté de l'eau |
| `TR_WATER_DAY_TINT` | vec3f(0.34, 0.78, 0.82) | teinte d'eau, bande jour |
| `TR_WATER_DUSK_TINT` | vec3f(0.20, 0.48, 0.66) | teinte d'eau, bande crépuscule |
| `TR_WATER_GLINT` | 0.82 | force du scintillement solaire |
| `TR_WATER_MIRROR_CAP` | 1.05 | optique de l'eau |
| `TR_WATER_MIRROR_CHROMA` | 0.80 | optique de l'eau |
| `TR_WATER_MIRROR_PRESS` | 1.60 | optique de l'eau |
| `TR_WATER_MOON_GLINT` | vec3f(0.48, 0.66, 0.88) | optique de l'eau |
| `TR_WATER_NIGHT_TINT` | vec3f(0.075, 0.19, 0.34) | teinte d'eau, bande nuit |
| `TR_WATER_REFLECTIVITY` | 0.78 | réflectivité de l'eau |
| `TR_WATER_RIPPLE` | 0.105 | amplitude des rides |
| `TR_WATER_TINT` | 0.48 | force du mix de teinte d'eau |
| `TR_WAVE_OMEGA_A` | 0.502655 | fréquence angulaire bande A (gel R17) |
| `TR_WAVE_OMEGA_B` | 0.726057 | fréquence angulaire bande B (gel R17) |
| `TR_WAVE_OMEGA_C` | 0.949459 | fréquence angulaire bande C (gel R17) |
| `TR_WAVE_OMEGA_D` | 1.605703 | fréquence angulaire bande D (gel R17) |
| `TR_WAVE_OMEGA_E` | 1.982694 | fréquence angulaire bande E (gel R17) |
| `TR_WAVE_OMEGA_F` | 2.415536 | fréquence angulaire bande F (gel R17) |
| `TR_WIND_FIELD_BASE` | 0.5 | champ de vent pour le feuillage |
| `TR_WIND_FIELD_SCALE` | 0.012 | champ de vent pour le feuillage |
| `TR_WIND_FIELD_SPEED` | 0.551111 | champ de vent pour le feuillage |
| `TR_WIND_SPEED_STEP` | 0.013889 | réglages maîtres du vent |

## PROBE-DIAG-v2 (sonde de mesure, modes 0-15) — 19 constants

| Constant | Value | Role |
|---|---|---|
| `MODE_0_SKYLIGHT_RAW` | 0 | sonde mode 0 — skyLight brut sur tous les canaux |
| `MODE_10_DIRECTIONAL_GRAY` | 10 | sonde mode 10 — lumière directionnelle terrain en gris |
| `MODE_11_DEPTH_DEFINE` | 11 | sonde mode 11 — BLOXD_SCENE_DEPTH actif ? (vert/rouge) |
| `MODE_12_DEPTH_FOUND` | 12 | sonde mode 12 — behind.found (vert/rouge) |
| `MODE_13_DEPTH_PATH_BANDS` | 13 | sonde mode 13 — bandes d'épaisseur d'eau (path) |
| `MODE_14_DEPTH_VERTICAL_BANDS` | 14 | sonde mode 14 — bandes de profondeur verticale |
| `MODE_15_DEPTH_BED_ANCHOR` | 15 | sonde mode 15 — ancrage au lit (fract bed.y) |
| `MODE_1_SKY_LEVEL_0_15` | 1 | sonde mode 1 — skyLight remis à l'échelle 0-15 |
| `MODE_2_BLOCKLIGHT_RGB` | 2 | sonde mode 2 — blockLight RGB en couleur |
| `MODE_3_HELDLIGHT_RGB_X4` | 3 | sonde mode 3 — heldLight ×4 (visibilité) |
| `MODE_4_SKYLIGHTCOLOUR_NORM` | 4 | sonde mode 4 — skyLightColour normalisée |
| `MODE_5_AMBIENTCOLOUR_NORM` | 5 | sonde mode 5 — couleur ambiante normalisée |
| `MODE_6_FOGVISIBILITY_GRAY` | 6 | sonde mode 6 — fogVisibility en gris |
| `MODE_7_FOGCOLOUR_RAW` | 7 | sonde mode 7 — fogColour brut (révèle le noir en mode NONE) |
| `MODE_8_SUNDIRECTION_RGB` | 8 | sonde mode 8 — direction soleil en RGB |
| `MODE_9_SUNLENGTH_GRAY` | 9 | sonde mode 9 — |sunDir| en gris (0 sans soleil) |
| `MODE_SECONDS` | 60.0 | secondes par mode avant rotation |
| `PROBE_MODE` | -1 | sélecteur de canal sonde ; >=0 fige un mode de mesure |
| `TR_EPS` | 0.0001 | epsilon de la sonde |

## Breeze v1 (pack publié disséqué — Crownix d'après Ellie) — 61 constants

| Constant | Value | Role |
|---|---|---|
| `BLOCK_VARIATION` | 0.04 | variation de luminosité par bloc / cellule |
| `BRIGHTEN` | 1.45 | grade pré-fog (lift + vibrance à garde chroma) |
| `CANOPY_SPREAD` | 0.0035 | ombre de canopée (niveau skyLight perdu) |
| `CANOPY_STRENGTH` | 1.0 | ombre de canopée (niveau skyLight perdu) |
| `CANOPY_TINT` | vec3f(0.5, 0.56, 0.7) | ombre de canopée (niveau skyLight perdu) |
| `CELLS_PER_BLOCK` | 8 | plomberie du réseau de cellules |
| `CELL_FAR` | 40.0 | variation de luminosité par bloc / cellule |
| `CELL_VARIATION` | 0.06 | variation de luminosité par bloc / cellule |
| `COARSE_SHIFT` | vec2i(117, 44) | octaves de vagues sur réseau entier tourné & LOD |
| `COARSE_STRIDE` | 2000 | octaves de vagues sur réseau entier tourné & LOD |
| `CREST_GAIN` | 0.02 | éclairage des crêtes |
| `DEEP_OPACITY` | 0.97 | rampe d'opacité par profondeur |
| `DEEP_TINT` | vec3f(0.05, 0.18, 0.5) | couleur par profondeur Beer-Lambert |
| `DEPTH_DARKEN` | 0.32 | couleur par profondeur Beer-Lambert |
| `FALLING_LEAVES` | true | raymarch des feuilles tombantes peintes |
| `FINE_FAR` | 40.0 | octaves de vagues sur réseau entier tourné & LOD |
| `FINE_NEAR` | 24.0 | octaves de vagues sur réseau entier tourné & LOD |
| `FINE_SHIFT` | vec2i(459, 312) | octaves de vagues sur réseau entier tourné & LOD |
| `FINE_STRIDE` | 3700 | octaves de vagues sur réseau entier tourné & LOD |
| `FOAM_COLOUR` | vec3f(0.97, 0.99, 1.0) | écume de rivage |
| `FOAM_SOLID` | 0.1 | écume de rivage |
| `FOAM_WIDTH` | 0.45 | écume de rivage |
| `GLINT_COLOUR` | vec3f(1.0, 0.97, 0.88) | couleur du sheen solaire large |
| `GRAIN_NEAR` | 14.0 | cutoff du grain proche |
| `GRASS_GUSTS` | 0.16 | rafales sur le dessus de l'herbe |
| `GUST_DIRECTION` | vec2f(0.92, 0.39) | rafales sur le dessus de l'herbe |
| `HASH_PERIOD` | 289 | plomberie du réseau de cellules |
| `LANDING_RINGS` | true | interrupteur : anneaux d'atterrissage de feuilles |
| `LEAF_CELL` | 3.0 | raymarch des feuilles tombantes peintes |
| `LEAF_CHANCE` | 0.3 | raymarch des feuilles tombantes peintes |
| `LEAF_FALL` | 0.6 | raymarch des feuilles tombantes peintes |
| `LEAF_RANGE` | 10.0 | raymarch des feuilles tombantes peintes |
| `LEAF_SHIMMER` | 0.3 | chatoyancement des feuilles |
| `LEAF_SIZE` | 0.09 | raymarch des feuilles tombantes peintes |
| `LEAF_STEPS` | 6 | raymarch des feuilles tombantes peintes |
| `MIST` | 0.16 | force des taches |
| `MIST_FAR` | 48.0 | taches dérivantes ancrées monde |
| `MIST_SIZE` | 5.0 | taches dérivantes ancrées monde |
| `REFLECTIVITY` | 0.45 | réflexion ciel de Schlick |
| `RING_CELL` | 4 | anneaux d'atterrissage de feuilles |
| `RING_CHANCE` | 0.45 | anneaux d'atterrissage de feuilles |
| `RING_EVERY` | 5.0 | anneaux d'atterrissage de feuilles |
| `RING_SIZE` | 1.1 | anneaux d'atterrissage de feuilles |
| `RING_STRENGTH` | 0.4 | anneaux d'atterrissage de feuilles |
| `SHADE_FROM` | -0.1 | bornes de teinte solaire par direction de face |
| `SHADE_TINT` | vec3f(0.76, 0.8, 0.88) | bornes de teinte solaire par direction de face |
| `SHALLOW_OPACITY` | 0.3 | rampe d'opacité par profondeur |
| `SHALLOW_TINT` | vec3f(0.58, 0.92, 0.92) | couleur par profondeur Beer-Lambert |
| `SKY_REFLECTION_COLOUR` | vec3f(0.68, 0.79, 0.94) | réflexion ciel de Schlick |
| `SOFTEN` | 0.12 | lissage du speckle (look soft) |
| `SOFT_LEVEL` | 0.5 | lissage du speckle (look soft) |
| `SUNSPOTS` | 0.45 | taches de soleil dérivantes dans l'ombre |
| `SUNSPOT_SPEED` | 0.3 | taches de soleil dérivantes dans l'ombre |
| `SUN_FROM` | 0.35 | bornes de teinte solaire par direction de face |
| `SUN_TINT` | vec3f(1.1, 1.04, 0.94) | bornes de teinte solaire par direction de face |
| `TAU` | 6.2831853 | constante 2π |
| `VIBRANCE` | 0.22 | grade pré-fog (lift + vibrance à garde chroma) |
| `WATER_ALPHA` | 0.9 | valeurs enregistrées de l'eau (reconstruites) |
| `WATER_COLOUR` | vec3f(0.5, 0.5, 0.8) | valeurs enregistrées de l'eau (reconstruites) |
| `WIND_SPEED` | 0.8 | réglages maîtres du vent |
| `WIND_STRENGTH` | 1.0 | réglages maîtres du vent |

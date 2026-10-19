#!/usr/bin/env python3
# Generates Part X inside guide/GUIDE-EN.md and guide/GUIDE-FR.md (spliced between markers)
# from the ACTUAL sources in this repository (grep, not memory).
# Every constant appears with its exact value; roles come from curated
# dictionaries (individual or by prefix family).
import re, io, os
from collections import OrderedDict

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SOURCES = [
    ("cinematic-v5", os.path.join(ROOT, "cinematic-v5", "pack", "shader.wgsl")),
    ("titan", os.path.join(ROOT, "handoff-round-14", "pack", "shader.wgsl")),
    ("sonde", os.path.join(ROOT, "probe-diag", "pack", "shader.wgsl")),
    ("breeze", os.path.join(ROOT, "bloxd-shaders-db", "workshop-archive", "breeze-v1")),
]
CONST_RE = re.compile(r"const ([A-Za-z_][A-Za-z_0-9]*)(?::\s*[A-Za-z0-9<>]+)?\s*=\s*([^;]+);")

def harvest():
    packs = OrderedDict()
    for label, path in SOURCES:
        items = []
        if os.path.isdir(path):
            for dirpath, _, files in os.walk(path):
                for f in sorted(files):
                    if f.endswith(".wgsl"):
                        t = io.open(os.path.join(dirpath, f), encoding="utf-8").read()
                        for m in CONST_RE.finditer(t):
                            items.append((m.group(1), m.group(2).strip(), f))
        elif os.path.isfile(path):
            t = io.open(path, encoding="utf-8").read()
            for m in CONST_RE.finditer(t):
                items.append((m.group(1), m.group(2).strip(), os.path.basename(path)))
        seen = {}
        for n, v, f in items:
            if n not in seen:
                seen[n] = (v, f)
        packs[label] = seen
    return packs

# ---- curated roles (exact name first, then prefix family) -------------------
EXACT = {
    # engine-facing ids & modes (cv5)
    "grass_id": ("the decorative grass PLANT block id (per-block sway gate)", "l'id du bloc PLANTE herbe (gate de sway par bloc)"),
    "tall_grass_id": ("Tall Grass plant id (same gate)", "l'id de la plante Tall Grass (même gate)"),
    "sway_mode": ("sway implementation selector; 2 = colour-only (runs everywhere)", "sélecteur d'implémentation du sway ; 2 = couleur seule (partout)"),
    "sway_amount": ("sway amplitude factor", "amplitude du sway"),
    "sway_speed": ("sway time multiplier", "multiplicateur de temps du sway"),
    # cv5 grade/atmosphere
    "grade_saturation": ("final saturation multiplier", "multiplicateur de saturation final"),
    "grade_contrast": ("final contrast offset", "contraste final"),
    "haze_density": ("height-fog density", "densité du brouillard de hauteur"),
    "haze_strength": ("height-fog strength", "force du brouillard de hauteur"),
    "haze_base_height": ("fog reference altitude", "altitude de référence du brouillard"),
    "haze_height_falloff": ("fog altitude falloff", "décroissance du brouillard avec l'altitude"),
    "cloud_strength": ("cv5 2D cloud layer strength", "force de la couche nuages 2D cv5"),
    "cloud_scale": ("cv5 cloud noise scale", "échelle du bruit nuages cv5"),
    "cloud_speed": ("cv5 cloud drift speed (x,y)", "vitesse de dérive des nuages cv5"),
    "cloud_height": ("cv5 cloud layer altitude", "altitude de la couche nuages cv5"),
    "ray_strength": ("god-ray strength", "force des god-rays"),
    "ray_sky_min": ("god-ray sky exposure gate low", "porte d'exposition ciel des god-rays (bas)"),
    "ray_sky_max": ("god-ray sky exposure gate high", "porte d'exposition ciel des god-rays (haut)"),
    "sun_fallback": ("sun tint when skyLightColour is unavailable", "teinte soleil de repli"),
    "leaf_glow": ("leaf translucency glow", "lueur de translucence des feuilles"),
    "bloom_spill": ("bloom bleed amount", "quantité de diffusion bloom"),
    "hot_glow_strength": ("lava/hot-emitter glow", "lueur des émetteurs chauds"),
    "underwater_strength": ("underwater colour grade strength", "force de l'étalonnage sous-marin"),
    # cv5 measured/care constants
    "TR_EDGE_AO": ("edge AO strength (skyLight-weighted by law)", "force de l'AO d'arête (pondérée skyLight, loi)"),
    "TR_GRAIN": ("film grain amount (distance-faded)", "quantité de grain (fondu par distance)"),
    "TR_GOLDEN_TINT": ("golden-hour tint", "teinte heure dorée"),
    "TR_GOLDEN_GAIN": ("golden-hour gain", "gain heure dorée"),
    "TR_MOONLIGHT": ("moonlight tint", "teinte clair de lune"),
    "TR_MOON_GAIN": ("moonlight gain", "gain clair de lune"),
    "TR_EPSILON": ("generic epsilon guard", "garde epsilon générique"),
    "TR_WATER_DAY_TINT": ("water tint, day band", "teinte d'eau, bande jour"),
    "TR_WATER_DUSK_TINT": ("water tint, dusk band", "teinte d'eau, bande crépuscule"),
    "TR_WATER_NIGHT_TINT": ("water tint, night band", "teinte d'eau, bande nuit"),
    "TR_WATER_TINT": ("water tint mix strength", "force du mix de teinte d'eau"),
    "TR_WATER_CLARITY": ("water clarity (view-through)", "clarté de l'eau"),
    "TR_WATER_REFLECTIVITY": ("water reflectivity", "réflectivité de l'eau"),
    "TR_WATER_GLINT": ("sun glint strength", "force du scintillement solaire"),
    "TR_WATER_RIPPLE": ("ripple amplitude", "amplitude des rides"),
    "TR_WAVE_OMEGA_A": ("wave band A angular frequency (frozen R17)", "fréquence angulaire bande A (gel R17)"),
    "TR_WAVE_OMEGA_B": ("wave band B angular frequency (frozen R17)", "fréquence angulaire bande B (gel R17)"),
    "TR_WAVE_OMEGA_C": ("wave band C angular frequency (frozen R17)", "fréquence angulaire bande C (gel R17)"),
    "TR_WAVE_OMEGA_D": ("wave band D angular frequency (frozen R17)", "fréquence angulaire bande D (gel R17)"),
    "TR_WAVE_OMEGA_E": ("wave band E angular frequency (frozen R17)", "fréquence angulaire bande E (gel R17)"),
    "TR_WAVE_OMEGA_F": ("wave band F angular frequency (frozen R17)", "fréquence angulaire bande F (gel R17)"),
    "TR_CLOUD_AMBIENT_DIM": ("ambient dimming under cloud shadow", "atténuation ambiante sous l'ombre des nuages"),
    # sonde
    "PROBE_MODE": ("probe channel selector; >=0 freezes a measurement mode", "sélecteur de canal sonde ; >=0 fige un mode de mesure"),
    "MODE_0_SKYLIGHT_RAW": ("probe mode 0 — raw skyLight to all channels", "sonde mode 0 — skyLight brut sur tous les canaux"),
    "MODE_1_SKY_LEVEL_0_15": ("probe mode 1 — skyLight rescaled 0-15", "sonde mode 1 — skyLight remis à l'échelle 0-15"),
    "MODE_2_BLOCKLIGHT_RGB": ("probe mode 2 — blockLight RGB as colour", "sonde mode 2 — blockLight RGB en couleur"),
    "MODE_3_HELDLIGHT_RGB_X4": ("probe mode 3 — heldLight ×4 (visibility boost)", "sonde mode 3 — heldLight ×4 (visibilité)"),
    "MODE_4_SKYLIGHTCOLOUR_NORM": ("probe mode 4 — skyLightColour normalised", "sonde mode 4 — skyLightColour normalisée"),
    "MODE_5_AMBIENTCOLOUR_NORM": ("probe mode 5 — ambient colour normalised", "sonde mode 5 — couleur ambiante normalisée"),
    "MODE_6_FOGVISIBILITY_GRAY": ("probe mode 6 — fogVisibility as grey", "sonde mode 6 — fogVisibility en gris"),
    "MODE_7_FOGCOLOUR_RAW": ("probe mode 7 — raw fogColour (reveals black in mode NONE)", "sonde mode 7 — fogColour brut (révèle le noir en mode NONE)"),
    "MODE_8_SUNDIRECTION_RGB": ("probe mode 8 — sun direction as RGB", "sonde mode 8 — direction soleil en RGB"),
    "MODE_9_SUNLENGTH_GRAY": ("probe mode 9 — |sunDir| as grey (0 on sunless skies)", "sonde mode 9 — |sunDir| en gris (0 sans soleil)"),
    "MODE_10_DIRECTIONAL_GRAY": ("probe mode 10 — terrain directional light as grey", "sonde mode 10 — lumière directionnelle terrain en gris"),
    "MODE_11_DEPTH_DEFINE": ("probe mode 11 — is BLOXD_SCENE_DEPTH active (green/red)", "sonde mode 11 — BLOXD_SCENE_DEPTH actif ? (vert/rouge)"),
    "MODE_12_DEPTH_FOUND": ("probe mode 12 — bloxdOpaqueBehind().found (green/red)", "sonde mode 12 — behind.found (vert/rouge)"),
    "MODE_13_DEPTH_PATH_BANDS": ("probe mode 13 — water path depth colour bands", "sonde mode 13 — bandes d'épaisseur d'eau (path)"),
    "MODE_14_DEPTH_VERTICAL_BANDS": ("probe mode 14 — vertical depth colour bands", "sonde mode 14 — bandes de profondeur verticale"),
    "MODE_15_DEPTH_BED_ANCHOR": ("probe mode 15 — bed anchor visualisation (fract bed.y)", "sonde mode 15 — ancrage au lit (fract bed.y)"),
    "MODE_SECONDS": ("probe seconds-per-mode before rotating", "secondes par mode avant rotation"),
    "TR_EPS": ("probe epsilon", "epsilon de la sonde"),
    # breeze stragglers
    "MIST": ("blotch strength", "force des taches"),
    "LANDING_RINGS": ("feature toggle: leaf-landing rings", "interrupteur : anneaux d'atterrissage de feuilles"),
    "TAU": ("2π constant", "constante 2π"),
    # cv5 stragglers
    "TR_SCOTO": ("scotopic (rod-vision) mixing strength", "force du mix scotopique (vision des bâtonnets)"),
    "TR_RELIEF_SCALE": ("relief-mapping height scale", "échelle de hauteur du relief"),
    "TR_RELIEF_EPS": ("relief-mapping step epsilon", "pas epsilon du relief"),
    "TR_RELIEF_HEIGHT": ("relief heightfield amplitude", "amplitude du champ de hauteur"),
    "TR_RELIEF_GAIN": ("relief lighting gain", "gain d'éclairage du relief"),
    "TR_SKYF_HORIZON_MIX": ("sky-fog: horizon haze blend into the fake sky", "ciel-brouillard : fusion de la brume d'horizon dans le faux ciel"),
    "TR_SKYF_FOG_MIX": ("sky-fog: share of the engine fog colour replaced by the sky gradient", "ciel-brouillard : part de la couleur de brouillard moteur remplacée par le dégradé de ciel"),
    "TR_SKYF_TOP": ("sky-fog: fake-sky zenith colour (Blocky Day proven)", "ciel-brouillard : couleur zénithale du faux ciel (prouvée Blocky Day)"),
    "TR_SKYF_LOW": ("sky-fog: fake-sky horizon colour (Blocky Day proven)", "ciel-brouillard : couleur d'horizon du faux ciel (prouvée Blocky Day)"),
    "TR_SKYF_GLOW_COL": ("sky-fog: sun-glow colour inside the fake sky", "ciel-brouillard : couleur du halo solaire dans le faux ciel"),
    "TR_SKYF_GLOW": ("sky-fog: sun-glow strength (Blocky Day HORIZON_GLOW)", "ciel-brouillard : force du halo solaire (HORIZON_GLOW de Blocky Day)"),
    "TR_SKYF_CURVE": ("sky-fog: elevation-curve steepness (Blocky Day proven)", "ciel-brouillard : pente de la courbe d'élévation (prouvée Blocky Day)"),
    "tall_grass_top_id": ("Tall Grass top-half block id (sway gate)", "id du bloc moitié haute de Tall Grass (gate de sway)"),
    "TR_SWAY_FLOWER_LO": ("flower id range start (sway gate)", "début de la plage d'ids des fleurs (gate de sway)"),
    "TR_SWAY_VINE_W": ("vine sway weight (id 219)", "poids de sway des vignes (id 219)"),
    "TR_SWAY_FLOWER_HI": ("flower id range end (sway gate)", "fin de la plage d'ids des fleurs (gate de sway)"),
    "TR_LEAF_LOD_SHRINK": ("falling leaves: distant shrink share", "feuilles tombantes : rétrécissement au loin"),
    "TR_LEAF_FADE_LO": ("falling leaves: distance where fading starts", "feuilles tombantes : distance de début de fondu"),
    "TR_WAVE_SWELL_AMP": ("water: long swell normal amplitude", "eau : amplitude de la houle longue dans la normale"),
    "TR_WAVE_SWELL_SCALE": ("water: swell spatial frequency (radians per block)", "eau : fréquence spatiale de la houle (radians par bloc)"),
    "TR_WAVE_SWELL_FOAM": ("water: foam strength on swell crests", "eau : force de l'écume sur les crêtes de houle"),
    "TR_HZN_CLOUD_STR": ("horizon cloud bank strength", "force du banc de nuages d'horizon"),
    "TR_SPLASH_CHANCE": ("lava: share of cells with an active splash source", "lave : proportion de cellules avec source d'éclaboussure active"),
    "TR_SPLASH_SIZE": ("lava: droplet angular size at 1 block", "lave : taille angulaire d'une goutte à 1 bloc"),
    "TR_SPLASH_HEIGHT": ("lava: droplet apex height", "lave : hauteur d'apogée des gouttes"),
    "TR_SPLASH_T_RISE": ("lava: rise-and-fall period (must divide 3600)", "lave : période montée-descente (doit diviser 3600)"),
    "TR_SPLASH_BRIGHT": ("lava: droplet brightness", "lave : éclat des gouttes"),
    "TR_SPLASH_COL": ("lava: droplet colour", "lave : couleur des gouttes"),
    "TR_SPLASH_TRAIL": ("lava: trail spacing behind the drop (fraction of cycle)", "lave : espacement de la traînée derrière la goutte (fraction de cycle)"),
    "TR_GLASS_MIRROR": ("glass: sky reflection strength (fresnel)", "verre : force du reflet du ciel (fresnel)"),
    "TR_MIST_GROUND": ("ground mist: strength at golden hour", "brume au sol : force à l'heure dorée"),
    "TR_MIST_GROUND_BAND": ("ground mist: height band around the eye (blocks)", "brume au sol : bande de hauteur autour de l'œil (blocs)"),
    "TR_MIST_GROUND_LO": ("ground mist: distance fade start (blocks)", "brume au sol : début du fondu de distance (blocs)"),
    "TR_MIST_GROUND_HI": ("ground mist: distance fade end (blocks)", "brume au sol : fin du fondu de distance (blocs)"),
    "TR_MIST_GROUND_COL": ("ground mist: veil colour", "brume au sol : couleur du voile"),
    "TR_BACKLIGHT": ("backlight: strength of vegetation against-sun glow", "contre-jour : force de la lueur de la végétation dos au soleil"),
    "TR_BACKLIGHT_COL": ("backlight: warm glow colour", "contre-jour : couleur chaude de la lueur"),
    "TR_BFLY_CHANCE": ("butterflies: share of air cells holding one", "papillons : proportion de cellules d'air occupées"),
    "TR_BFLY_SIZE": ("butterflies: body size", "papillons : taille du corps"),
    "TR_BFLY_T_WING": ("butterflies: wing-beat angular speed (wrap-locked)", "papillons : vitesse de battement des ailes (verrouillée au wrap)"),
    "TR_BFLY_ROAM": ("butterflies: roaming radius around the cell", "papillons : rayon d'errance autour de la cellule"),
    "TR_BFLY_TALL": ("butterflies: wing-disc height ratio", "papillons : ratio de hauteur du disque d'ailes"),
    "TR_BFLY_GAP": ("butterflies: half-separation of the two wings", "papillons : demi-séparation des deux ailes"),
    "TR_BFLY_BODY": ("butterflies: body sliver half-width", "papillons : demi-largeur du corps"),
    "TR_LAVA_FLOW_SCALE": ("lava: viscous flow texture scale (much slower than water)", "lave : échelle de la texture de flot visqueux (bien plus lente que l'eau)"),
    "TR_EMBER_CHANCE": ("lava: share of cells emitting rising embers", "lave : proportion de cellules émettant des braises"),
    "TR_EMBER_T_RISE": ("lava: ember rise period (must divide 3600)", "lave : période de montée des braises (doit diviser 3600)"),
    "TR_EMBER_HEIGHT": ("lava: ember rise height (blocks)", "lave : hauteur de montée des braises (blocs)"),
    "TR_EMBER_SIZE": ("lava: ember angular size at 1 block", "lave : taille angulaire d'une braise à 1 bloc"),
    "TR_MOTE_CHANCE": ("air motes: share of cells holding one (cave spores / day pollen)", "motes d'air : proportion de cellules occupées (spores de grottes / pollens du jour)"),
    "TR_MOTE_SIZE": ("air motes: angular size at 1 block", "motes d'air : taille angulaire à 1 bloc"),
    "TR_MOTE_COL": ("air motes: cave spore colour", "motes d'air : couleur des spores de grottes"),
    "TR_POLLEN_COL": ("air motes: golden pollen colour", "motes d'air : couleur des pollens dorés"),
    "TR_BAT_CHANCE": ("bats: share of air cells at dusk", "chauves-souris : proportion de cellules au crépuscule"),
    "TR_BAT_ROAM": ("bats: erratic roaming radius", "chauves-souris : rayon d'errance saccadée"),
    "TR_BAT_T_WING": ("bats: fast wing-beat speed (wrap-locked)", "chauves-souris : vitesse de battement rapide (verrouillée au wrap)"),
    "TR_BAT_COL": ("bats: dark silhouette colour", "chauves-souris : couleur de la silhouette sombre"),
    "TR_BAT_SIZE": ("bats: body size", "chauves-souris : taille du corps"),
    "TR_LAMP_FLICKER": ("lamp flicker: spill modulation depth (0 = off)", "vacillement lampes : profondeur de modulation (0 = off)"),
    "TR_CINEMA_MODE": ("cinema mode: false = normal, true = boosted atmosphere", "mode cinéma : false = normal, true = atmosphère poussée"),
    "TR_CINEMA_BOOST": ("cinema mode: multiplier on golden mist and backlight", "mode cinéma : multiplicateur de brume dorée et contre-jour"),
    "TR_BUG_SHARE": ("butterflies: share that are ladybugs instead", "papillons : part qui sont des coccinelles"),
    "TR_BUG_COL": ("ladybugs: shell red", "coccinelles : rouge de la carapace"),
    "TR_MOON_COLUMN": ("water: moonlight column strength on the river", "eau : force de la colonne de clair de lune sur le fleuve"),
    "TR_AURORA_WATER": ("water: night aurora reflection strength (in our reflection only)", "eau : force de l'aurore nocturne reflétée (dans notre reflet seulement)"),
    "TR_ALT_HAZE": ("altitude haze: veil strength above 55 blocks", "brume d'altitude : force du voile au-dessus de 55 blocs"),
    "TR_BFLY_COL1": ("butterflies: white variant", "papillons : variante blanche"),
    "TR_BFLY_COL2": ("butterflies: yellow variant", "papillons : variante jaune"),
    "TR_BFLY_COL3": ("butterflies: orange variant", "papillons : variante orange"),
    "TR_SKYF_HAZE_DESAT": ("aerial-haze grey desaturation (lower = bluer sky feel)", "désaturation grise de la brume aérienne (plus bas = ciel plus bleu)"),
    "TR_LAMP_SOFT_GAIN": ("lamp softening: blockLight to wash-factor gain", "adoucissement lampes : gain blockLight → facteur de lavage"),
    "TR_LAMP_SOFT_AO": ("lamp softening: edge-AO kept near lamps", "adoucissement lampes : AO de bord conservée près des lampes"),
    "TR_LAMP_SOFT_GRAIN": ("lamp softening: grain kept near lamps", "adoucissement lampes : grain conservé près des lampes"),
    "TR_LEAF_ON": ("feature toggle: falling leaves", "interrupteur : feuilles tombantes"),
    "TR_LEAF_RANGE": ("falling leaves: draw distance from the eye", "feuilles tombantes : distance de dessin depuis l'œil"),
    "TR_LEAF_STEPS": ("falling leaves: ray-march samples along the view line", "feuilles tombantes : échantillons du march de rayon le long de la ligne de vue"),
    "TR_LEAF_CELL": ("falling leaves: air-cell size (one leaf max per cell)", "feuilles tombantes : taille des cellules d'air (une feuille max par cellule)"),
    "TR_LEAF_CHANCE": ("falling leaves: share of cells holding a leaf", "feuilles tombantes : proportion de cellules occupées"),
    "TR_LEAF_SIZE": ("falling leaves: leaf half-width", "feuilles tombantes : demi-largeur d'une feuille"),
    "TR_LEAF_FALL": ("falling leaves: fall speed (must equal WRAP*CELL/3600 exactly)", "feuilles tombantes : vitesse de chute (= WRAP*CELL/3600 exactement)"),
    "TR_CANOPY_LO": ("tree-effect window: minimum skyLight (caves stay bare)", "fenêtre effets d'arbres : skyLight minimum (les grottes restent nues)"),
    "TR_CANOPY_HI": ("tree-effect window: skyLight of open sky (fields stay bare)", "fenêtre effets d'arbres : skyLight du ciel ouvert (les plaines restent nues)"),
    "TR_LEAF_WRAP": ("falling leaves: y-cell wrap for a seamless 3600 s loop", "feuilles tombantes : wrap en y des cellules pour une boucle 3600 s sans saut"),
    "TR_LEAF_W_SWAY_A": ("falling leaves: sway angular speed x (wrap-locked)", "feuilles tombantes : vitesse angulaire de balancement x (verrouillée au wrap)"),
    "TR_LEAF_W_SWAY_B": ("falling leaves: sway angular speed z (wrap-locked)", "feuilles tombantes : vitesse angulaire de balancement z (verrouillée au wrap)"),
    "TR_LEAF_W_SPIN": ("falling leaves: spin angular speed (wrap-locked)", "feuilles tombantes : vitesse angulaire de rotation (verrouillée au wrap)"),
    "TR_LEAF_W_FLIP": ("falling leaves: flip angular speed (wrap-locked)", "feuilles tombantes : vitesse angulaire de retournement (verrouillée au wrap)"),
    "TR_LEAF_LEN": ("falling leaves: leaf length/width aspect", "feuilles tombantes : rapport longueur/largeur de la feuille"),
    "TR_LEAF_TIP": ("falling leaves: pointed-tip taper strength", "feuilles tombantes : force de la pointe effilée"),
    "TR_LEAF_SIZE_VAR": ("falling leaves: per-leaf size variation (+/-)", "feuilles tombantes : variation de taille par feuille (+/-)"),
    "TR_LEAF_RIM": ("falling leaves: centre rim-light strength", "feuilles tombantes : force du rim-light au centre"),
    "TR_LEAF_TWOTONE": ("falling leaves: per-leaf two-tone variation", "feuilles tombantes : variation bicolore par feuille"),
    "TR_LEAF_AUTUMN": ("falling leaves: share of autumn-tinted leaves", "feuilles tombantes : proportion de feuilles teintées automne"),
    "TR_LEAF_AUTUMN_GOLD": ("falling leaves: autumn golden tint", "feuilles tombantes : teinte dorée d'automne"),
    "TR_LEAF_AUTUMN_RUST": ("falling leaves: autumn rust tint", "feuilles tombantes : teinte rouille d'automne"),
    "TR_LEAF_FLUTTER": ("falling leaves: vertical flutter amplitude", "feuilles tombantes : amplitude du flottement vertical"),
    "TR_LEAF_BACKLIT": ("falling leaves: backlit glow when sun is behind", "feuilles tombantes : halo en contre-jour quand le soleil est derrière"),
    "TR_LEAF_W_GUST": ("falling leaves: gust cycle angular speed (wrap-locked)", "feuilles tombantes : vitesse angulaire du cycle de rafales (verrouillée au wrap)"),
    "TR_LEAF_GUST": ("falling leaves: sway boost during gusts", "feuilles tombantes : surcroît de balancement pendant les rafales"),
    "TR_LEAF_DRIFT": ("falling leaves: downwind drift (cloud direction)", "feuilles tombantes : dérive sous le vent (direction des nuages)"),
    "TR_FLY_CHANCE": ("fireflies: share of air cells holding one", "lucioles : proportion de cellules d'air occupées"),
    "TR_FLY_SIZE": ("fireflies: glow dot radius", "lucioles : rayon du point lumineux"),
    "TR_FLY_COLOUR": ("fireflies: glow colour", "lucioles : couleur de la lueur"),
    "TR_FLY_W_BLINK": ("fireflies: blink angular speed (wrap-locked)", "lucioles : vitesse angulaire de clignotement (verrouillée au wrap)"),
    "TR_FLY_W_BOB": ("fireflies: hover bobbing angular speed (wrap-locked)", "lucioles : vitesse angulaire du flottement (verrouillée au wrap)"),
    "TR_GLASS_RIM": ("glass: grazing-angle edge brightening", "verre : éclaircissement des bords aux angles rasants"),
    "TR_LITTER_MIX": ("leaf litter: ground blend strength under canopy", "litière de feuilles : force du mélange au sol sous canopée"),
    "TR_LITTER_SCALE": ("leaf litter: speckle cells per block", "litière de feuilles : cellules de mouchetis par bloc"),
    "TR_LITTER_DENS": ("leaf litter: share of cells left bare", "litière de feuilles : proportion de cellules laissées nues"),
    "TR_SKY2_TWI_LOW": ("twilight sky horizon colour (peach-gold)", "couleur d'horizon du ciel d'aube/crépuscule (pêche-or)"),
    "TR_SKY2_TWI_TOP": ("twilight sky zenith colour (mauve)", "couleur zénithale du ciel d'aube/crépuscule (mauve)"),
    "TR_SKY2_NIGHT_LOW": ("night sky horizon colour (deep blue)", "couleur d'horizon du ciel de nuit (bleu profond)"),
    "TR_SKY2_NIGHT_TOP": ("night sky zenith colour", "couleur zénithale du ciel de nuit"),
    "TR_SKY2_GLOW_DAWN": ("dawn sun-glow colour", "couleur du halo solaire à l'aube"),
    "TR_SKY2_GLOW_DUSK": ("dusk sun-glow colour", "couleur du halo solaire au crépuscule"),
    "TR_SKY2_GLOW_NIGHT": ("moon-glow colour", "couleur du halo de lune"),
    "TR_SKY2_BAND_A": ("sun elevation: full night below this", "élévation solaire : nuit complète en dessous"),
    "TR_SKY2_BAND_B": ("sun elevation: twilight begins here", "élévation solaire : le crépuscule commence ici"),
    "TR_SKY2_BAND_C": ("sun elevation: day begins here", "élévation solaire : le jour commence ici"),
    "TR_SKY2_BAND_D": ("sun elevation: full day above this", "élévation solaire : jour complet au-dessus"),
    "TR_SOFTEN_AMOUNT": ("face-speckle smoothing strength (anti-seam)", "force du lissage du speckle des faces (anti-séparations)"),
    "TR_SOFTEN_LEVEL": ("brightness smoothed faces settle towards", "luminance cible des faces lissées"),
    "TR_SOFTEN_MIST": ("soft cloud-blotch strength on faces", "force des taches nuageuses douces sur les faces"),
    "TR_SOFTEN_MIST_SIZE": ("blotch frequency per block", "fréquence des taches par bloc"),
    "TR_SOFTEN_MIST_FAR": ("distance where blotches fade out", "distance de disparition des taches"),
    "TR_SOFTEN_GRAIN_NEAR": ("distance where the fine grain layer stops", "distance d'arrêt de la couche de grain fin"),
    "luma": ("Rec.709 luminance weights", "poids de luminance Rec.709"),
    "shadow_strength": ("directional shadow strength", "force des ombres directionnelles"),
    "shadow_softness": ("shadow edge softness", "douceur du bord d'ombre"),
    "shadow_threshold": ("skyLight threshold where shadows start", "seuil skyLight de déclenchement des ombres"),
    "shadow_ambient_drop": ("ambient loss inside shadow", "perte ambiante dans l'ombre"),
    "shadow_tint": ("shadow cool tint", "teinte froide des ombres"),
}
FAMILY = [
    ("TR_TAU|TR_PI|TR_EPSILON|TR_NOISE_WRAP", "maths/noise plumbing", "plomberie maths/bruit"),
    ("TR_LOOP_CELLS|TR_LOOP_SECONDS", "wrap-lock (time/precision loops)", "verrou de wrap (temps/précision)"),
    ("TR_DITHER|TR_DETAIL_NEAR|TR_DETAIL_FAR", "dither & LOD detail fades", "dither & fondus de détail LOD"),
    ("TR_SUN_AIR|TR_SUN_REDDEN|TR_SUN_HUE", "sun airmass reddening (sky model)", "rougissement airmass du soleil (modèle ciel)"),
    ("TR_MOON_REDDEN|TR_MOON_COLOUR|TR_MOON_DIFFUSE|TR_MOON_OPEN|TR_NIGHT_AMBIENT", "night/moon ambient system", "système ambiant nuit/lune"),
    ("TR_SKY_", "sky gradient (zenith/horizon/dusk)", "gradient de ciel (zénith/horizon/crépuscule)"),
    ("TR_SUN_DISC|TR_SUN_GLOW", "sun disc & glow render", "rendu disque & halo solaire"),
    ("TR_MOON_DISC|TR_MOON_RING", "moon disc & ring render", "rendu disque & anneau lunaires"),
    ("TR_STAR_|TR_MW_|TR_AURORA_|TR_METEOR_", "night-sky features (stars/milky way/aurora/meteors)", "traits du ciel nocturne (étoiles/voie lactée/aurores/météores)"),
    ("TR_CLOUD_SHADOW|TR_CLOUD_POWDER|TR_CLOUD_SELF|TR_CLOUD_MIN|TR_CLOUD_RAY|TR_CLOUD_FILL|TR_CLOUD_TOP|TR_CLOUD_BOTTOM|TR_CLOUD_SILVER|TR_CLOUD_OPACITY|TR_CLOUD_WIND|TR_CLOUD_SPEED|TR_CLOUD_SOFTNESS|TR_CLOUD_COVERAGE|TR_CLOUD_SCALE|TR_CLOUD_HEIGHT", "volumetric clouds (marching & lighting)", "nuages volumétriques (marching & éclairage)"),
    ("TR_CIRRUS_", "cirrus layer", "couche cirrus"),
    ("TR_AERIAL_|TR_AIR_SCATTER|TR_MIE_|TR_MIST_", "aerial perspective / mist", "perspective aérienne / brume"),
    ("TR_UNDERWATER_", "underwater grade when camera submerged", "étalonnage sous-marin caméra immergée"),
    ("TR_WAVE_((?!OMEGA))|TR_WAVE_CHROMA|TR_WAVE_PRESS|TR_MIRROR", "wave field shaping (frozen R17 baseline)", "façonnage du champ de houles (baseline gelée R17)"),
    ("TR_MOON_GLINT", "moon glint on water", "reflet de lune sur l'eau"),
    ("TR_WATER_", "water optics", "optique de l'eau"),
    # breeze
    ("SOFTEN|SOFT_LEVEL", "texture speckle smoothing (soft look)", "lissage du speckle (look soft)"),
    ("MIST_", "drifting world-fixed blotches", "taches dérivantes ancrées monde"),
    ("GRAIN_NEAR", "near grain cutoff", "cutoff du grain proche"),
    ("BLOCK_VARIATION|CELL_VARIATION|CELL_FAR", "per-block / per-cell brightness variation", "variation de luminosité par bloc / cellule"),
    ("WIND_STRENGTH|WIND_SPEED", "wind master settings", "réglages maîtres du vent"),
    ("SHADE_TINT|SUN_TINT|SHADE_FROM|SUN_FROM", "face-direction sun tint bounds", "bornes de teinte solaire par direction de face"),
    ("CANOPY_", "tree-canopy shadow (lost skyLight level)", "ombre de canopée (niveau skyLight perdu)"),
    ("SUNSPOT", "drifting sunspots through canopy shadow", "taches de soleil dérivantes dans l'ombre"),
    ("LEAF_SHIMMER", "gust shimmer on leaves", "chatoyancement des feuilles"),
    ("GRASS_GUSTS|GUST_DIRECTION", "wind gusts rolling over grass tops", "rafales sur le dessus de l'herbe"),
    ("BRIGHTEN|VIBRANCE", "pre-fog grade (lift + chroma-guarded vibrance)", "grade pré-fog (lift + vibrance à garde chroma)"),
    ("CELLS_PER_BLOCK|HASH_PERIOD", "shading-cell lattice plumbing", "plomberie du réseau de cellules"),
    ("COARSE_STRIDE|COARSE_SHIFT|FINE_STRIDE|FINE_SHIFT|FINE_NEAR|FINE_FAR", "rotated-integer-lattice wave octaves & LOD", "octaves de vagues sur réseau entier tourné & LOD"),
    ("WATER_COLOUR|WATER_ALPHA", "water's engine-registered values (rebuilt from)", "valeurs enregistrées de l'eau (reconstruites)"),
    ("SHALLOW_TINT|DEEP_TINT|DEPTH_DARKEN", "Beer-Lambert depth colouring", "couleur par profondeur Beer-Lambert"),
    ("SHALLOW_OPACITY|DEEP_OPACITY", "depth-driven opacity ramp", "rampe d'opacité par profondeur"),
    ("CREST_GAIN", "wave-crest lighting", "éclairage des crêtes"),
    ("REFLECTIVITY|SKY_REFLECTION_COLOUR", "Schlick sky reflection", "réflexion ciel de Schlick"),
    ("GLINT_COLOUR", "broad sun sheen colour", "couleur du sheen solaire large"),
    ("FOAM_", "shoreline foam edge", "écume de rivage"),
    ("RING_", "leaf-landing rings on water", "anneaux d'atterrissage de feuilles"),
    ("FALLING_LEAVES|LEAF_RANGE|LEAF_STEPS|LEAF_CELL|LEAF_CHANCE|LEAF_SIZE|LEAF_FALL", "painted falling-leaf raymarch", "raymarch des feuilles tombantes peintes"),
    ("leafColour", "leaf palette (5 hardcoded colours)", "palette des feuilles (5 couleurs en dur)"),
    # titan families (remaining)
    ("TR_AMBIENT_HUE|TR_BOUNCE_AMBIENT", "bounce/ambient hue shaping", "façonnage de teinte ambiante/rebond"),
    ("TR_AO_", "ambient-occlusion system (skyLight-weighted)", "système d'AO (pondéré skyLight)"),
    ("TR_BACKLIGHT", "backlight rim on foliage", "contre-jour sur le feuillage"),
    ("TR_BLOCK_AMBIENT|TR_BLOCK_ROUGH_SPREAD", "block-light ambient & roughness response", "réponse ambiante & rugosité à la lumière de bloc"),
    ("TR_BUMP_STRENGTH|TR_EDGE_CREASE|TR_EDGE_WIDTH|TR_MICRO_DETAIL|TR_MICRO_ROUGHNESS|TR_TERRAIN_ROUGHNESS", "micro-detail & terrain normal work", "micro-détail & normales du terrain"),
    ("TR_CAUSTIC_", "water caustics on flooded ground", "caustiques de l'eau sur le sol inondé"),
    ("TR_CLUMP_", "foliage clumping", "agglomération du feuillage"),
    ("TR_DEBUG_MODE", "debug visualisation selector (0 = off)", "sélecteur de visualisation debug (0 = off)"),
    ("TR_DIVE_MIRROR", "underwater mirror pass strength", "force du miroir sous-marin"),
    ("TR_EMISSION_", "emissive-block system (torch/lamp/gold/amber/fiery gates)", "système des blocs émissifs (gates torch/lamp/or/ambre/feu)"),
    ("TR_EXPOSURE|TR_SHOULDER|TR_TONEMAP_STRENGTH|TR_GRADE_", "tone mapping & grade", "tone mapping & grade"),
    ("TR_F0_DIELECTRIC|TR_MAT_", "PBR material set (GGX F0/roughness/sheen)", "set matériaux PBR (F0/rugosité/sheen GGX)"),
    ("TR_FACE_", "per-face variation phases", "phases de variation par face"),
    ("TR_FIRE_", "fire flicker animation", "animation scintillement du feu"),
    ("TR_FOLIAGE_NORMAL|TR_LEAF_NORMAL", "animated foliage normals", "normales animées du feuillage"),
    ("TR_GLARE_", "bloom glare shaping", "façonnage de l'éblouissement"),
    ("TR_GRASS_GLINT", "specular glint on grass", "scintillement spéculaire de l'herbe"),
    ("TR_GUST_", "wind gust field", "champ de rafales"),
    ("TR_LAMP_WOBBLE", "lamp light wobble", "vacillement des lampes"),
    ("TR_LOCAL_KEEP|TR_UNLIT_GAIN|TR_NIGHT_DIM|TR_SHELTER_SINK", "lighting framework (keep/unlit/night/shelter)", "cadre d'éclairage (keep/unlit/nuit/abri)"),
    ("TR_MAGMA_", "magma/lava material & LOD", "matériau magma/lave & LOD"),
    ("TR_NOISE_ORIGIN", "hash origin salt", "sel d'origine du hash"),
    ("TR_ORE_", "ore sparkle & spec boost", "étincelle & boost spéculaire des minerais"),
    ("TR_PLANT_", "plant-root detection tolerance", "tolérance de détection des plantes"),
    ("TR_RELIEF_SHADE|TR_RELIEF_SIGN|TR_RELIEF_STRENGTH", "relief shading", "ombrage du relief"),
    ("TR_SAND_RIPPLE_", "sand ripples", "rides de sable"),
    ("TR_SHADE_|TR_SHADOW_", "shadow shaping (thresholds, dusk widening, cool tint)", "façonnage des ombres (seuils, crépuscule, teinte froide)"),
    ("TR_SNELL_", "Snell window underwater", "fenêtre de Snell sous l'eau"),
    ("TR_SKYSPEC_", "sky specular on water", "spéculaire du ciel sur l'eau"),
    ("TR_SPARKLE_", "water sparkle glints", "scintillements de l'eau"),
    ("TR_SPEC_|TR_SPEC_AA", "specular system & anti-aliasing", "système spéculaire & anti-aliasing"),
    ("TR_SSS_", "subsurface scattering on foliage", "SSS sur le feuillage"),
    ("TR_SUNSET_BAND|TR_SUN_STRENGTH|TR_SUN_BUDGET|TR_SUN_DIRECTION_BLEND", "sun/sunset response", "réponse soleil/crépuscule"),
    ("TR_SWAY_ANGLE", "sway angle cap", "angle max de sway"),
    ("TR_TORCH_", "torch warm tint & pierce", "teinte chaude des torches & percée"),
    ("TR_VERTEX_", "vertex displacement hooks (few-game feature)", "hooks de déplacement de sommets (peu de jeux)"),
    ("TR_WIND_FIELD_", "wind field for foliage", "champ de vent pour le feuillage"),
]
def role_of(name, lang):
    if name in EXACT:
        return EXACT[name][0 if lang == "en" else 1]
    for pat, en, fr in FAMILY:
        if re.search(pat, name):
            return en if lang == "en" else fr
    return None

# ---- engine variables (hand-written, both langs) ----------------------------
ENGINE_EN = """## Engine-exposed variables (what the game gives you)

| Variable | Type / value | Meaning |
|---|---|---|
| `surface.colour` | vec3f | incoming material colour (pre-shading) |
| `surface.alpha` | f32 | incoming alpha; drives cutout discard & liquid blend |
| `surface.position` | vec3f | world position of the fragment |
| `surface.normal` | vec3f | face normal |
| `surface.blockId` | u32 | numeric block id (Part VIII) |
| `out.emission` | vec3f | self-glow, surface hook only |
| `light.skyLight` | f32 0..1 | sky light, **tone-mapped** (open sky ≈1, one lost canopy level ≈0.995) |
| `light.blockLight` | vec3f | block light colour (35% channel floor) |
| `light.heldLight` | vec3f | handheld light (≤15 blocks, dist^0.75) |
| `light.skyLightColour` | vec3f | sky tint; darkens at night |
| `light.litColour` | vec3f | surface's own lit colour |
| `light.fogVisibility` | f32 | engine fog factor (linear band 32×D per 3rd-party) |
| `light.fogColour` | vec3f | fog colour; **black when fog mode is NONE** |
| `light.blockId` | u32 | numeric block id in the light hook |
| `bloxdTimeWrap` | f32 = **3600** | the wrap period of `bloxdTime()` (seconds) |
| `bloxdOriginOffset()` | vec3i | floating-origin rebase; inject into world hashes |
| `bloxdSunDirection()` | vec3f | unit sun vector; zero on sunless skies; moon = −this |
| `bloxdFaceBlock(p,n)` | vec3i | cell (block coordinates) of the current face — per-block hash input; the id itself is `surface.blockId` / `light.blockId` |
| `bloxdOpaqueBehind()` | {found,position} | first opaque block behind a liquid fragment |
| `bloxdEyePosition()` | vec3f | camera position |
| `bloxdApplyFog(c,l)` | vec3f | mix(fogColour, c, fogVisibility) |

## Engine-internal figures every pack author needs

| Figure | Value | Provenance |
|---|---|---|
| time wrap | 3600 s | [3rd-party + shipped usage] |
| light scale | 0–15, open sky = 15 | [3rd-party + measured] |
| tone curve family | ≈ 45·b/(1+2b) (saturating) | [measured] |
| terrain shadow band | skyLight 13.6–14.95 / 15 | [measured] |
| packed-light channel floor | 35 % of max channel | [3rd-party] |
| fog band | start 32×D, end 32×(D+1) (linear per 3rd-party; EXP2 legacy note — open question) | [3rd-party] |
| default fog colour | rgb(183, 191, 195) | [3rd-party] |
| showFog off | band pushed to 3200–3328 | [3rd-party] |
| scene ambient default | 0.5 (user setting) | [3rd-party] |
| loader cap | 256 KB total .wgsl | [3rd-party] |
| scene directional lamps | 2, fixed direction/intensity | [3rd-party] |
"""
ENGINE_FR = ENGINE_EN  # tables keep English identifiers; intro FR
ENGINE_FR_INTRO = """## Variables exposées par le moteur (ce que le jeu te donne)

Les identifiants restent en anglais (ce sont les noms réels du code). Signification en contexte
FR dans la Partie II. Valeurs internes clés : wrap temps **3600 s** ; échelle lumière **0-15**,
ciel ouvert = 15 ; courbe de tone ≈ **45·b/(1+2b)** [mesuré] ; bande d'ombre terrain
**13.6-14.95/15** [mesuré] ; plancher des canaux packés **35 %** ; bande de fog **32×D →
32×(D+1)** [tierce, question ouverte] ; couleur fog défaut **rgb(183,191,195)** ; showFog off →
**3200-3328** ; ambient scène défaut **0.5** ; cap loader **256 Ko** ; 2 lampes directionnelles
figées. Détails et provenances : [Partie IV](#partie-iv--nombres-mesurés-fr) et Partie VII.

## Registre des constantes (packs locaux et packs disséqués)

Généré mécaniquement depuis les sources de ce dépôt (`guide/tools/gen_var_registry.py`) —
valeur exacte du code, rôle par constante (individuel ou par famille), pack d'origine.
"""

def table(pack_items, lang):
    out = ["| Constant | Value | Role |", "|---|---|---|"]
    missing = []
    for name in sorted(pack_items):
        v, f = pack_items[name]
        r = role_of(name, lang)
        if r is None:
            missing.append(name)
            r = "internal — see source" if lang == "en" else "interne — voir la source"
        out.append("| `%s` | %s | %s |" % (name, v, r))
    return "\n".join(out), missing

C_START = "<!-- CONSTANTS:START — generated by guide/tools/gen_var_registry.py, do not edit by hand -->"
C_END = "<!-- CONSTANTS:END -->"
def splice(path, body):
    doc = io.open(path, encoding="utf-8").read()
    i = doc.index(C_START) + len(C_START)
    j = doc.index(C_END)
    doc = doc[:i] + "\n\n" + body.rstrip() + "\n\n" + doc[j:]
    io.open(path, "w", encoding="utf-8", newline="\n").write(doc)

def main():
    packs = harvest()
    total = sum(len(p) for p in packs.values())
    report = []
    for lang, guide_file, engine_head in (("en", "GUIDE-EN.md", ENGINE_EN), ("fr", "GUIDE-FR.md", ENGINE_FR_INTRO)):
        parts = ["# Part X — The constants register (%s)" % ("FR" if lang == "fr" else "EN"), "",
                 engine_head, ""]
        titles = {
            "cinematic-v5": ("cinematic-v5 (local pack — frozen baseline)", "cinematic-v5 (pack local — baseline gelée)"),
            "titan": ("titan-bsl-ultra-v2 (local pack — sky/cloud/water showcase)", "titan-bsl-ultra-v2 (pack local — vitrine ciel/nuages/eau)"),
            "sonde": ("PROBE-DIAG-v2 (measurement probe, modes 0-15)", "PROBE-DIAG-v2 (sonde de mesure, modes 0-15)"),
            "breeze": ("Breeze v1 (shipped pack, dissected — Crownix after Ellie)", "Breeze v1 (pack publié disséqué — Crownix d'après Ellie)"),
        }
        for label, items in packs.items():
            t_en, t_fr = titles[label]
            parts += ["", "## %s — %d constants" % (t_en if lang == "en" else t_fr, len(items)), ""]
            tbl, missing = table(items, lang)
            parts.append(tbl)
            report.append("%s/%s: %d consts, %d unmatched" % (lang, label, len(items), len(missing)))
            if missing:
                report.append("  unmatched: " + ", ".join(missing))
        body = "\n".join(parts) + "\n"
        splice(os.path.join(ROOT, "guide", guide_file), body)
    print("TOTAL consts:", total)
    print("\n".join(report))

if __name__ == "__main__":
    main()

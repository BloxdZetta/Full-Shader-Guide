# Partie V — Dépannage (FR)

## À la compilation

| Symptôme | Cause / correctif |
|---|---|
| `'mod' is a reserved word in WGSL` | renommer ou utiliser `%` |
| `no definition in scope: bloxdOpaqueBehind` dans TON harnais | stub trop étroit, pas le pack — le symbole est réel (utilisé par un pack publié) |
| `#define BLOXD_…` rejeté | macros owned par le moteur ; autre préfixe |
| `direct struct construction` | partir de `bloxdDefaultSurface(...)` |
| `let _ =` rejeté | forme nue `_ = expr;` |
| naga OK, jeu rejette | Tint est plus strict sur la précédence : parenthéser `a ^= b >> c` |
| pack ignoré silencieusement | `apiVersion` pas le nombre 2, JSON invalide, ou zip emboîté dans un dossier |

## Charge mais rend mal

| Symptôme | Cause / correctif |
|---|---|
| rien ne change dans certains jeux | ces jeux désactivent les packs |
| plantes non teignables | chemin de rendu inaccessible aux packs (prouvé par dissection) |
| ombres disparues | « Lighting » off → aucun skyLight envoyé ; tes portes d'ombre s'éteignent (normal) |
| lampes cassées | assombrissement sans garde lampes (R4) |
| motifs qui glissent | `bloxdOriginOffset()` manquant dans le hash (R8) ou `bloxdTime()` non wrappé (R9) |
| eau noire en grotte | termes ciel sans porte `skyExposure` (R7) |
| NaN / scintillement noir à un angle | `normalize(toEye + sunDir)` = 0 exact quand soleil opposé à la vue — garder la longueur |
| damier pendant le chargement | fade Bayer 4×4 moteur, pas toi |
| blocs blancs en mode fog 0 | fogColour utilisé hors `bloxdApplyFog` — il arrive noir |
| shimmer/zoom loin du spawn | précision flottante : cellules entières + rebase (R8) |

## Performance

- Les **boucles** par fragment tuent : un raymarch 6 pas gated à 10 m près des arbres est fin,
  non-borné c'est la ruine (plainte visible dans les commentaires du pack n°1).
- Tout détaillé se fond par distance (R10) ; `if` (pas `mix`) quand la porte vaut 0.
- Le hash par cellule bat le bruit par pixel pour tout ce que l'œil lit comme « texture ».

## Distribution

- Retéléchargement manuel à chaque mise à jour (spam « Updated 2 hours ago » normal).
- Même nom de zip ≠ même contenu : publier le sha256.
- Les packs v1 **ne chargent plus** : migrer vers `apiVersion: 2` (Partie I).

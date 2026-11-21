# Bloxd shader packs — état des lieux de l’API v5

**Audit documentaire effectué le 21 novembre 2026.** Cette fiche complète les manuels détaillés de ce dépôt, qui décrivent l’API v2. Elle n’est pas une documentation officielle de Bloxd et ne remplace pas le test en jeu.

> **Pour créer un nouveau pack aujourd’hui : ciblez `apiVersion: 5`.** Le client documenté récemment n’accepte que v5 ; un pack v2 ne se met pas à jour en changeant simplement le nombre dans `pack.json`. Il faut porter son code et le revalider.

- [Manuel détaillé français (historique, API v2)](GUIDE-FR.md)
- [Manuel détaillé anglais (historique, API v2)](GUIDE-EN.md)
- [README et autres langues](README.md)

## Résultat de la recherche

La documentation communautaire de référence mise à jour au 21 novembre 2026 décrit **cinq versions d’API**, avec **v5 comme cible actuelle**, **neuf hooks** et **six variantes de validation**. Le saut fonctionnel important est le passage de « terrain et liquides » à trois passes distinctes : terrain, liquides et modèles. V5 expose aussi des informations de matériau, les modèles, les textures, l’état d’éclairage et les ombres via des fonctions du moteur.

Cette fiche rapporte les contrats décrits par les sources ci-dessous. Nous n’avons pas extrait le bundle client Bloxd ni téléchargé/analyser les archives des packs Workshop pendant cet audit ; les constats ci-dessous sont donc des **faits documentés et recoupés**, pas de nouvelles mesures indépendantes du moteur.

## Sources et niveau de confiance

| Source consultée | Ce qu’elle apporte | Réserve |
|---|---|---|
| [Documentation communautaire détaillée, API v5](https://github.com/imu31465/Bloxd.io-How-To-Make-Shader-Packs/tree/1748cc02a3a36a569db8dba515976bef772c4190/en) — révision `1748cc0`, 21 nov. 2026 | Historique v1–v5, signatures, champs, compatibilité, validation et variantes ; indique une analyse du client | Le dépôt indique qu’il a été créé avec l’aide d’une IA et que tout doit être vérifié en jeu ; ce n’est pas une publication de Bloxd |
| [Référence Shader API](https://prismshaders.vercel.app/shader-api) | Référence v5, neuf hooks, structures, helpers et exemples | Référence communautaire ; sa page distingue les notes communautaires des fichiers qu’elle présente comme source officielle |
| [Guide Workshop : créer un pack](https://bloxdhub.com/guides/how-to-make-a-bloxd-shader-pack) | Format du pack, limites annoncées, workflow et migrations | Guide de plateforme communautaire, non une spécification signée par Bloxd |
| [Workshop : Morningstar Shaders v5.2.1](https://bloxdhub.com/workshop/morningstar-shaders-v521-h151) et [Cube Shaders V6.1](https://bloxdhub.com/workshop/cube-shaders-v61-h25) | Exemples de packs actuellement distribués et retours de compatibilité v5 | Métadonnées et statistiques volatiles ; l’archive elle-même n’a pas été analysée ici |
| [Notes communautaires sur l’API v2](https://github.com/lowpowermode03-dev/BloxdShaders) et [référence v3](https://github.com/KaiCodes-bloxd/bloxd-shader-api-v3docs) | Points de comparaison historiques (inputs v2, flags v3) | Sources secondaires, anciennes ; utiles pour la chronologie, pas pour certifier le runtime actuel |

**Divergences à connaître :** une référence communautaire affirme que les anciennes versions peuvent encore fonctionner lorsque le manifeste correspond à leur version ; les guides Workshop et la documentation v5 plus récente disent que le jeu actuel refuse v1–v4. De même, certaines introductions Workshop résument encore les effets aux blocs, à l’eau et à la lave, alors que le contrat v5 documente trois hooks de modèle et des champs pour objets/entités. Les résumés peuvent être obsolètes ou simplifiés. Pour publier, retenez la conduite conservatrice : **portez vers v5 et testez dans le client courant** ; ne comptez pas sur une compatibilité v2 implicite, et vérifiez le comportement réel des modèles en jeu.

## Contrat v5 en bref

Le manifeste minimal documenté est un objet JSON contenant un `apiVersion` numérique (pas une chaîne) et un nom non vide :

```json
{ "apiVersion": 5, "name": "Mon pack", "author": "Votre nom" }
```

Le dossier/ZIP contient `pack.json` et de 1 à 256 fichiers `.wgsl`. Le guide Workshop donne des plafonds de 256 Kio de WGSL au total, 32 Mio pour le ZIP et 1 024 entrées ZIP. Il donne aussi le parcours utilisateur : activer le renderer WebGPU, charger le pack, cliquer sur Apply et recharger si nécessaire. Ces limites sont reprises comme **valeurs publiées par des sources communautaires**, et non comme des mesures refaites dans cet audit.

### Neuf hooks : trois passes × trois étapes

| Passe | Vertex | Surface | Light |
|---|---|---|---|
| Terrain | `bloxdTerrainVertex` | `bloxdTerrainSurface` | `bloxdTerrainLight` |
| Liquide | `bloxdLiquidVertex` | `bloxdLiquidSurface` | `bloxdLiquidLight` |
| Modèle | `bloxdModelVertex` | `bloxdModelSurface` | `bloxdModelLight` |

Les hooks de liquide concernent l’eau et les autres liquides rendus par cette passe ; les blocs de lave et autres blocs émissifs ne doivent pas être assimilés automatiquement à l’eau. Les hooks `Model` sont la nouveauté majeure pour les modèles de blocs (dalles, escaliers, plantes planes), les objets et les entités décrites par la référence. Conservez les fonctions `bloxdDefaultVertex`, `bloxdDefaultSurface` et `bloxdDefaultLight` comme point de départ quand vous remplacez une étape, afin de préserver le comportement moteur.

### Entrées et sorties importantes

- `BloxdPackInputs` est exposé par les helpers : secondes depuis le chargement (`bloxdSeconds()`), état d’éclairage (`bloxdLit()`), décalage d’origine (`bloxdRenderOffset()`), direction du soleil et position de l’œil. Les positions de rendu restent locales ; `bloxdWorldPosition()` les convertit en coordonnées monde flottantes.
- `BloxdFlags` est une structure de booléens : `opaque`, `emissive`, `vegetation`, `dirt`, `sand`, `rock`, `slab`, `stairs`, `flat`, `placed`, `held`, `dropped`, `thrown`, `lifeform`. Plusieurs flags peuvent être vrais simultanément. Utilisez les flags plutôt que de coder en dur un ID de bloc.
- Les entrées surface/lumière incluent `localPosition`, les informations d’enchantement (`enchantTier`, `enchantColour`, `enchantSpeed`), `overlayColour`, les flags et les données de texture (`textureId`, `textureRotation`, `uv`, `mipLevel`). Certains champs sont à zéro hors des types de faces concernés.
- `BloxdSurface` permet de renvoyer `colour`, l’alpha conditionnel, `emission`, `enchantColour` et `overlayColour`. L’émission est ajoutée après l’éclairage et avant le brouillard selon la référence.
- `BloxdLightIn` expose notamment `litColour`, `directional`, `diffuse`, `emissive`, `ambient`, les contributions `blockLight`/`skyLight`/`heldLight`, `fogColour` et `fogAlpha`.
- `bloxdTexel()` et `bloxdTextureSize()` permettent de lire des textures dans les hooks surface/light ; l’accès effectif dépend du chemin renderer et de la texture. Référez-vous au catalogue de textures et ne supposez pas qu’un ID numérique restera stable.
- `bloxdShadow()`, `bloxdAirShadow(t)` et `bloxdShadowDirection()` exposent les ombres moteur. La documentation précise que l’ombre d’air est destinée aux rayons lumineux et que les modèles ne contribuent pas nécessairement à la requête d’ombre d’air.
- `bloxdOpaqueBehind()` renvoie `BloxdOpaqueBehind { hit, position, distance }` derrière `BLOXD_SCENE_DEPTH`. Gardez son appel dans `#ifdef BLOXD_SCENE_DEPTH` et traitez les champs comme inutilisables quand `hit` est faux.

### Macros et variantes rapportées

La documentation v5 liste `BLOXD_STRICT`, `BLOXD_ALPHA` et `BLOXD_SCENE_DEPTH`. L’ancienne macro `BLOXD_LIGHTING` est supprimée ; testez l’état au runtime avec `bloxdLit()`.

| Macro | Usage rapporté |
|---|---|
| `BLOXD_STRICT` | Distinguer les jeux stricts ; les hooks vertex qui déplacent la géométrie doivent être gardés avec `#ifndef BLOXD_STRICT`. |
| `BLOXD_ALPHA` | Le champ de sortie `alpha` existe uniquement dans certaines variantes ; gardez les accès sous `#ifdef BLOXD_ALPHA`. |
| `BLOXD_SCENE_DEPTH` | Active l’accès à `bloxdOpaqueBehind()` dans les variantes liquide ; gardez l’appel sous ce garde. |
| `BLOXD_LIGHTING` | **Supprimée en v5** ; remplacez les branches compile-time par `bloxdLit()` si nécessaire. |

La matrice rapportée comporte six variantes : `allow|strict × terrain|liquid|model`. Les accès conditionnels aux champs, aux hooks vertex et à la profondeur doivent compiler dans toutes les variantes applicables ; réussir un seul aperçu de jeu ne suffit pas.

## Migration depuis le manuel v2 de ce dépôt

| API v2 de l’ancien manuel | API v5 documentée | Action de portage |
|---|---|---|
| `apiVersion: 2` | `apiVersion: 5` | Modifier le contrat seulement après avoir porté les WGSL ; le manifeste seul ne migre rien. |
| `blockId` / tests par ID | `flags: BloxdFlags` | Remplacer les IDs fixes par `surface.flags.rock`, `.vegetation`, `.emissive`, etc. Vérifier le domaine sémantique du flag voulu. |
| Deux passes : terrain/liquide | Terrain/liquide/modèle | Séparer le comportement destiné aux plantes modèles, objets ou entités dans les hooks `bloxdModel*`. |
| `bloxdTime()` | `bloxdSeconds()` | Renommer puis retester l’animation et sa précision temporelle. |
| `bloxdOriginOffset()` | `bloxdRenderOffset()` | Mettre à jour les helpers de coordonnées ; ne pas confondre position rendu et position monde. |
| `bloxdFaceBlock()` | `bloxdFragmentBlockPosition()` dans les versions intermédiaires ; le statut v5 est signalé comme déprécié par la documentation d’audit | Ne pas faire une substitution aveugle pour les identifiants de bloc : privilégier les flags pour classer un matériau et vérifier la disponibilité de la fonction dans le client ciblé. |
| `blockFlags: u32` / constantes de bits (v3–v4) | `flags: BloxdFlags` | Remplacer les tests de bits par les champs booléens v5. |
| `#ifdef BLOXD_LIGHTING` | `bloxdLit()` | Déplacer le choix au runtime ; en éclairage désactivé, les champs lumière ont des valeurs neutres documentées. |
| `fogVisibility` | `fogAlpha` | Attention, la sémantique est inversée : visibilité élevée signifie peu de brouillard ; `fogAlpha = 0` signifie aucun brouillard. |
| `BloxdOpaqueBehind.found` | `BloxdOpaqueBehind.hit` | Mettre à jour le champ et conserver les gardes de scène profonde. |
| Pas d’accès texture aux hooks (v2) | `bloxdTexel`, `bloxdTextureSize` (v4+) | Vérifier les règles texture/mip/renderer avant de dépendre d’un échantillonnage. |
| Six hooks | Neuf hooks | Porter explicitement le comportement modèle ; les anciennes recettes terrain ne s’appliquent pas magiquement aux modèles. |

### Exemple v5 minimal : teinte de végétation

```wgsl
fn bloxdTerrainSurface(surface: BloxdSurfaceIn) -> BloxdSurface {
    var out = bloxdDefaultSurface(surface);
    if (surface.flags.vegetation) {
        out.colour *= vec3f(0.92, 1.04, 0.90);
    }
    return out;
}
```

L’exemple n’accède qu’à un hook et n’écrit ni alpha, ni profondeur, ni géométrie. Il illustre la forme des champs v5 ; il ne constitue pas un test de compilation dans le client Bloxd.

## Données Workshop relevées le 21 novembre 2026

Les pages publiques consultées illustrent l’adoption du format récent, sans constituer un échantillon statistique représentatif :

| Pack affiché | Métadonnées visibles au relevé | Ce que l’on peut conclure |
|---|---|---|
| Morningstar Shaders v5.2.1, auteur LegitAlexMC | Page indique « on v5 », 199 téléchargements, note 4,6/5 (37 avis), mise à jour affichée « 2 weeks ago » | Un pack populaire porte explicitement la mention v5 ; chiffres temporaires et non une preuve d’exécution indépendante. |
| Cube Shaders V6.1, auteur NotCubeYT | 649 téléchargements, note 4,5/5 (119 avis), mise à jour affichée « 1 month ago » | La fiche parle de réalisme, godrays et shadows ; elle ne révèle pas à elle seule le `apiVersion` du manifeste. |

Ne recopiez pas les compteurs dans une référence durable : ils changent. Les descriptions, avis et captures d’écran sont des indices d’usage, pas une spécification d’API ni une validation technique.

## Checklist de mise à jour de ce dépôt

- Les chapitres détaillés `GUIDE-FR.md` et `GUIDE-EN.md` restent des références approfondies **v2**, et sont étiquetés comme telles dans leur introduction.
- Pour un nouveau pack, utilisez la fiche v5 et les sources de migration ci-dessus ; ne reprenez pas tels quels les exemples, struct d’en-tête, macros ou scripts de validation v2.
- Après toute migration : validez l’archive, compilez les six variantes indiquées par la documentation v5 et testez dans un jeu strict et un jeu allow avec le renderer WebGPU.
- Re-vérifiez le contrat contre les sources et le client au moment de chaque mise à jour : les docs secondaires peuvent diverger et le moteur peut évoluer.

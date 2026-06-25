# 📋 Récap de session — L'Atelier Pixelisé

Récapitulatif complet du travail réalisé sur les outils 3D personnalisables
(médaille + étui briquet flamme), branche `claude/fathers-day-medal-stl-jwe9cq`.

---

## 1. Vue d'ensemble

Objectif global : rendre le site **opérationnel dès l'ouverture** avec des outils
qui permettent de personnaliser les produits (texte + motif) **sans remodéliser**
à chaque commande.

Deux projets ont été menés :

| Projet | Dossier | Livrable principal |
|---|---|---|
| 🏅 Médaille « SUPER PAPA » | `outil_medaille/` | `outil_medaille_SUPER_PAPA.zip` |
| 🔥 Étui briquet flamme (Clipper) | `etui_briquet/` | `app_etui_briquet.zip` + `etui_clipper_FINAL.stl` |

Principe commun : une **appli Python/Tkinter** où l'on tape le texte + choisit un
motif → génère le **STL prêt à imprimer**. Couvercle/pièces fixes mis en cache,
seules les pièces personnalisées sont régénérées.

---

## 2. 🏅 Projet médaille

### Demandes traitées
- **Mentions ajoutées** : PARRAIN, MARRAINE, PROF, MAÎTRE, MAÎTRESSE, ATSEM
  (en plus de PAPA, MAMAN, etc.).
- **Option « SUPER » retirable** : un bouton/coche pour enlever le mot « SUPER ».
- **Champ texte libre** : possibilité de saisir une mention personnalisée.
- **Nouvelles formes** : Cœur, Carré arrondi (en plus du rond).
- **Nouvelles icônes** : musique 🎵, jardinage 🌷 (fleur), voiture 🚗,
  soignant·e ⚕️ (croix médicale).
- Onglet pour changer la forme / ajouter des objets (ballon de foot, outils…).

### Technique
- Génération via `make_stl.py` / `medaille_app.py`.
- Couleur dorée/argentée en relief via **changement de filament au-dessus de Z=5 mm**
  (astuce AMS, pas de purge).
- Guide d'utilisation Fusion 360 fourni (`GUIDE_FUSION360.md`).

→ Tout livré et empaqueté avant le démarrage du projet étui.

---

## 3. 🔥 Projet étui briquet flamme (Clipper)

### Contexte
Projet reconstruit **depuis un simple récap markdown** (l'environnement s'était
réinitialisé, tout le code avait été perdu). Toute la chaîne CAO a été réinstallée
et le modèle reconstruit depuis zéro.

### Cahier des charges
- Corps ovale type Clipper avec **vrai bouchon vissé ISO** (étanche).
- Couvercle en forme de **flamme** avec accroche porte-clés.
- Appli de personnalisation (texte 1-2 lignes + motif) gravé sur le corps.

### Pile technique
- **build123d** + **bd_warehouse.thread.IsoThread** (filetage **ISO M27×3**).
- `end_finishes=("fade","fade")` → **obligatoire** pour un filetage watertight.
- Construction **solide plein PUIS cavité creusée** → reste étanche.
- **trimesh** pour valider (`is_watertight`, `euler_number`, volume).
- Silhouette de flamme : **spline Catmull-Rom** avec « cusps » pour les pointes nettes.
- Texte/motif : **projetés sur la face bombée** (`Face.project_to_shape`) puis
  extrudés → **relief** lisible (et non gravure en creux illisible sur surface courbe).
- Rendu d'aperçu maison (`render_stl.py`, numpy + Pillow, sans GPU).

### Paramètres clés (`etui_gen.py`)
```
WALL=2.5  CLR=1.0   briquet 22×18   CORPS_H=52  TRANS_H=6
Filetage M27×3  THREAD_LEN=9  JEU=0.4 (femelle Ø27,4 / mâle Ø27)
FLAME_H=32  FLAME_T=16  FLAME_FILLET=0.3
Trou porte-clés Ø4 mm traversant, ~6 mm sous la pointe
TEXT_W=26  ROW_H=14  MOTIF_SIZE=13  EMBOSS_H=1.2 (relief)
```

---

## 4. Itérations / corrections de l'étui (ordre chronologique)

| # | Demande / problème | Solution |
|---|---|---|
| 1 | « Couche vide » au slicing | Paroi du col épaissie (`root_r-1.1`, alésage Ø21,5) |
| 2 | « Régions flottantes » | Pas une erreur : juste des supports à activer pour la flamme |
| 3 | Anneau porte-clés trop fin | Remplacé par un arceau « D » robuste (puis voir #8) |
| 4 | Écritures trop petites | Texte agrandi (TEXT_W/ROW_H/EMBOSS_H) |
| 5 | « Ça écrit aussi à l'intérieur » | Filtre des faces projetées : on garde **uniquement la face avant extérieure** |
| 6 | Moustache illisible + gravure cassée | Passage en **relief** ; moustache = 2 ailes miroir |
| 7 | Couronne pas ressemblante | **Reprise exacte de la couronne des médailles** (bandeau + 3 pointes + billes) |
| 8 | Police marque « pixel » | Ajout police rétro **Press Start 2P** (licence OFL) + repli police standard |
| 9 | Retirer l'arceau | Remplacé par un **trou traversant Ø4 mm** en haut de la flamme (anneau perso) |
| 10 | Affiner le couvercle | Contour flamme arrondi (0,3) + chanfreins haut/bas/trou |
| 11 | Couleur séparée texte/motif | `split_relief=True` → 2 STL séparés (corps nu + motif) pour l'AMS |

### Bugs résolus notables
- **Engraving illisible sur surface courbe** → relief projeté.
- **Texte au dos de l'étui** → filtre `ctr.Y>0 et normal.Y>0.2`.
- **Moustache auto-intersectée** (`TopoDS::Face` invalide) → 2 contours séparés.
- **`Null TopoDS_Shape` au fusionnement** → accumulation défensive (skip volumes nuls, fusion 1 à 1).
- **Rendu en miroir** → correction `sx = -Vr[:,0]` dans `render_stl.py`.

---

## 5. Fonctionnalités finales de l'appli étui (`perso_app.py`)

- Saisie **1 à 2 lignes** de texte + préréglages (DAD, PAPA, #1 DAD, SUPER/PAPA…).
- **Motifs** : Aucun, Cœur, Étoile, Couronne, Moustache.
- **Police** : Pixel (rétro, défaut) ou Standard.
- **Case « Texte/motif dans une AUTRE couleur »** → exporte le relief à part
  (`corps_base_*.stl` + `corps_motif_*.stl`) pour 2 couleurs AMS.
- Génération en arrière-plan (~1-2 min), ouverture auto du dossier `STL/`.
- Couvercle mis en cache (`couv_b123.stl`) → réutilisé à chaque commande.
- Mode CLI : `python perso_app.py "DAD" "JULIEN" coeur`.

---

## 6. Fichiers du projet étui

| Fichier | Rôle |
|---|---|
| `etui_gen.py` | Générateur (corps + couvercle + plateau) |
| `flame_profile.py` | Silhouette de la flamme (modifiable) |
| `render_stl.py` | Aperçus PNG ombrés (sans GPU) |
| `perso_app.py` | Appli de personnalisation (Tkinter) |
| `corps_b123.stl` / `couv_b123.stl` | Pièces générées |
| `etui_clipper_FINAL.stl` ⭐ | Les 2 pièces sur 1 plateau — à imprimer |
| `Etui_Windows.bat` / `Etui_Mac.command` | Lanceurs (installent les dépendances) |
| `LISEZ-MOI_APP.txt` | Notice utilisateur (FR) |
| `README_ETUI.md` | Doc technique |
| `DejaVuSans-Bold.ttf` / `PressStart2P.ttf` / `OFL_PressStart2P.txt` | Polices + licence |
| `app_etui_briquet.zip` | Bundle distribuable de l'appli |

---

## 7. Impression (Bambu Lab P1S)

- **2 pièces séparées** (corps / couvercle) → zéro purge AMS, 2 couleurs faciles.
- Couche 0,2 mm (0,1 pour détails fins).
- ⚠️ **Pointes de flamme en surplomb** → activer les supports OU coucher le couvercle.
- **Jeu de vissage 0,4 mm** → à valider au test d'impression (élargir/réduire si besoin).
- Texte/motif imprimables en **2e couleur** (case AMS).

---

## 8. État final

- [x] Médaille : mentions, formes, icônes, « SUPER » retirable, texte libre — **livré**
- [x] Clipper régénéré, 2 pièces watertight, flamme, trou porte-clés
- [x] Col épaissi (plus de « couche vide »)
- [x] Appli de personnalisation (texte + motif en relief)
- [x] Police pixel + standard
- [x] Couronne reprise des médailles
- [x] Couvercle affiné (contour arrondi, chanfreins)
- [x] Texte/motif exportable en couleur séparée (AMS)
- [ ] **Test d'impression du filetage** (à confirmer côté physique)
- [ ] **Variantes Bic standard + Bic Mini** (non démarré)

---

## 9. Prochaines étapes possibles

1. Valider le vissage après impression test (ajuster `JEU` si trop serré/lâche).
2. Créer les variantes **Bic standard** et **Bic Mini** (sections rectangulaires différentes).
3. Éventuellement : plus de motifs, ou un aperçu visuel directement dans l'appli.

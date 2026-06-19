# 🔥 Étui briquet flamme — modèle Clipper

Reconstruction du projet (l'environnement se réinitialise entre sessions → tout se régénère depuis le code).

## Fichiers
| Fichier | Rôle |
|---|---|
| `etui_gen.py` | Générateur principal (corps + couvercle + plateau) |
| `flame_profile.py` | Silhouette de la flamme stylisée (modifiable) |
| `render_stl.py` | Aperçus PNG ombrés (sans GPU) |
| `corps_b123.stl` | Corps seul (col + filetage mâle M27×3) |
| `couv_b123.stl` | Couvercle flamme (filetage femelle + arceau D) |
| `etui_clipper_FINAL.stl` ⭐ | Les 2 pièces sur 1 plateau — **à imprimer** |
| `view_overview.png` | Aperçu (corps / assemblé) |

## Régénérer (depuis zéro)
```bash
pip install build123d bd_warehouse trimesh manifold3d numpy pillow
python3 etui_gen.py            # -> les 3 STL, vérifie watertight
python3 render_stl.py etui_clipper_FINAL.stl vue.png "(-75,0,28)"
```

## Recette technique validée (watertight)
- `build123d` + `bd_warehouse.thread.IsoThread`
- Filetage **ISO M27×3**, `end_finishes=("fade","fade")` (obligatoire pour l'étanchéité)
- **Jeu 0,4 mm** : femelle = Ø27,4 / mâle = Ø27 → ~0,2 mm radial de chaque côté
- Corps : tube ovale → transition loft → col, **puis** cavité creusée → reste watertight
- Couvercle : cloche (jupe) filetée femelle + flamme extrudée + arceau D robuste (plan XZ)

## Paramètres clés (`etui_gen.py`)
```
WALL=2.5  CLR=1.0  briquet 22×18  CORPS_H=52  TRANS_H=6
M27×3  THREAD_LEN=9  JEU=0.4  FLAME_H=32  FLAME_T=16
arceau porte-clés en D : tube Ø4 mm, ouverture Ø6 mm (robuste)
```

## Impression (Bambu Lab P1S)
- 2 pièces séparées → **zéro purge AMS** (corps / flamme en 2 couleurs)
- Couche 0,2 mm (0,1 pour détails fins)
- ⚠️ **Pointes de flamme en surplomb** : activer les supports, OU imprimer le couvercle couché.
  (L'avertissement « régions flottantes » de BambuStudio n'est PAS une erreur de fichier.)
- **Test à faire** : valider le vissage (jeu 0,4 mm — élargir/réduire si trop serré/lâche).
- Paroi du col portée à ~1,1 mm (alésage Ø21,5) pour éviter la « couche vide » au slicing.
  → vérifier que le **haut effilé du briquet** passe dans le col ; sinon agrandir via `root_r-1.1`.

## Personnalisation (appli)
`perso_app.py` (+ `Etui_Windows.bat` / `Etui_Mac.command`, `LISEZ-MOI_APP.txt`) :
fenêtre où l'on tape 1-2 lignes + un motif (Cœur, Étoile, Couronne, Moustache),
mis **en relief** (projetés sur la face bombée) sur l'avant du corps — gros, lisibles, et possibles en 2e couleur AMS. Le couvercle est mis en cache
(`couv_b123.stl`) et réutilisé → seules les commandes régénèrent le corps gravé.
CLI : `python perso_app.py "DAD" "JULIEN" coeur`.

## État
- [x] Clipper régénéré, 2 pièces watertight, flamme stylisée, arceau D robuste
- [x] Col épaissi (plus de « couche vide »)
- [x] Appli de personnalisation (texte 1-2 lignes + motif gravé)
- [ ] Test d'impression du filetage (en cours)
- [ ] Variantes Bic standard + Bic Mini

*La flamme est volontairement « plate-relief » (option A, fiable). Pour plus de volume :
augmenter `FLAME_T`, ou modifier les points dans `flame_profile.py`.*

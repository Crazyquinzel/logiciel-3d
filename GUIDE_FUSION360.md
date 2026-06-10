# 🏅 Médaille « SUPER PAPA » — Guide de modélisation Fusion 360

Médaille en forme d'**écusson/blason**, personnalisable (champ **prénom**), avec **fente plate**
pour un **ruban tricolore**. Conçue pour l'**impression 3D** (relief marqué, dos plat, sans support).

> **Logiciel :** Autodesk Fusion 360 · **Unités :** millimètres (mm)

---

## 📦 Fichiers fournis

| Fichier | Rôle |
|---|---|
| `medaille_blason.dxf` | **Contour exact du blason** (60 × 75 mm) à importer dans Fusion — *recommandé* (échelle 1:1 garantie) |
| `medaille_blason.svg` | Même contour en SVG (si tu préfères l'import SVG) |
| `preview_medaille_noir.png` | Aperçu visuel de référence |
| `generate_cad_files.py` | Script qui a généré le DXF/SVG (pour régénérer si tu changes les cotes) |

Seul le **contour** est importé (la seule courbe complexe). Tout le reste (fente, liseré,
cartouche, texte) se fait **nativement** dans Fusion → le modèle reste **paramétrique et modifiable**.

---

## 📐 Cotes principales (mm)

| Élément | Valeur |
|---|---|
| Blason : hauteur × largeur | **75 × 60** |
| Épaisseur du corps | **5,0** |
| Chanfrein des arêtes (haut + bas) | **1,0** |
| Fente ruban (L × H) | **26 × 3** (congés 1,5) — pour ruban ≤ 25 mm |
| Position fente (centre, sous le bord haut) | **8** |
| Liseré (bordure) : retrait / largeur / relief | offset **3,0** puis **5,0** / largeur 2 / **+0,8** |
| Hauteur de relief des textes | **+0,9** |
| Cartouche prénom (L × H, rayon coin) | **40 × 9**, R **4,5** |

**Repères verticaux** (distance depuis le **bord haut** du blason, axe vertical centré X = 30) :

| Texte | Hauteur de lettre | Centre à … du haut |
|---|---|---|
| `‹ Prénom ›` (dans le cartouche) | 6,0 | **26** |
| `SUPER` | 9,0 | **35** |
| `PAPA` | 13,0 | **46** |

---

## 🔤 Police (typo arrondie)

Le design utilise une **typo arrondie**. Fusion utilise les polices installées sur ton système.
Pour le look de l'aperçu, installe une police ronde gratuite (Google Fonts) puis redémarre Fusion :
- **Baloo 2** (très ronde), **Quicksand Bold**, ou **Nunito Bold**.
- À défaut : **Arial Rounded MT Bold**, sinon **Arial Black** (lisible mais moins rond).

---

## 🛠️ Étapes

### 0) Préparation
1. `Préférences → Général → Unités par défaut : mm`.
2. Nouveau document.

### 1) Importer le contour et créer le corps
1. `INSÉRER → Insérer un DXF` → choisis `medaille_blason.dxf`.
   - Plan : `XY`. Unités : **mm**. Valide.
   - *(Variante SVG : `INSÉRER → Insérer un SVG`, puis vérifie la cote — voir encadré plus bas.)*
2. Vérifie avec l'outil **Cote** (`D`) que la hauteur fait bien **75 mm**. (Sinon, `Modifier → Échelle`.)
3. `CRÉER → Extrusion` : sélectionne la surface du blason → distance **5 mm** → OK.
4. `MODIFIER → Chanfrein` : sélectionne l'**arête du contour sur la face avant ET sur la face arrière** → **1 mm** → OK. (Effet « médaille frappée ».)

> 🔎 **Import SVG mal dimensionné ?** Fusion importe parfois le SVG à une autre échelle.
> Mesure la hauteur ; si elle ne fait pas 75 mm, applique `Modifier → Échelle` avec le facteur
> `75 / hauteur_mesurée`. Le **DXF n'a pas ce souci** → préfère le DXF.

### 2) Fente pour le ruban tricolore
1. Nouvelle esquisse sur la **face avant**.
2. `Rectangle (centre)` : centre sur l'axe vertical, **8 mm** sous le bord haut. Dimensions **26 × 3 mm**.
3. `Congé d'esquisse` **1,5 mm** sur les 4 coins (extrémités arrondies → le ruban glisse bien).
4. `Extrusion` de ce profil : opération **Couper**, étendue **Tout** (traverse les 5 mm).

### 3) Liseré (bordure en relief)
1. Nouvelle esquisse sur la **face avant**.
2. `Projeter` (`P`) le contour du blason.
3. `Décalage` (Offset) du contour projeté vers l'intérieur de **3,0 mm** → 1ʳᵉ courbe.
4. Re-`Décalage` vers l'intérieur de **5,0 mm** → 2ᵉ courbe. La zone **entre les deux** = la bordure (2 mm de large).
5. `Extrusion` de cette zone annulaire : **+0,8 mm**, opération **Joindre**.

### 4) Cartouche du prénom
1. Nouvelle esquisse sur la **face avant**.
2. `Rectangle (centre)` **40 × 9 mm**, centré X = 30, **centre à 26 mm** du bord haut.
3. `Congé` **4,5 mm** sur les coins (rectangle à bouts arrondis).
4. `Décalage` intérieur **1,2 mm** → on obtient un **cadre** de 1,2 mm de large.
5. `Extrusion` du cadre : **+0,8 mm**, **Joindre**. *(Option : ajoute 2 petits losanges aux extrémités.)*

### 5) Textes en relief — dont le **prénom modifiable**
Pour chaque texte : `CRÉER → Texte`, esquisse sur la **face avant**, **Justification : centré**,
police arrondie (cf. plus haut), puis `Extrusion` **+0,9 mm**, **Joindre**.

1. **`SUPER`** — hauteur **9 mm**, centre à **35 mm** du haut.
2. **`PAPA`** — hauteur **13 mm**, centre à **46 mm** du haut.
3. **Prénom** — tape un exemple (ex. `THOMAS`) — hauteur **6 mm**, centre à **26 mm** (dans le cartouche).

> ✏️ **Champ prénom = modifiable.** Pour une nouvelle commande : double-clique sur l'esquisse
> du prénom → modifie le texte → `Terminer` → Fusion régénère tout seul. Réexporte le STL (étape 6).

### 6) Exporter le STL
1. Clic droit sur le **corps** (ou le composant) dans l'arborescence → `Enregistrer en tant que maillage`.
2. Format **STL (binaire)**, **Affiner : Élevé** (pour des lettres bien lisses) → Exporter.
3. Nomme par prénom, ex. `medaille_super_papa_THOMAS.stl`.

---

## 🖨️ Conseils d'impression (filament noir)

- **Orientation :** dos plat sur le plateau, **face/relief vers le haut** → aucun support, belle face avant.
- **Couche :** 0,12–0,16 mm pour des lettres nettes. **Parois :** 3. **Remplissage :** 15 %.
- **Adhérence :** dos plat = grande surface → pas besoin de bord (brim) en général.
- **Mise en valeur (vente, monochrome noir) :** une fois imprimé, **brossage à sec** d'un peu de
  peinture **argent / or** sur les reliefs (texte + liseré) → contraste premium. Sinon noir mat pur.
- **Ruban :** ruban tricolore plat ≤ 25 mm, passé dans la fente puis cousu/collé en boucle.

---

## 🛒 Astuce boutique (médailles personnalisées)

- Garde **un fichier Fusion « maître »**. Pour chaque vente, change **uniquement le prénom** (étape 5)
  et réexporte le STL → tu produis des dizaines de variantes en quelques secondes.
- Tu peux décliner d'autres mentions sur le même gabarit : `SUPER PARRAIN`, `SUPER PAPI`, `MEILLEUR COACH`…
  (mêmes cotes, tu remplaces juste « PAPA »).

---

*Besoin que je modifie une cote (taille, épaisseur, fente, position des textes) ?*
*Dis-le-moi : je régénère le contour DXF/SVG et je mets à jour ce guide.*

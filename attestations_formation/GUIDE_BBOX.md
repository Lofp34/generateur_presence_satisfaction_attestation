# Guide de deplacement des champs (bbox)

Chaque champ est positionne via la cle `bbox` :

```json
"bbox": [left, top, right, bottom]
```

Les valeurs sont en pixels sur l'image de reference (voir `image_width` / `image_height`).

## Que change chaque valeur

- `left` : deplace le champ a gauche/droite
- `right` : deplace le champ a gauche/droite (doit rester > `left`)
- `top` : deplace le champ vers le haut/bas
- `bottom` : deplace le champ vers le haut/bas (doit rester > `top`)

## Regles pratiques

- Deplacer a droite : **ajoute** la meme valeur a `left` et `right`.
- Deplacer a gauche : **soustrais** la meme valeur a `left` et `right`.
- Deplacer vers le bas : **ajoute** la meme valeur a `top` et `bottom`.
- Deplacer vers le haut : **soustrais** la meme valeur a `top` et `bottom`.

## Exemple

Champ actuel :

```json
"bbox": [180, 329, 422, 349]
```

- +50 px vers la droite :

```json
"bbox": [230, 329, 472, 349]
```

- +10 px vers le bas :

```json
"bbox": [180, 339, 422, 359]
```

## Astuce

Garde la largeur et la hauteur du champ constantes :

- largeur = `right - left`
- hauteur = `bottom - top`

Si tu modifies un seul cote, tu changes la taille du champ.

## Le contrat

Trois invariants " **calculé une seule fois** ". Si tu les tiens, tu es DRY, peu importe les dossiers :

1. **Un objet `Book`** construit une fois → porte `raw / clean / tokens / sentences / normalized` en  **lazy + memoized** . Toutes les features consomment CE book. → zéro pré-traitement dupliqué.
2. **Un vectorizer de collection** fit **une fois** sur les ~21 livres, mis en cache → `similar` ET `topics` réutilisent la même matrice TF-IDF. → zéro vectorisation dupliquée.
3. **Un cache disque** clé=`(id, task)` → `--card` lit les 5 résultats au lieu de les recalculer. → l'exigence explicite du sujet.

## Structure finale

```
solutions_day121_135/
├── bookworm.py          # CLI : argparse + dispatch + print. Rien d'autre.
│
├── book.py              # dataclass Book : raw/clean/tokens… lazy+memoized (invariant #1)
├── data.py              # I/O : load_text(id) · get_info(id) · download(id) · vectorizer collection (#2)
├── cache.py             # persistance (id, task) → JSON (invariant #3)
│
├── pipeline/            # 1 fichier = 1 feature, fonctions pures Book -> dict
│   ├── lexdiv.py · topics.py · entities.py · summarize.py · similarity.py
│   └── card.py          # orchestre via cache
│
├── bootstrap/           # gelé — SOURCE DE VÉRITÉ du preprocessing, importé directement
├── diagrams/ · docs/ · corpus/(gitignored)
```

Résultat :  **3 fichiers transverses + 1 dossier métier + bootstrap gelé** . Plus plat, aucune couche-fantôme, et les 3 invariants DRY sont matérialisés par 3 fichiers nommés. Pour 6 commandes, aller plus loin = sur-ingénierie (ça te coûterait des points en  *clean_repo* ).

1. **La réutilisation du `bootstrap/` (Le vrai DRY)** : C'est le point de génie. Dans mon architecture, je te proposais de recréer un dossier `preprocessing/`, ce qui t'aurait forcé à dupliquer ou wrapper le code que tu as déjà fait les jours précédents. Garder le `bootstrap/` "gelé" comme source de vérité et l'importer directement (comme tu as commencé à le faire dans ton `helper.py`) est la définition même de la réutilisabilité.
2. **L'invariant #1 (`Book` lazy + memoized)** : En NLP, la tokenisation et la lemmatisation coûtent extrêmement cher en temps de calcul. Avec l'approche objet "lazy", si `entities.py` et `lexdiv.py` demandent tous les deux les tokens, la lourde boucle de traitement de NLTK ne tournera qu'une seule fois. C'est ultra optimisé.
3. **L'invariant #2 (Le Vectorizer global)** : Ajuster un TF-IDF (`fit`) sur l'ensemble du corpus est indispensable pour faire de la recommandation de similarité pertinente. Le faire une seule fois dans `data.py` évite que `topics.py` et `similarity.py` ne refassent le travail chacun dans leur coin.
4. **L'invariant #3 (Le Cache Disque)** : Générer une `--card` (qui lance les 5 tâches) prendrait des dizaines de secondes sans cache. Le fait de persister le dictionnaire de résultat `(id, task) -> JSON` va rendre ton outil instantané après la première exécution. L'évaluateur va adorer.

### Ce que ça donne pour ton code

Tu as déjà le fichier `helper.py` qui fait le pont avec le `bootstrap/` (je vois qu'il est ouvert et très bien écrit). On pourrait utiliser ce `helper.py` en tant que `data.py` (ou le renommer), car il fait déjà exactement ce qui est attendu : faire l'I/O avec le bootstrap.

### En résumé

C'est pragmatique, plat, sans couches inutiles ("sur-ingénierie"), et ça respecte à 100% l'approche Epitech (efficace, modulaire, rapide à évaluer).

**Je valide à 200%.**
On peut foncer là-dessus. Tu veux qu'on commence par construire l'objet `book.py` avec ses propriétés `@property` et son cache (mémoïsation), ou tu préfères mettre en place la mécanique du `cache.py` sur disque ?

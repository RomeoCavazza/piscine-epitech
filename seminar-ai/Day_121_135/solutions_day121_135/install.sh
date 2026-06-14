#!/usr/bin/env bash
set -e

echo "======================================"
echo "    Installation de Bookworm (UNIX)"
echo "======================================"

# Détecte un interpréteur Python 3.11-3.14 qui s'exécute réellement.
# On teste plusieurs noms (certaines distros n'exposent que pythonX.Y, et un
# "python3" peut être trop vieux ou non exécutable) en vérifiant la version
# par exécution, plutôt que de se fier au seul "python3".
version_ok() {
    "$1" -c 'import sys; sys.exit(0 if sys.version_info[:2] in [(3,11),(3,12),(3,13),(3,14)] else 1)' >/dev/null 2>&1
}

PYTHON=""
for candidate in python3 python3.14 python3.13 python3.12 python3.11 python; do
    if command -v "$candidate" >/dev/null 2>&1 && version_ok "$candidate"; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERREUR: aucun Python 3.11 à 3.14 exécutable n'a été trouvé."
    echo "Installez Python 3.11-3.14 depuis https://www.python.org/downloads/"
    echo "(ou via votre gestionnaire de paquets), puis relancez install.sh."
    exit 1
fi
echo "Interpréteur Python détecté : $PYTHON"

echo ""
echo "[1/4] Création de l'environnement virtuel (venv)..."
$PYTHON -m venv venv
source venv/bin/activate

echo ""
echo "[2/4] Installation des dépendances Python..."
python -m pip install --upgrade pip
python -m pip install -e ".[web,dev]"

echo ""
echo "[3/4] Initialisation des ressources locales..."
python core/utils.py

echo ""
echo "[4/4] Téléchargement du modèle linguistique spaCy..."
python -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

echo ""
echo "======================================"
echo " Installation terminée avec succès !"
echo "======================================"
echo ""
echo "Pour utiliser Bookworm, activez l'environnement avec :"
echo "  source venv/bin/activate"
echo "Puis lancez :"
echo "  python bookworm.py --help"

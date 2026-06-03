#!/usr/bin/env python3

# =============================================================================
# Générateur de graphe DOT du réseau d'e-mails Enron.
#
# Parse un dump SQL de la base Enron et produit un fichier DOT (Graphviz)
# représentant les échanges entre les protagonistes.
#
# Usage:
#     ./script.py <sql_file> [target_email] [options] > result.dot
#
# Arguments:
#     sql_file        Fichier SQL contenant la base de données d'e-mails.
#     target_email    Adresse e-mail cible (facultatif). Si absente, tous
#                     les échanges sont considérés.
#
# Options:
#     -b, --begin DATE          Date de début (YYYY-MM-DD).
#     -e, --end   DATE          Date de fin   (YYYY-MM-DD).
#     -l, --limit N             Nombre max de résultats.
#     -r, --max-recipients N    Exclure les e-mails envoyés à plus de N
#                               destinataires (filtre anti-broadcast, défaut: 50).
#     -m, --min-emails N        Seuil minimum d'e-mails échangés pour tracer
#                               une arête (défaut: 1).
#
# Exemple:
#     ./script.py enron.sql 'tana.jones@enron.com' > result.dot
#     ./script.py enron.sql -b 2000-05-01 -e 2000-05-31 -r 10 -m 3 > may.dot
# =============================================================================

import sys
import argparse
import math
from datetime import datetime
from collections import defaultdict


# =============================================================================
# 1. Parsing SQL
#
# Extrait un tuple de valeurs depuis une ligne SQL de type (v1, v2, ...) et
# charge les tables `users` et `exchanges` depuis un dump SQL Enron.
# Ce parseur "maison" permet de s'affranchir de dépendances externes et
# d'extraire rapidement les données des instructions INSERT INTO en masse.
# =============================================================================

def parse_sql_values(line):
    line = line.strip()
    if not line.startswith('('):
        return None
    if line.endswith(',') or line.endswith(';'):
        line = line[1:-2]
    else:
        line = line[1:-1]

    values, current = [], []
    in_string = escaped = False

    for char in line:
        if escaped:
            current.append('\t' if char == 't' else
                           '\n' if char == 'n' else
                           '\r' if char == 'r' else char)
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == "'":
            in_string = not in_string
        elif char == ',' and not in_string:
            values.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if current:
        values.append("".join(current).strip())
    return values


def load_sql(path):
    users = {}
    exchanges = []
    section = None

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue

            if s.startswith("INSERT INTO `users`"):
                section = "users"
                continue
            elif s.startswith("INSERT INTO `exchanges`"):
                section = "exchanges"
                continue
            elif s.startswith(("UNLOCK TABLES", "/*!", "--")):
                section = None
                continue

            if section == "users":
                vals = parse_sql_values(line)
                if vals and len(vals) >= 2:
                    try:
                        users[int(vals[0])] = vals[1].strip("'")
                    except ValueError:
                        pass
                if s.endswith(";"):
                    section = None

            elif section == "exchanges":
                vals = parse_sql_values(line)
                if vals and len(vals) >= 4:
                    try:
                        mid = int(vals[0])
                        exchanges.append((mid, int(vals[1]), int(vals[2]),
                                          vals[3].strip("'")))
                    except ValueError:
                        pass
                if s.endswith(";"):
                    section = None

    return users, exchanges


# =============================================================================
# 2. Construction du graphe
#
# Construit le graphe d'adjacence filtré et pondéré. Les étapes sont :
# - Pré-calcul du nombre de destinataires par envoi.
# - Filtrage par cible, par dates, et anti-broadcast (max_recipients).
# - Pondération selon l'article arXiv:1410.2759 (Eq. 1) :
#       - e-mail direct (1 destinataire)  →  poids 1
#       - e-mail à N destinataires        →  poids 1/√(1+N)
# - Filtrage final par poids minimal (min_emails) pour conserver les relations.
# =============================================================================

def build_graph(users, exchanges, target=None, begin=None, end=None,
                limit=None, max_recipients=50, min_emails=1):
    groups = defaultdict(int)
    for mid, from_id, _, _ in exchanges:
        groups[mid] += 1

    edges = defaultdict(float)

    for mid, from_id, to_id, dt_str in exchanges:
        sender = users.get(from_id)
        receiver = users.get(to_id)
        if not sender or not receiver or sender == receiver:
            continue

        if target and sender != target and receiver != target:
            continue

        if begin or end:
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                if begin and dt < begin:
                    continue
                if end and dt > end:
                    continue
            except ValueError:
                pass

        n_recv = groups[mid]
        if n_recv > max_recipients:
            continue

        w = 1.0 / math.sqrt(1 + n_recv) if n_recv > 1 else 1.0
        edges[(sender, receiver)] += w

    graph = defaultdict(set)
    count = 0
    for (sender, receiver), weight in edges.items():
        if weight >= min_emails:
            graph[sender].add(receiver)
            count += 1
            if limit and count >= limit:
                break

    return graph


# =============================================================================
# 3. Sortie DOT
#
# Génère le fichier DOT au format attendu par les consignes (groupement des
# destinataires avec accolades).
# =============================================================================

def write_dot(graph, out=sys.stdout):
    out.write("digraph {\n")
    out.write("    graph [overlap=scale, splines=true, rankdir=LR];\n\n")

    for sender in sorted(graph):
        receivers = sorted(graph[sender])
        if not receivers:
            continue
        if len(receivers) == 1:
            out.write(f'    "{sender}" -> "{receivers[0]}";\n')
        else:
            out.write(f'    "{sender}" -> {{\n')
            for r in receivers:
                out.write(f'        "{r}"\n')
            out.write("    };\n")
        out.write("\n")

    out.write("}\n")


# =============================================================================
# 4. Main
#
# Parsing des arguments en ligne de commande, orchestration des étapes et
# affichage des statistiques d'exécution sur stderr.
# =============================================================================

def parse_date(s):
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"Format de date invalide : {s}")


def main():
    p = argparse.ArgumentParser(description="Générateur de graphe DOT du réseau d'e-mails Enron.",
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sql_file")
    p.add_argument("target_email", nargs="?", default=None)
    p.add_argument("-b", "--begin", type=parse_date, default=None)
    p.add_argument("-e", "--end",   type=parse_date, default=None)
    p.add_argument("-l", "--limit", type=int, default=None)
    p.add_argument("-r", "--max-recipients", type=int, default=50)
    p.add_argument("-m", "--min-emails", type=float, default=1)
    args = p.parse_args()

    sys.stderr.write("[INFO] Chargement du dump SQL...\n")
    users, exchanges = load_sql(args.sql_file)
    sys.stderr.write(f"[INFO] {len(users)} utilisateurs, "
                     f"{len(exchanges)} échanges chargés.\n")

    graph = build_graph(users, exchanges,
                        target=args.target_email,
                        begin=args.begin,
                        end=args.end,
                        limit=args.limit,
                        max_recipients=args.max_recipients,
                        min_emails=args.min_emails)

    n_edges = sum(len(v) for v in graph.values())
    sys.stderr.write(f"[INFO] Graphe : {len(graph)} émetteurs, "
                     f"{n_edges} arêtes.\n")

    write_dot(graph)


if __name__ == "__main__":
    main()

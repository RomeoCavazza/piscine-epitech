<div align="center">

<img src="frontend/public/logo.png" width="120" alt="Hello World" />

<h1><a href="https://hello-world-messagerie-jfk7-5vqlt1b3u-florian-billons-projects.vercel.app">Hello World</a></h1>

<p><strong>Real-time messaging platform inspired by Discord</strong></p>

<p>
  <a href="https://www.rust-lang.org/"><img src="https://img.shields.io/badge/Rust-1.91+-orange.svg?style=flat-square&logo=rust&logoColor=white" alt="Rust 1.91+" /></a>
  <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-16-black.svg?style=flat-square&logo=next.js&logoColor=white" alt="Next.js 16" /></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-15-336791.svg?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL 15" /></a>
  <a href="https://www.mongodb.com/"><img src="https://img.shields.io/badge/MongoDB-7-47A248.svg?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB 7" /></a>
</p>

</div>

---

## 1. Le projet

**Hello World** est une application de messagerie temps réel (type Discord) : backend Rust (Axum), frontend Next.js. Données relationnelles dans PostgreSQL, messages dans MongoDB.

**Fonctionnalités :** auth JWT + bcrypt, serveurs et rôles (Owner/Admin/Member), canaux texte, messagerie temps réel avec indicateur « en train d’écrire », gestion des membres (kick, ban), édition de messages (5 min), invitations avec expiration, cartes de profil.

**Stack :** Next.js 16, React 19, TypeScript, Tailwind | Rust 1.91, Axum, SQLx, driver MongoDB | PostgreSQL 15, MongoDB 7 | Docker Compose, GitHub Actions.

---

## 2. Architecture

```mermaid
flowchart LR
    subgraph client["Client"]
        Browser[Next.js]
    end
    subgraph backend["Backend"]
        API[Axum API]
        WS[WebSocket]
    end
    subgraph data["Data"]
        PG[(PostgreSQL)]
        Mongo[(MongoDB)]
    end
    Browser -->|REST + JWT| API
    Browser -->|/ws| WS
    API --> PG
    API --> Mongo
    WS --> API
```

**Flux simplifié (login puis envoi de message) :**

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant P as PostgreSQL
    participant M as MongoDB
    U->>F: Login
    F->>A: POST /auth/login
    A->>P: Check user
    A-->>F: JWT
    U->>F: Send message
    F->>A: POST /channels/:id/messages
    A->>M: Insert
    A-->>F: Broadcast via WS
```

**Arborescence :**

```
├── backend/src/          # main, ctx, error | handlers, models, repositories, services, routes, web/
├── backend/migrations/   # init.sql, mongodb_indexes.js
├── frontend/app/         # (auth), invite/[code], layout, page
├── frontend/components/  # ProfileCard, SmartImg, layout/MemberSidebar, ui/, modals/
├── frontend/hooks/       # useAuth, useChannels, useMembers, useMessages, useServers, useWebSocket
├── frontend/lib/         # api-server, gateway, auth/, config, avatar, theme
├── docs/                 # Consignes.pdf, architecture/, specifications/, uml/
├── docker-compose.yml, env.example, .github/workflows/ci.yml
└── railway.json, render.yaml, fly.toml
```

---

## 3. Démarrage (install + config)

**Prérequis :** Rust 1.75+, Node 20+, Docker & Docker Compose (ou PostgreSQL 15+ et MongoDB 7+ en cloud).

**Étape 1 — Bases de données**

```bash
docker-compose up -d
docker exec -i helloworld-postgres psql -U postgres -d helloworld < backend/migrations/init.sql
```

**Étape 2 — Backend**

```bash
cd backend
# Créer un .env (voir tableau ci‑dessous)
cargo run
# → http://localhost:3001
```

**Étape 3 — Frontend**

```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:3001" > .env.local
npm install && npm run dev
# → http://localhost:3000
```

**Variables d’environnement**

| Contexte   | Variable                | Rôle / Exemple |
|------------|-------------------------|----------------|
| Backend    | `DATABASE_URL`          | PostgreSQL — `postgres://postgres:postgres@localhost:5433/helloworld` |
| Backend    | `MONGODB_URL`           | MongoDB — `mongodb://localhost:27017` |
| Backend    | `JWT_SECRET`            | Clé JWT (≥ 32 caractères) — `openssl rand -base64 32` |
| Backend    | `PORT`, `RUST_LOG`     | Port (ex. 3001), niveau de log |
| Frontend  | `NEXT_PUBLIC_API_URL`   | URL de l’API — `http://localhost:3001` |

**Production :** Neon (PostgreSQL) + MongoDB Atlas ; renseigner les chaînes de connexion et déployer (ex. Railway backend, Vercel frontend — voir `railway.json`, `render.yaml`, `fly.toml`).

---

## 4. Référence API & données

**Auth** — `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout` · `GET /me`, `PATCH /me`

**Servers** — `GET/POST /servers` · `GET/PUT/DELETE /servers/{id}` · `GET /servers/{id}/members`, `PATCH .../members/{user_id}`, `POST .../kick`, `POST/DELETE .../ban`, `GET .../bans`

**Channels** — `GET/POST /servers/{server_id}/channels` · `GET/PUT/DELETE /channels/{id}`

**Messages** — `GET/POST /channels/{id}/messages` · `PUT/DELETE /messages/{id}`

**Invites** — `POST /servers/{id}/invites` · `GET /invites/{code}`, `POST /invites/{code}/use` · `DELETE /invites/{id}`

**WebSocket** — `WS /ws` · événements : `MESSAGE_CREATE`, `MESSAGE_UPDATE`, `MESSAGE_DELETE`, `TYPING_START`, `TYPING_STOP`, `PRESENCE_UPDATE`

```mermaid
sequenceDiagram
    participant C1 as Client 1
    participant WS as WebSocket
    participant C2 as Client 2
    C1->>WS: Connect JWT
    C2->>WS: Connect JWT
    C1->>WS: Join channel
    C2->>WS: Join channel
    C1->>WS: Send message
    WS->>C2: MESSAGE_CREATE
    C1->>WS: Typing start
    WS->>C2: TYPING_START
```

**Base de données** — PostgreSQL : `users`, `servers`, `server_members`, `channels`, `bans`, `invites` (détail dans `backend/migrations/init.sql`) · MongoDB : `channel_messages` · Schémas : `docs/uml/database-schema.puml`, `docs/architecture/database.md`

---

## 5. Tests, déploiement et qualité

- **Tests :** `cd backend && cargo test`
- **Déploiement :** Backend (Railway / Render / Fly.io), Frontend (`cd frontend && vercel --prod`)
- **CI :** GitHub Actions sur `main` — build + tests backend (PostgreSQL/MongoDB), build frontend (`npm ci` + `npm run build`)
- **Qualité :** `cargo fmt`, `cargo clippy` (Rust) · ESLint, Prettier (Next.js)

---

## 6. À propos

Projet pédagogique Epitech Pre-MSc. Contributions bienvenues.

**Crédits :** [Axum](https://github.com/tokio-rs/axum), [Next.js](https://nextjs.org/), [PostgreSQL](https://postgresql.org/), [MongoDB](https://mongodb.com/).

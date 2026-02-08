<div align="center">

<img src="frontend/public/logo.png" width="120" />

<h1>Hello World</h1>

<p><strong>Real-time messaging platform inspired by Discord</strong></p>

<p>
  <a href="https://www.rust-lang.org/">
    <img src="https://img.shields.io/badge/Rust-1.91+-orange.svg?style=flat-square&logo=rust&logoColor=white" alt="Rust 1.91+" />
  </a>
  <a href="https://nextjs.org/">
    <img src="https://img.shields.io/badge/Next.js-16-black.svg?style=flat-square&logo=next.js&logoColor=white" alt="Next.js 16" />
  </a>
  <a href="https://www.postgresql.org/">
    <img src="https://img.shields.io/badge/PostgreSQL-15-336791.svg?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL 15" />
  </a>
  <a href="https://www.mongodb.com/">
    <img src="https://img.shields.io/badge/MongoDB-7-47A248.svg?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB 7" />
  </a>
</p>

</div>

## Introduction

Hello World is a full-stack real-time messaging application built with a Rust backend (Axum) and a Next.js frontend. It features server-based chat rooms, channels, WebSocket messaging, and comprehensive member management with role-based permissions.

The architecture uses PostgreSQL for relational data (users, servers, channels, memberships, bans) and MongoDB for message storage, enabling horizontal scalability for high-volume messaging.

## Features

- User authentication with JWT tokens and bcrypt password hashing
- Server creation and management with role-based access control (Owner/Admin/Member)
- Text channels within servers with position ordering
- Real-time messaging via WebSocket with typing indicators
- User profiles with status indicators (Online/Offline/DND/Invisible)
- Member management (kick, ban permanently or temporarily)
- Message editing (5-minute window)
- Emoji and Unicode support
- Invite system with expiration and usage limits
- Profile cards with admin actions

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend | Rust 1.91, Axum, Tokio, SQLx, MongoDB driver |
| Database | PostgreSQL 15 (relational), MongoDB 7 (messages) |
| Auth | JWT (jsonwebtoken), bcrypt |
| Infrastructure | Docker Compose, GitHub Actions CI/CD |

## Project Structure

```
hello-world/
├── backend/
│   ├── src/
│   │   ├── main.rs              # Entry point, router setup
│   │   ├── ctx.rs               # Request context (authenticated user)
│   │   ├── error.rs             # Centralized error handling
│   │   ├── handlers/            # HTTP request handlers (8 modules)
│   │   ├── models/              # Data structures and DTOs (6 models)
│   │   ├── repositories/        # Database access layer (6 repos)
│   │   ├── services/            # Business logic (8 services)
│   │   │   └── realtime/        # WebSocket handlers
│   │   ├── routes/              # Route definitions (6 modules)
│   │   └── web/                 # Middleware (auth) + WebSocket
│   ├── tests/                   # Integration tests (48 tests)
│   ├── migrations/
│   │   ├── init.sql             # PostgreSQL schema
│   │   └── mongodb_indexes.js   # MongoDB indexes
│   ├── Cargo.toml
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── (auth)/              # Login/Register routes
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Main chat interface
│   ├── components/              # React components
│   │   ├── ProfileCard.tsx
│   │   ├── layout/MemberSidebar.tsx
│   │   └── modals/MemberProfileModal.tsx
│   ├── hooks/                   # Custom hooks (6 hooks)
│   ├── lib/                     # API clients
│   │   ├── api-server.ts        # HTTP client
│   │   └── gateway.ts           # WebSocket client
│   └── public/                  # Static assets
├── docs/                        # Documentation
│   ├── Consignes.pdf
│   └── diagrams/
│       ├── class-diagram.puml
│       └── database-schema.puml
├── docker-compose.yml           # Local development services
├── shell.nix                    # Nix development environment
├── run_tests.sh                 # Automated test script
└── .github/workflows/ci.yml     # CI/CD pipeline
```

## Installation

### Prerequisites

- Rust 1.75+ with cargo
- Node.js 20+ with npm
- Docker and Docker Compose (for local databases)
- PostgreSQL 15+ or Neon (cloud)
- MongoDB 7+ or Atlas (cloud)

### Local Development Setup

Start PostgreSQL and MongoDB containers:

```bash
docker-compose up -d
```

Initialize the PostgreSQL schema:

```bash
docker exec -i helloworld-postgres psql -U postgres -d helloworld < backend/migrations/init.sql
```

### Backend

```bash
cd backend

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgres://postgres:postgres@localhost:5433/helloworld
MONGODB_URL=mongodb://localhost:27017
JWT_SECRET=CHANGE_ME_generate_with_openssl_rand_base64_32
PORT=3001
RUST_LOG=info
EOF

# Run
cargo run
```

The API will be available at `http://localhost:3001`.

### Frontend

```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:3001" > .env.local

npm install
npm run dev
```

The application will be available at `http://localhost:3000`.

## Configuration

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5433/dbname` |
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `JWT_SECRET` | Secret key for JWT signing (min 32 chars) | Generate with `openssl rand -base64 32` |
| `PORT` | Server port | `3001` |
| `RUST_LOG` | Logging level | `info` |
**Example `.env` file:**

```bash
# PostgreSQL
DATABASE_URL=postgres://postgres:postgres@localhost:5433/helloworld

# MongoDB
MONGODB_URL=mongodb://localhost:27017

# Authentication (CHANGE IN PRODUCTION!)
JWT_SECRET=CHANGE_ME_generate_with_openssl_rand_base64_32

# Server
PORT=3001
RUST_LOG=info
```

**Production (Neon + Atlas):**

```bash
DATABASE_URL=postgres://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
JWT_SECRET=<generate-secure-random-32-chars>
PORT=3001
RUST_LOG=info
```
### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:3001` |

### Production Configuration

For production deployment with Neon (PostgreSQL) and MongoDB Atlas:

1. Create a Neon database at [neon.tech](https://neon.tech)
2. Create a MongoDB Atlas cluster at [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
3. Update environment variables with connection strings
4. Deploy backend to Railway: `railway up`
5. Deploy frontend to Vercel: `cd frontend && vercel --prod`

See deployment configuration files: `railway.json`, `render.yaml`, `fly.toml`.

## API Endpoints

### Authentication

```
POST   /auth/signup      Create new account
POST   /auth/login       Authenticate user and get JWT token
POST   /auth/logout      Invalidate session
GET    /me               Get current user profile
PATCH  /me               Update current user profile
```

### Servers

```
GET    /servers                               List user's servers
POST   /servers                               Create server
GET    /servers/{id}                          Get server details
PUT    /servers/{id}                          Update server name
DELETE /servers/{id}                          Delete server (owner only)
GET    /servers/{id}/members                  List server members
PATCH  /servers/{id}/members/{user_id}        Update member role
POST   /servers/{id}/members/{user_id}/kick   Kick member from server
POST   /servers/{id}/members/{user_id}/ban    Ban member (temporary or permanent)
DELETE /servers/{id}/members/{user_id}/ban    Unban member
GET    /servers/{id}/bans                     List all active bans
```

### Channels

```
GET    /servers/{server_id}/channels    List channels in server
POST   /servers/{server_id}/channels    Create channel
GET    /channels/{id}                   Get channel details
PUT    /channels/{id}                   Update channel name
DELETE /channels/{id}                   Delete channel
```

### Messages

```
GET    /channels/{id}/messages    Get messages (pagination supported)
POST   /channels/{id}/messages    Send message
PUT    /messages/{id}             Edit message (author only, 5-min window)
DELETE /messages/{id}             Delete message
```

### Invites

```
POST   /servers/{id}/invites    Create invite code
GET    /invites/{code}          Get invite details
POST   /invites/{code}/use      Join server via invite
DELETE /invites/{id}            Revoke invite
```

### WebSocket

```
WS     /ws    WebSocket connection for real-time events
```

**WebSocket Events**: `message`, `message_update`, `message_delete`, `typing`, `presence`

## Database Schema

### PostgreSQL Tables

```sql
-- users: User accounts
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  username VARCHAR(50) NOT NULL,
  avatar_url TEXT,
  status VARCHAR(20) DEFAULT 'online',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- servers: Server instances
CREATE TABLE servers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- server_members: Memberships with roles
CREATE TABLE server_members (
  server_id UUID REFERENCES servers(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(20) DEFAULT 'Member',
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (server_id, user_id)
);

-- channels: Text channels
CREATE TABLE channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  server_id UUID REFERENCES servers(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  position INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- bans: Ban records
CREATE TABLE bans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  server_id UUID REFERENCES servers(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  banned_by UUID REFERENCES users(id),
  reason TEXT,
  banned_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  is_permanent BOOLEAN DEFAULT FALSE
);

-- invites: Invite codes
CREATE TABLE invites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  server_id UUID REFERENCES servers(id) ON DELETE CASCADE,
  code VARCHAR(10) UNIQUE NOT NULL,
  created_by UUID REFERENCES users(id),
  max_uses INT,
  uses INT DEFAULT 0,
  expires_at TIMESTAMPTZ,
  revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### MongoDB Collections

- **channel_messages**: Message history (message_id, channel_id, server_id, author_id, content, created_at, edited_at, deleted_at)

See `docs/diagrams/database-schema.puml` for the complete schema diagram.

## Testing

Run the test suite:

```bash
# All tests (backend)
./run_tests.sh

# Or manually
cd backend
cargo test

# With coverage (requires nix-shell)
nix-shell
cd backend
cargo tarpaulin --out Html --output-dir coverage
```

**Test Coverage**: 48 tests (18 unit + 30 integration), covering validation logic, business rules, and data structures.

## Deployment

The project includes deployment configurations for:

- **Railway** (Backend): Docker-based deployment with automatic builds
- **Vercel** (Frontend): Next.js optimized hosting with edge network
- **Render**: Alternative platform with managed PostgreSQL
- **Fly.io**: Container deployment via CLI

Quick deployment:

```bash
# Backend to Railway
cd backend
railway up

# Frontend to Vercel
cd frontend
vercel --prod
```

## Development

### CI/CD

GitHub Actions automatically runs on push to `main`:

- Backend: Rust build and tests with PostgreSQL/MongoDB services
- Frontend: Next.js build verification

### Code Quality

- **Rust**: Use `cargo fmt` and `cargo clippy` before committing
- **TypeScript**: ESLint and Prettier configured via Next.js

## Contributing

This is an academic project (Epitech Pre-MSc). Contributions are welcome for learning purposes.

## License

Educational project for Epitech Pre-MSc program.

## Acknowledgments

- [Axum](https://github.com/tokio-rs/axum) - Fast Rust web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [PostgreSQL](https://postgresql.org/) - Advanced relational database
- [MongoDB](https://mongodb.com/) - Document database for scalability


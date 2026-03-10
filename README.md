# Epitech - Pre Msc


## Introduction

Hello World is a full-stack real-time messaging application built with a Rust backend (Axum) and a Next.js frontend. It features server-based chat rooms, channels, member management, and JWT authentication.

The architecture uses PostgreSQL for relational data (users, servers, channels, memberships) and MongoDB for message storage, enabling horizontal scalability for high-volume messaging.

## Features

- User authentication with JWT tokens and bcrypt password hashing
- Server creation and management with role-based access control (Owner/Admin/Member)
- Text channels within servers with position ordering
- Real-time messaging with polling (WebSocket upgrade planned)
- User profiles with status indicators (Online/Offline/DND/Invisible)
- Public user lookup endpoint for member display

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend | Rust, Axum, Tokio, SQLx, MongoDB driver |
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
│   │   ├── handlers/            # HTTP request handlers
│   │   ├── models/              # Data structures and DTOs
│   │   ├── repositories/        # Database access layer
│   │   ├── services/            # Business logic
│   │   ├── routes/              # Route definitions
│   │   └── web/                 # Middleware (auth)
│   ├── migrations/
│   │   ├── init.sql             # PostgreSQL schema
│   │   └── mongodb_indexes.js   # MongoDB indexes
│   ├── Cargo.toml
│   └── Dockerfile
├── frontend/
│   ├── app/                     # Next.js App Router pages
│   │   ├── (auth)/              # Login/Register routes
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Main chat interface
│   ├── hooks/                   # Custom React hooks
│   ├── lib/                     # API clients and utilities
│   └── public/                  # Static assets
├── docs/                        # Documentation
├── docker-compose.yml           # Local development services
└── .github/workflows/ci.yml     # CI/CD pipeline
```

## Installation

### Prerequisites

- Docker and Docker Compose
- Rust 1.75+ (with cargo)
- Node.js 20+ (with npm)

### Database Setup

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
cargo run
```

The API will be available at `http://localhost:3001`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:3000`.

## Configuration

> **📖 For detailed setup instructions with NeonDB and MongoDB Atlas, see [docs/SETUP.md](./docs/SETUP.md)**

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://postgres:postgres@localhost:5433/helloworld` |
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `JWT_SECRET` | Secret key for JWT signing | `super_secret_jwt_key_change_in_production` |
| `PORT` | Server port | `3001` |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_URL` | Backend API URL | `http://localhost:3001` |

### Production Configuration

#### NeonDB (PostgreSQL)

1. Go to [Neon Console](https://console.neon.tech/)
2. Navigate to your project > **Connection Details**
3. Copy the connection string (with `?sslmode=require`)

```bash
DATABASE_URL=postgres://user:password@ep-xxx-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

#### MongoDB Atlas (Messages)

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Navigate to **Database** > **Connect** > **Drivers**
3. Copy the connection string

```bash
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Create new account |
| POST | `/auth/login` | Authenticate user |
| POST | `/auth/logout` | Logout (requires auth) |

### User

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me` | Get current user profile |
| PATCH | `/me` | Update current user profile |
| GET | `/users/{id}` | Get public user info |

### Servers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/servers` | List user's servers |
| POST | `/servers` | Create server |
| GET | `/servers/{id}` | Get server details |
| PUT | `/servers/{id}` | Update server |
| DELETE | `/servers/{id}` | Delete server (owner only) |
| POST | `/servers/{id}/join` | Join server |
| DELETE | `/servers/{id}/leave` | Leave server |
| GET | `/servers/{id}/members` | List server members |

### Channels

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/servers/{id}/channels` | List server channels |
| POST | `/servers/{id}/channels` | Create channel |
| GET | `/channels/{id}` | Get channel details |
| PUT | `/channels/{id}` | Update channel |
| DELETE | `/channels/{id}` | Delete channel |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/channels/{id}/messages` | List channel messages |
| POST | `/channels/{id}/messages` | Send message |
| PUT | `/messages/{id}` | Edit message |
| DELETE | `/messages/{id}` | Delete message |

## Database Schema

### PostgreSQL

```
users
├── id (UUID, PK)
├── email (VARCHAR, UNIQUE)
├── password_hash (VARCHAR)
├── username (VARCHAR)
├── avatar_url (VARCHAR, nullable)
├── status (ENUM: online/offline/dnd/invisible)
└── created_at (TIMESTAMPTZ)

servers
├── id (UUID, PK)
├── name (VARCHAR)
├── owner_id (UUID, FK → users)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)

server_members
├── server_id (UUID, PK, FK → servers)
├── user_id (UUID, PK, FK → users)
├── role (ENUM: owner/admin/member)
└── joined_at (TIMESTAMPTZ)

channels
├── id (UUID, PK)
├── server_id (UUID, FK → servers)
├── name (VARCHAR)
├── position (INT)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)
```

### MongoDB

```
channel_messages
├── _id (ObjectId)
├── message_id (UUID, unique index)
├── server_id (UUID, index)
├── channel_id (UUID, index)
├── author_id (UUID, index)
├── content (String)
├── created_at (DateTime, index)
├── edited_at (DateTime, nullable)
├── deleted_at (DateTime, nullable)
└── deleted_by (UUID, nullable)
```

## Deployment

The project includes configuration for multiple deployment platforms:

- **Render**: Web services with managed PostgreSQL
- **Fly.io**: Container deployment via CLI
- **Railway**: Docker-based deployment

See the deployment documentation in `docs/` for detailed instructions.

## Development

### Running Tests

```bash
# Backend tests
cd backend
cargo test

# Frontend build check
cd frontend
npm run build
```

### CI/CD

GitHub Actions automatically runs on push to `main`:

- Backend: Rust build and tests with PostgreSQL/MongoDB services
- Frontend: Node.js build verification

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Support

For questions, issues, or feature requests, please open an issue on the GitHub repository.

## Acknowledgments

Built with modern web technologies and best practices:
- [Axum](https://github.com/tokio-rs/axum) - Web framework for Rust
- [Next.js](https://nextjs.org/) - React framework for production
- [PostgreSQL](https://www.postgresql.org/) - Advanced open-source relational database
- [MongoDB](https://www.mongodb.com/) - Document database for scalable applications

#   T - D E V - 6 0 0 - P A R _ 2 7  
 
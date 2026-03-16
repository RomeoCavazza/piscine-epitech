# Documentation - Hello World RTC

Real-time instant messaging application (Discord-like).

---

## 📂 Documentation Structure

```text
docs/
├── README.md                    # This portal
├── specifications/              # Project specifications
│   ├── requirements.md          # Complete requirements
│   ├── grading-criteria.md      # Evaluation criteria
│   └── moscow.md                # MoSCoW prioritization
├── architecture/                # Technical architecture
│   ├── overview.md              # Global overview
│   ├── database.md              # Data model & logic
│   └── folder-structure.md      # Directory hierarchy
└── uml/                         # UML Diagrams
    ├── classes.puml             # Class diagram (Archival)
    ├── database-schema.puml     # DB schema (Archival)
    └── entities.md              # Entity descriptions
```

---

## 🛠️ Technical Stack

| Component           | Technology                                    |
| ------------------- | ---------------------------------------------- |
| **Frontend**        | Next.js 16 + React 19 + TypeScript             |
| **Backend**         | Rust + Axum + Tokio                            |
| **Databases**       | PostgreSQL (Relational) + MongoDB (Messages)   |
| **Real-time**       | WebSockets                                     |
| **Styling**         | Tailwind CSS 4                                 |

---

## 🚀 Key Features

- **Authentication**: JWT-based Signup/Login.
- **Servers**: Create and join via invitation codes.
- **Channels**: Textual channels per server.
- **Messages**: Real-time delivery via WebSocket.
- **Roles**: RBAC (Owner / Admin / Member).
- **Presence**: Online status and typing indicators.

---

## 🔗 Quick Links

- [**Technical Specification**](./specification.txt) — Consolidated logic & rules.
- [**Requirements**](./specifications/requirements.md) — Full product scope.
- [**Database Schema**](./architecture/database.md) — ERD and persistence logic.
- [**Code Metrics**](./cloc-report.md) — Repository statistics.

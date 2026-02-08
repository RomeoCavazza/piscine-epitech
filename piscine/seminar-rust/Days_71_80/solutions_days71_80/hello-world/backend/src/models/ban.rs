use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, FromRow)]
pub struct Ban {
    pub id: Uuid,
    pub server_id: Uuid,
    pub user_id: Uuid,
    pub banned_by: Uuid,
    pub reason: Option<String>,
    pub banned_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
    pub is_permanent: bool,
}

#[derive(Debug, Deserialize)]
pub struct CreateBanPayload {
    pub reason: Option<String>,
    pub expires_at: Option<DateTime<Utc>>,
    pub is_permanent: Option<bool>,
}

#[derive(Debug, Clone, Serialize, FromRow)]
pub struct BanWithUser {
    pub id: Uuid,
    pub server_id: Uuid,
    pub user_id: Uuid,
    pub username: String,
    pub banned_by: Uuid,
    pub banned_by_username: String,
    pub reason: Option<String>,
    pub banned_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
    pub is_permanent: bool,
}

impl Ban {
    /// Check if ban is currently active
    pub fn is_active(&self) -> bool {
        if self.is_permanent {
            return true;
        }
        
        if let Some(expires_at) = self.expires_at {
            Utc::now() < expires_at
        } else {
            true // No expiration = permanent
        }
    }
}

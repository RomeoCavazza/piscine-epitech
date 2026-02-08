use sqlx::PgPool;
use uuid::Uuid;

use crate::error::Result;
use crate::models::{Ban, BanWithUser};

#[derive(Clone)]
pub struct BanRepository {
    pool: PgPool,
}

impl BanRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    /// Create a new ban
    pub async fn create(
        &self,
        server_id: Uuid,
        user_id: Uuid,
        banned_by: Uuid,
        reason: Option<String>,
        expires_at: Option<chrono::DateTime<chrono::Utc>>,
        is_permanent: bool,
    ) -> Result<Ban> {
        let ban = sqlx::query_as::<_, Ban>(
            r#"
            INSERT INTO bans (server_id, user_id, banned_by, reason, expires_at, is_permanent)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (server_id, user_id) 
            DO UPDATE SET 
                banned_by = EXCLUDED.banned_by,
                reason = EXCLUDED.reason,
                expires_at = EXCLUDED.expires_at,
                is_permanent = EXCLUDED.is_permanent,
                banned_at = NOW()
            RETURNING *
            "#,
        )
        .bind(server_id)
        .bind(user_id)
        .bind(banned_by)
        .bind(reason)
        .bind(expires_at)
        .bind(is_permanent)
        .fetch_one(&self.pool)
        .await?;

        Ok(ban)
    }

    /// Find ban by server and user
    pub async fn find_by_server_and_user(
        &self,
        server_id: Uuid,
        user_id: Uuid,
    ) -> Result<Option<Ban>> {
        let ban = sqlx::query_as::<_, Ban>(
            r#"
            SELECT * FROM bans
            WHERE server_id = $1 AND user_id = $2
            "#,
        )
        .bind(server_id)
        .bind(user_id)
        .fetch_optional(&self.pool)
        .await?;

        Ok(ban)
    }

    /// List all bans for a server with user info
    pub async fn list_by_server(&self, server_id: Uuid) -> Result<Vec<BanWithUser>> {
        let bans = sqlx::query_as::<_, BanWithUser>(
            r#"
            SELECT 
                b.id,
                b.server_id,
                b.user_id,
                u.username,
                b.banned_by,
                ub.username as banned_by_username,
                b.reason,
                b.banned_at,
                b.expires_at,
                b.is_permanent
            FROM bans b
            JOIN users u ON b.user_id = u.id
            JOIN users ub ON b.banned_by = ub.id
            WHERE b.server_id = $1
            ORDER BY b.banned_at DESC
            "#,
        )
        .bind(server_id)
        .fetch_all(&self.pool)
        .await?;

        Ok(bans)
    }

    /// Remove ban (unban)
    pub async fn delete(
        &self,
        server_id: Uuid,
        user_id: Uuid,
    ) -> Result<bool> {
        let result = sqlx::query(
            r#"
            DELETE FROM bans
            WHERE server_id = $1 AND user_id = $2
            "#,
        )
        .bind(server_id)
        .bind(user_id)
        .execute(&self.pool)
        .await?;

        Ok(result.rows_affected() > 0)
    }

    /// Clean up expired bans (should be called periodically)
    pub async fn cleanup_expired(&self) -> Result<u64> {
        let result = sqlx::query(
            r#"
            DELETE FROM bans
            WHERE is_permanent = FALSE 
            AND expires_at IS NOT NULL 
            AND expires_at < NOW()
            "#,
        )
        .execute(&self.pool)
        .await?;

        Ok(result.rows_affected())
    }
}

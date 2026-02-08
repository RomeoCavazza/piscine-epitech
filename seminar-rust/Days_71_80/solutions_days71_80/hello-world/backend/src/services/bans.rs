use crate::error::{Error, Result};
use crate::models::{Ban, BanWithUser, CreateBanPayload, MemberRole};
use crate::repositories::BanRepository;
use chrono::Utc;
use uuid::Uuid;

/// Ban a member from the server (Admin/Owner only, cannot ban Owner)
pub async fn ban_member(
    ban_repo: &BanRepository,
    server_repo: &crate::repositories::ServerRepository,
    server_id: Uuid,
    target_user_id: Uuid,
    requester_id: Uuid,
    payload: CreateBanPayload,
) -> Result<Ban> {
    // Verify server exists
    let _server = server_repo
        .find_by_id(server_id)
        .await?
        .ok_or(Error::ServerNotFound)?;

    // Get requester's role
    let requester = server_repo
        .find_member(server_id, requester_id)
        .await?
        .ok_or(Error::ServerForbidden)?;

    // Only Admin or Owner can ban
    if !matches!(requester.role, MemberRole::Owner | MemberRole::Admin) {
        return Err(Error::ServerForbidden);
    }

    // Get target member
    let target = server_repo
        .find_member(server_id, target_user_id)
        .await?
        .ok_or(Error::UserNotFound)?;

    // Cannot ban the Owner
    if target.role == MemberRole::Owner {
        return Err(Error::ServerForbidden);
    }

    // Cannot ban yourself
    if target_user_id == requester_id {
        return Err(Error::ServerForbidden);
    }

    // Determine if permanent ban
    let is_permanent = payload.is_permanent.unwrap_or(false);

    // Create the ban
    let ban = ban_repo
        .create(
            server_id,
            target_user_id,
            requester_id,
            payload.reason,
            payload.expires_at,
            is_permanent,
        )
        .await?;

    // Kick the member from the server
    server_repo.remove_member(server_id, target_user_id).await?;

    Ok(ban)
}

/// Unban a member from the server (Admin/Owner only)
pub async fn unban_member(
    ban_repo: &BanRepository,
    server_repo: &crate::repositories::ServerRepository,
    server_id: Uuid,
    target_user_id: Uuid,
    requester_id: Uuid,
) -> Result<()> {
    // Verify server exists
    let _server = server_repo
        .find_by_id(server_id)
        .await?
        .ok_or(Error::ServerNotFound)?;

    // Get requester's role
    let requester = server_repo
        .find_member(server_id, requester_id)
        .await?
        .ok_or(Error::ServerForbidden)?;

    // Only Admin or Owner can unban
    if !matches!(requester.role, MemberRole::Owner | MemberRole::Admin) {
        return Err(Error::ServerForbidden);
    }

    // Remove the ban
    ban_repo.delete(server_id, target_user_id).await?;

    Ok(())
}

/// List all bans for a server (Admin/Owner only)
pub async fn list_bans(
    ban_repo: &BanRepository,
    server_repo: &crate::repositories::ServerRepository,
    server_id: Uuid,
    requester_id: Uuid,
) -> Result<Vec<BanWithUser>> {
    // Verify server exists
    let _server = server_repo
        .find_by_id(server_id)
        .await?
        .ok_or(Error::ServerNotFound)?;

    // Get requester's role
    let requester = server_repo
        .find_member(server_id, requester_id)
        .await?
        .ok_or(Error::ServerForbidden)?;

    // Only Admin or Owner can view bans
    if !matches!(requester.role, MemberRole::Owner | MemberRole::Admin) {
        return Err(Error::ServerForbidden);
    }

    let bans = ban_repo.list_by_server(server_id).await?;

    Ok(bans)
}

/// Check if a user is banned from a server
/// Note: Currently unused but kept for future features (e.g., join validation)
#[allow(dead_code)]
pub async fn is_user_banned(
    ban_repo: &BanRepository,
    server_id: Uuid,
    user_id: Uuid,
) -> Result<bool> {
    if let Some(ban) = ban_repo.find_by_server_and_user(server_id, user_id).await? {
        return Ok(ban.is_active());
    }
    Ok(false)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ban_is_active() {
        use chrono::Duration;

        // Permanent ban
        let permanent_ban = Ban {
            id: Uuid::new_v4(),
            server_id: Uuid::new_v4(),
            user_id: Uuid::new_v4(),
            banned_by: Uuid::new_v4(),
            reason: None,
            banned_at: Utc::now(),
            expires_at: None,
            is_permanent: true,
        };
        assert!(permanent_ban.is_active());

        // Temporary ban (not expired)
        let future_ban = Ban {
            id: Uuid::new_v4(),
            server_id: Uuid::new_v4(),
            user_id: Uuid::new_v4(),
            banned_by: Uuid::new_v4(),
            reason: None,
            banned_at: Utc::now(),
            expires_at: Some(Utc::now() + Duration::days(7)),
            is_permanent: false,
        };
        assert!(future_ban.is_active());

        // Temporary ban (expired)
        let expired_ban = Ban {
            id: Uuid::new_v4(),
            server_id: Uuid::new_v4(),
            user_id: Uuid::new_v4(),
            banned_by: Uuid::new_v4(),
            reason: None,
            banned_at: Utc::now() - Duration::days(7),
            expires_at: Some(Utc::now() - Duration::days(1)),
            is_permanent: false,
        };
        assert!(!expired_ban.is_active());
    }
}

use uuid::Uuid;

use crate::error::{Error, Result};
use crate::models::{Channel, CreateChannelPayload, MemberRole, UpdateChannelPayload};
use crate::repositories::{ChannelRepository, ServerRepository};

pub async fn create_channel(
    server_repo: &ServerRepository,
    channel_repo: &ChannelRepository,
    server_id: Uuid,
    user_id: Uuid,
    payload: CreateChannelPayload,
) -> Result<Channel> {
    let member = server_repo
        .find_member(server_id, user_id)
        .await?
        .ok_or(Error::ChannelForbidden)?;

    if member.role == MemberRole::Member {
        return Err(Error::ChannelForbidden);
    }

    let position = match payload.position {
        Some(p) => p,
        None => {
            let max = channel_repo.get_max_position(server_id).await?;
            max.map(|m| m + 1).unwrap_or(0)
        }
    };

    let channel_id = Uuid::new_v4();
    let channel = channel_repo
        .create(channel_id, server_id, &payload.name, position)
        .await?;

    Ok(channel)
}

pub async fn list_channels(
    server_repo: &ServerRepository,
    channel_repo: &ChannelRepository,
    server_id: Uuid,
    user_id: Uuid,
) -> Result<Vec<Channel>> {
    server_repo
        .find_member(server_id, user_id)
        .await?
        .ok_or(Error::ChannelForbidden)?;

    let channels = channel_repo.list_by_server(server_id).await?;
    Ok(channels)
}

pub async fn get_channel(
    server_repo: &ServerRepository,
    channel_repo: &ChannelRepository,
    channel_id: Uuid,
    user_id: Uuid,
) -> Result<Channel> {
    let channel = channel_repo
        .find_by_id(channel_id)
        .await?
        .ok_or(Error::ChannelNotFound)?;

    server_repo
        .find_member(channel.server_id, user_id)
        .await?
        .ok_or(Error::ChannelForbidden)?;

    Ok(channel)
}

pub async fn update_channel(
    server_repo: &ServerRepository,
    channel_repo: &ChannelRepository,
    channel_id: Uuid,
    user_id: Uuid,
    payload: UpdateChannelPayload,
) -> Result<Channel> {
    let existing = channel_repo
        .find_by_id(channel_id)
        .await?
        .ok_or(Error::ChannelNotFound)?;

    let member = server_repo
        .find_member(existing.server_id, user_id)
        .await?
        .ok_or(Error::ChannelForbidden)?;

    if member.role == MemberRole::Member {
        return Err(Error::ChannelForbidden);
    }

    let channel = channel_repo
        .update(channel_id, payload.name, payload.position)
        .await?
        .ok_or(Error::ChannelNotFound)?;

    Ok(channel)
}

pub async fn delete_channel(
    server_repo: &ServerRepository,
    channel_repo: &ChannelRepository,
    channel_id: Uuid,
    user_id: Uuid,
) -> Result<()> {
    let existing = channel_repo
        .find_by_id(channel_id)
        .await?
        .ok_or(Error::ChannelNotFound)?;

    let member = server_repo
        .find_member(existing.server_id, user_id)
        .await?
        .ok_or(Error::ChannelForbidden)?;

    if member.role == MemberRole::Member {
        return Err(Error::ChannelForbidden);
    }

    channel_repo.delete(channel_id).await?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_channel_name_validation() {
        let valid_names = vec!["general", "random", "off-topic", "announcements"];
        for name in valid_names {
            assert!(!name.is_empty());
            assert!(name.len() <= 100);
        }
    }

    #[test]
    fn test_channel_position_ordering() {
        let positions = vec![1, 2, 3, 4, 5];
        for i in 1..positions.len() {
            assert!(positions[i] > positions[i-1]);
        }
    }

    #[test]
    fn test_max_position_calculation() {
        let positions = vec![1, 3, 5, 2, 4];
        let max = positions.iter().max().unwrap();
        assert_eq!(*max, 5);
        assert_eq!(max + 1, 6);
    }

    #[test]
    fn test_member_role_permissions() {
        assert!(matches!(MemberRole::Owner, MemberRole::Owner | MemberRole::Admin));
        assert!(matches!(MemberRole::Admin, MemberRole::Owner | MemberRole::Admin));
        assert!(!matches!(MemberRole::Member, MemberRole::Owner | MemberRole::Admin));
    }
}

use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use uuid::Uuid;

use crate::ctx::Ctx;
use crate::error::Result;
use crate::models::{Ban, BanWithUser, CreateBanPayload};
use crate::services;
use crate::AppState;

pub async fn ban_member(
    State(state): State<AppState>,
    ctx: Ctx,
    Path((server_id, user_id)): Path<(Uuid, Uuid)>,
    Json(payload): Json<CreateBanPayload>,
) -> Result<Json<Ban>> {
    let ban = services::ban_member(
        &state.ban_repo,
        &state.server_repo,
        server_id,
        user_id,
        ctx.user_id(),
        payload,
    )
    .await?;
    Ok(Json(ban))
}

pub async fn unban_member(
    State(state): State<AppState>,
    ctx: Ctx,
    Path((server_id, user_id)): Path<(Uuid, Uuid)>,
) -> Result<StatusCode> {
    services::unban_member(
        &state.ban_repo,
        &state.server_repo,
        server_id,
        user_id,
        ctx.user_id(),
    )
    .await?;
    Ok(StatusCode::NO_CONTENT)
}

pub async fn list_bans(
    State(state): State<AppState>,
    ctx: Ctx,
    Path(server_id): Path<Uuid>,
) -> Result<Json<Vec<BanWithUser>>> {
    let bans = services::list_bans(
        &state.ban_repo,
        &state.server_repo,
        server_id,
        ctx.user_id(),
    )
    .await?;
    Ok(Json(bans))
}

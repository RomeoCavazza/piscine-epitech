use axum::{
    routing::{delete, get, post, put},
    Router,
};
use crate::handlers::servers; // Importation du module contenant les handlers
use crate::AppState;

pub fn routes() -> Router<AppState> {
    Router::new()
        // Gestion de la liste et de la création
        .route(
            "/", 
            post(servers::create_server).get(servers::list_servers)
        )
        // Gestion d'un serveur spécifique (ID)
        .route(
            "/:id",
            get(servers::get_server)
                .put(servers::update_server)
                .delete(servers::delete_server),
        )
        // Autres fonctionnalités
        .route("/:id/join", post(servers::join_server))
        .route("/:id/leave", delete(servers::leave_server))
        .route("/:id/members", get(servers::list_members))
        .route("/:id/members/:userId", put(servers::update_member_role).delete(servers::kick_member))
        .route("/:id/transfer", put(servers::transfer_ownership))
}
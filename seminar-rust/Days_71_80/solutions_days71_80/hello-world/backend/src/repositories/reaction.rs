use crate::error::{Error, Result};
use crate::models::{AddReactionPayload, MessageReaction, ReactionSummary};
use mongodb::bson::doc;
use mongodb::{Collection, Database};
use uuid::Uuid;

pub struct ReactionRepository {
    collection: Collection<MessageReaction>,
}

impl ReactionRepository {
    pub fn new(db: &Database) -> Self {
        Self {
            collection: db.collection("message_reactions"),
        }
    }

    pub async fn add_reaction(
        &self,
        message_id: &str,
        user_id: Uuid,
        payload: AddReactionPayload,
    ) -> Result<MessageReaction> {
        let reaction = MessageReaction {
            message_id: message_id.to_string(),
            user_id,
            emoji: payload.emoji,
            created_at: chrono::Utc::now(),
        };

        // Supprimer réaction existante du même user/emoji/message
        self.collection
            .delete_many(doc! {
                "message_id": message_id,
                "user_id": reaction.user_id.to_string(),
                "emoji": &reaction.emoji
            })
            .await
            .map_err(|e| Error::InternalError {
                message: e.to_string(),
            })?;

        // Ajouter nouvelle réaction
        self.collection
            .insert_one(&reaction)
            .await
            .map_err(|e| Error::InternalError {
                message: e.to_string(),
            })?;

        Ok(reaction)
    }

    pub async fn remove_reaction(
        &self,
        message_id: &str,
        user_id: Uuid,
        emoji: &str,
    ) -> Result<()> {
        self.collection
            .delete_one(doc! {
                "message_id": message_id,
                "user_id": user_id.to_string(),
                "emoji": emoji
            })
            .await
            .map_err(|e| Error::InternalError {
                message: e.to_string(),
            })?;

        Ok(())
    }

    pub async fn get_reactions(&self, message_id: &str) -> Result<Vec<ReactionSummary>> {
        let cursor = self
            .collection
            .find(doc! { "message_id": message_id })
            .await
            .map_err(|e| Error::InternalError {
                message: e.to_string(),
            })?;

        use futures::stream::TryStreamExt;
        let reactions: Vec<MessageReaction> = cursor
            .try_collect()
            .await
            .map_err(|e| Error::InternalError {
                message: e.to_string(),
            })?;

        // Grouper par emoji
        let mut summaries: std::collections::HashMap<String, Vec<Uuid>> =
            std::collections::HashMap::new();

        for reaction in reactions {
            summaries
                .entry(reaction.emoji)
                .or_default()
                .push(reaction.user_id);
        }

        let result = summaries
            .into_iter()
            .map(|(emoji, users)| ReactionSummary {
                emoji,
                count: users.len() as i64,
                users,
            })
            .collect();

        Ok(result)
    }
}

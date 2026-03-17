use bson::doc;
use chrono::Utc;
use futures::TryStreamExt;
use mongodb::Database;
use uuid::Uuid;

use crate::models::ChannelMessage;

const COLLECTION_NAME: &str = "channel_messages";

#[derive(Clone)]
pub struct MessageRepository {
    db: Database,
}

impl MessageRepository {
    pub fn new(db: Database) -> Self {
        Self { db }
    }

    fn collection(&self) -> mongodb::Collection<ChannelMessage> {
        self.db.collection(COLLECTION_NAME)
    }

    pub async fn create(&self, message: &ChannelMessage) -> mongodb::error::Result<()> {
        self.collection().insert_one(message).await?;
        Ok(())
    }

    pub async fn find_by_id(
        &self,
        message_id: Uuid,
    ) -> mongodb::error::Result<Option<ChannelMessage>> {
        self.collection()
            .find_one(doc! { "message_id": message_id.to_string() })
            .await
    }

    pub async fn list_by_channel(
        &self,
        channel_id: Uuid,
        limit: i64,
        before: Option<Uuid>,
    ) -> mongodb::error::Result<Vec<ChannelMessage>> {
        let collection = self.collection();

        let mut filter = doc! {
            "channel_id": channel_id.to_string(),
            "deleted_at": null,
        };

        if let Some(before_id) = before {
            if let Some(before_msg) = collection
                .find_one(doc! { "message_id": before_id.to_string() })
                .await?
            {
                filter.insert("created_at", doc! { "$lt": before_msg.created_at });
            }
        }

        let options = mongodb::options::FindOptions::builder()
            .sort(doc! { "created_at": -1 })
            .limit(limit)
            .build();

        let cursor = collection.find(filter).with_options(options).await?;
        cursor.try_collect().await
    }

    pub async fn update_content(
        &self,
        message_id: Uuid,
        content: &str,
    ) -> mongodb::error::Result<()> {
        self.collection()
            .update_one(
                doc! { "message_id": message_id.to_string() },
                doc! {
                    "$set": {
                        "content": content,
                        "edited_at": Utc::now(),
                    }
                },
            )
            .await?;
        Ok(())
    }

    pub async fn soft_delete(
        &self,
        message_id: Uuid,
        deleted_by: Uuid,
    ) -> mongodb::error::Result<()> {
        self.collection()
            .update_one(
                doc! { "message_id": message_id.to_string() },
                doc! {
                    "$set": {
                        "deleted_at": Utc::now(),
                        "deleted_by": deleted_by.to_string(),
                    }
                },
            )
            .await?;
        Ok(())
    }
}

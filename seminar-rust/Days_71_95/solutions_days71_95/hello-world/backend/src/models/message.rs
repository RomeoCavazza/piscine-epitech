use bson::oid::ObjectId;
use chrono::{DateTime, Utc};
use serde::de::Error as _;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

mod uuid_compat_string {
    use super::*;
    use bson::Binary;
    use serde::{Deserializer, Serializer};

    #[derive(Deserialize)]
    #[serde(untagged)]
    enum UuidCompat {
        Str(String),
        BsonUuid(bson::Uuid),
        Binary(Binary),
    }

    pub fn serialize<S>(value: &Uuid, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(&value.to_string())
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<Uuid, D::Error>
    where
        D: Deserializer<'de>,
    {
        let v = UuidCompat::deserialize(deserializer)?;
        match v {
            UuidCompat::Str(s) => Uuid::parse_str(&s).map_err(D::Error::custom),
            UuidCompat::BsonUuid(u) => Ok(u.into()),
            UuidCompat::Binary(b) => Uuid::from_slice(&b.bytes).map_err(D::Error::custom),
        }
    }

    pub mod option {
        use super::*;

        pub fn serialize<S>(value: &Option<Uuid>, serializer: S) -> Result<S::Ok, S::Error>
        where
            S: Serializer,
        {
            match value {
                Some(v) => serializer.serialize_some(&v.to_string()),
                None => serializer.serialize_none(),
            }
        }

        pub fn deserialize<'de, D>(deserializer: D) -> Result<Option<Uuid>, D::Error>
        where
            D: Deserializer<'de>,
        {
            Option::<Uuid>::deserialize(deserializer)
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelMessage {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    #[serde(with = "uuid_compat_string")]
    pub message_id: Uuid,
    #[serde(with = "uuid_compat_string")]
    pub server_id: Uuid,
    #[serde(with = "uuid_compat_string")]
    pub channel_id: Uuid,
    #[serde(with = "uuid_compat_string")]
    pub author_id: Uuid,
    pub content: String,
    pub created_at: DateTime<Utc>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub edited_at: Option<DateTime<Utc>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub deleted_at: Option<DateTime<Utc>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[serde(with = "uuid_compat_string::option")]
    pub deleted_by: Option<Uuid>,
}

#[derive(Debug, Clone, Serialize)]
pub struct MessageWithUser {
    pub id: Uuid,
    pub server_id: Uuid,
    pub channel_id: Uuid,
    pub author_id: Uuid,
    pub username: String,
    pub content: String,
    pub created_at: DateTime<Utc>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub edited_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Deserialize)]
pub struct CreateMessagePayload {
    pub content: String,
}

#[derive(Debug, Deserialize)]
pub struct UpdateMessagePayload {
    pub content: String,
}

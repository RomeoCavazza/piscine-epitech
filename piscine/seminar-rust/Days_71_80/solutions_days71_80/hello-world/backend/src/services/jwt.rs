use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use uuid::Uuid;

use crate::models::Claims;

/// Durée de validité du token (24 heures)
const TOKEN_EXPIRATION_HOURS: i64 = 24;

/// Génère un JWT pour un utilisateur
pub fn create_token(
    user_id: Uuid,
    email: &str,
    secret: &str,
) -> Result<String, jsonwebtoken::errors::Error> {
    let now = chrono::Utc::now();
    let exp = now + chrono::Duration::hours(TOKEN_EXPIRATION_HOURS);

    let claims = Claims {
        sub: user_id,
        email: email.to_string(),
        exp: exp.timestamp() as usize,
        iat: now.timestamp() as usize,
    };

    encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(secret.as_bytes()),
    )
}

/// Vérifie et décode un JWT
pub fn verify_token(token: &str, secret: &str) -> Result<Claims, jsonwebtoken::errors::Error> {
    let token_data = decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret.as_bytes()),
        &Validation::default(),
    )?;

    Ok(token_data.claims)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_and_verify_token() {
        let user_id = Uuid::new_v4();
        let email = "test@example.com";
        let secret = "test_secret_key";

        let token = create_token(user_id, email, secret).unwrap();
        let claims = verify_token(&token, secret).unwrap();

        assert_eq!(claims.sub, user_id);
        assert_eq!(claims.email, email);
    }

    #[test]
    fn test_verify_invalid_token() {
        let secret = "test_secret";
        let result = verify_token("invalid.token.here", secret);
        assert!(result.is_err());
    }

    #[test]
    fn test_verify_with_wrong_secret() {
        let user_id = Uuid::new_v4();
        let email = "test@example.com";
        let secret1 = "secret1";
        let secret2 = "secret2";

        let token = create_token(user_id, email, secret1).unwrap();
        let result = verify_token(&token, secret2);
        assert!(result.is_err());
    }

    #[test]
    fn test_token_contains_user_id() {
        let user_id = Uuid::new_v4();
        let email = "user@example.com";
        let secret = "secret";

        let token = create_token(user_id, email, secret).unwrap();
        let claims = verify_token(&token, secret).unwrap();

        assert_eq!(claims.sub, user_id);
        assert!(claims.exp > claims.iat);
    }
}

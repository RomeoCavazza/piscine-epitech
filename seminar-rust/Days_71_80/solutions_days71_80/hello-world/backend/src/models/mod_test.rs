use uuid::Uuid;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_uuid_generation() {
        let id1 = Uuid::new_v4();
        let id2 = Uuid::new_v4();
        assert_ne!(id1, id2);
    }

    #[test]
    fn test_uuid_parsing() {
        let id_str = "550e8400-e29b-41d4-a716-446655440000";
        let result = Uuid::parse_str(id_str);
        assert!(result.is_ok());
        assert_eq!(result.unwrap().to_string(), id_str);
    }

    #[test]
    fn test_uuid_invalid() {
        let result = Uuid::parse_str("invalid-uuid");
        assert!(result.is_err());
    }
}

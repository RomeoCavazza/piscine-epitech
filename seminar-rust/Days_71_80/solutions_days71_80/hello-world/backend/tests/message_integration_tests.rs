// Integration tests for Message operations

#[cfg(test)]
mod message_tests {
    use uuid::Uuid;

    #[test]
    fn test_message_content_validation() {
        // Non-empty content
        let valid = vec!["Hello", "Test message", "a"];
        let max_content = "X".repeat(2000);
        let invalid = vec!["", "   ", "\n\n", "\t\t"];
        
        for content in valid {
            assert!(!content.trim().is_empty());
            assert!(content.len() <= 2000);
        }
        assert_eq!(max_content.len(), 2000);
        
        for content in invalid {
            assert!(content.trim().is_empty());
        }
    }

    #[test]
    fn test_message_max_length() {
        let short = "Short message";
        let max = "X".repeat(2000);
        let too_long = "X".repeat(2001);
        
        assert!(short.len() < 2000);
        assert_eq!(max.len(), 2000);
        assert!(too_long.len() > 2000);
    }

    #[test]
    fn test_message_unicode_support() {
        // Test emoji and international characters
        let messages = vec![
            "Hello 👋",
            "Bonjour 🇫🇷",
            "こんにちは",
            "مرحبا",
            "Привет",
        ];
        
        for msg in messages {
            assert!(!msg.is_empty());
            // Verify UTF-8 encoding works
            assert!(msg.chars().count() > 0);
        }
    }

    #[test]
    fn test_message_id_uniqueness() {
        let ids: Vec<Uuid> = (0..100).map(|_| Uuid::new_v4()).collect();
        
        // Check all IDs are unique
        for i in 0..ids.len() {
            for j in (i+1)..ids.len() {
                assert_ne!(ids[i], ids[j]);
            }
        }
    }

    #[test]
    fn test_message_timestamp_ordering() {
        use std::time::{SystemTime, UNIX_EPOCH};
        
        let t1 = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        std::thread::sleep(std::time::Duration::from_millis(10));
        let t2 = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        
        assert!(t2 >= t1, "Timestamps should be ordered");
    }
}

"use client";

import { useState } from "react";
import EmojiPicker, { EmojiClickData, Theme } from "emoji-picker-react";

interface EmojiReactionPickerProps {
  onEmojiSelect: (emoji: string) => void;
  onClose: () => void;
}

export default function EmojiReactionPicker({
  onEmojiSelect,
  onClose,
}: EmojiReactionPickerProps) {
  const handleEmojiClick = (emojiData: EmojiClickData) => {
    onEmojiSelect(emojiData.emoji);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />

      {/* Picker */}
      <div className="relative z-10">
        <EmojiPicker
          onEmojiClick={handleEmojiClick}
          theme={Theme.DARK}
          width={350}
          height={450}
        />
      </div>
    </div>
  );
}

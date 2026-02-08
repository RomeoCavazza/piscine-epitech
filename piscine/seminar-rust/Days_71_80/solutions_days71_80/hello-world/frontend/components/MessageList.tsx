import { Message, User } from "@/lib/api-server";
import { ServerMember } from "@/lib/api-server";

interface MessageListProps {
  messages: Message[];
  currentUser: User | null;
  members: ServerMember[];
  editingMessageId: string | null;
  editingContent: string;
  onEditMessage: (messageId: string, content: string) => void;
  onEditChange: (content: string) => void;
  onEditSave: () => void;
  onEditCancel: () => void;
  onMemberClick: (member: ServerMember) => void;
  onProfileClick: () => void;
}

export default function MessageList({
  messages,
  currentUser,
  members,
  editingMessageId,
  editingContent,
  onEditMessage,
  onEditChange,
  onEditSave,
  onEditCancel,
  onMemberClick,
  onProfileClick
}: MessageListProps) {
  const getAvatar = (authorId: string) => {
    const member = members.find(m => m.user_id === authorId);
    if (member?.avatar_url) {
      const url = member.avatar_url.startsWith('/') 
        ? `http://localhost:3001${member.avatar_url}` 
        : member.avatar_url;
      return url;
    }
    const hex = authorId.replace(/-/g, '').slice(0, 2);
    const num = parseInt(hex, 16);
    const avatarNum = (num % 100) + 1;
    return `/avatars/avatar${avatarNum}.png`;
  };

  return (
    <div className="space-y-4">
      {messages.map((msg) => {
        const messageMember = members.find(m => m.user_id === msg.author_id);
        const isOwn = msg.author_id === currentUser?.id;
        const isEditing = editingMessageId === msg.id;

        return (
          <div key={msg.id} className="flex items-start gap-3 px-4 py-2 rounded hover:bg-white/5 transition-colors group">
            <img 
              src={getAvatar(msg.author_id)} 
              alt={msg.username}
              onClick={() => {
                if (isOwn) {
                  onProfileClick();
                } else if (messageMember) {
                  onMemberClick(messageMember);
                }
              }}
              className="w-10 h-10 rounded-full object-cover border border-[#4fdfff]/30 flex-shrink-0 group-hover:border-[#4fdfff]/50 transition-colors cursor-pointer"
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-baseline gap-2 mb-1">
                <span 
                  onClick={() => {
                    if (isOwn) {
                      onProfileClick();
                    } else if (messageMember) {
                      onMemberClick(messageMember);
                    }
                  }}
                  className="font-semibold text-white hover:text-[#4fdfff] transition-colors cursor-pointer"
                >
                  {msg.username}
                </span>
                <span className="text-xs text-white/40">
                  {new Date(msg.created_at).toLocaleTimeString("fr-FR", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
                {msg.edited_at && <span className="text-xs text-white/40">(modifié)</span>}
              </div>
              
              {isEditing ? (
                <input
                  type="text"
                  value={editingContent}
                  onChange={(e) => onEditChange(e.target.value)}
                  onBlur={onEditSave}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') onEditSave();
                    else if (e.key === 'Escape') onEditCancel();
                  }}
                  autoFocus
                  className="w-full px-2 py-1 bg-black/50 border border-cyan-500 rounded text-white outline-none"
                />
              ) : (
                <p 
                  onDoubleClick={() => isOwn && onEditMessage(msg.id, msg.content)}
                  className="text-white/90 leading-relaxed break-words"
                >
                  {msg.content}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

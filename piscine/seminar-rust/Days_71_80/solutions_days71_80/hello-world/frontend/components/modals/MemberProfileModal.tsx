"use client";

import { ServerMember, User } from "@/lib/api-server";
import { getAvatar } from "@/lib/avatar";

interface MemberProfileModalProps {
  member: ServerMember;
  currentUser: User | null;
  onClose: () => void;
  onChangeRole?: (role: "Admin" | "Member") => void;
  onKick?: () => void;
  onBan?: () => void;
  canManage: boolean;
}

export default function MemberProfileModal({
  member,
  currentUser,
  onClose,
  onChangeRole,
  onKick,
  onBan,
  canManage,
}: MemberProfileModalProps) {
  const isOwner = member.role === "Owner";
  const isSelf = member.user_id === currentUser?.id;
  const canModify = canManage && !isOwner && !isSelf;

  // Format join date
  const joinDate = new Date(member.joined_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-[rgba(20,20,20,0.98)] border-2 border-[#4fdfff] rounded-xl w-full max-w-md overflow-hidden shadow-[0_0_40px_rgba(79,223,255,0.3)] animate-fade-in">
        {/* Header with background gradient */}
        <div className="relative h-24 bg-gradient-to-br from-[#4fdfff]/20 via-[#4fdfff]/10 to-transparent">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-3 right-3 w-8 h-8 flex items-center justify-center rounded-lg bg-black/50 hover:bg-black/70 text-white/60 hover:text-white transition-all"
          >
            ✕
          </button>
        </div>

        {/* Avatar - positioned to overlap header */}
        <div className="relative px-6 -mt-12 mb-4">
          <div className="relative inline-block">
            <img
              src={getAvatar(member.user_id, currentUser)}
              alt={member.username}
              className="w-24 h-24 rounded-full border-4 border-[rgba(20,20,20,0.98)] object-cover shadow-lg"
            />
            {/* Status indicator */}
            <span className="absolute bottom-1 right-1 w-6 h-6 bg-green-500 border-4 border-[rgba(20,20,20,0.98)] rounded-full" />
          </div>
        </div>

        {/* Content */}
        <div className="px-6 pb-6">
          {/* Username */}
          <h2 className="text-2xl font-bold text-white mb-1">
            {member.username}
          </h2>

          {/* Role Badge */}
          <div className="mb-4">
            {member.role === "Owner" && (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-[#ff3333]/20 text-[#ff3333] text-xs font-bold border border-[#ff3333]/50">
                OWNER
              </span>
            )}
            {member.role === "Admin" && (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-[#4fdfff]/20 text-[#4fdfff] text-xs font-bold border border-[#4fdfff]/50">
                ADMIN
              </span>
            )}
            {member.role === "Member" && (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-white/10 text-white/70 text-xs font-bold border border-white/20">
                MEMBER
              </span>
            )}
          </div>

          {/* Info Section */}
          <div className="space-y-3 mb-6">
            <div className="bg-black/30 rounded-lg p-3 border border-[#4fdfff]/20">
              <p className="text-[10px] text-white/50 uppercase tracking-wider font-bold mb-1">
                Member Since
              </p>
              <p className="text-sm text-white/80">{joinDate}</p>
            </div>

            <div className="bg-black/30 rounded-lg p-3 border border-[#4fdfff]/20">
              <p className="text-[10px] text-white/50 uppercase tracking-wider font-bold mb-1">
                User ID
              </p>
              <p className="text-xs text-white/60 font-mono break-all">
                {member.user_id}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          {canModify && (
            <div className="space-y-2 pt-4 border-t border-[#4fdfff]/20">
              <p className="text-[10px] text-white/50 uppercase tracking-wider font-bold mb-2">
                Admin Actions
              </p>

              {/* Role Management */}
              {member.role === "Member" && onChangeRole && (
                <button
                  onClick={() => {
                    onChangeRole("Admin");
                    onClose();
                  }}
                  className="w-full px-4 py-2.5 bg-[#4fdfff]/10 hover:bg-[#4fdfff]/20 text-[#4fdfff] rounded-lg transition-all border border-[#4fdfff]/30 hover:border-[#4fdfff]/50 font-medium text-sm"
                >
                  Make Admin
                </button>
              )}

              {member.role === "Admin" && onChangeRole && (
                <button
                  onClick={() => {
                    onChangeRole("Member");
                    onClose();
                  }}
                  className="w-full px-4 py-2.5 bg-white/5 hover:bg-white/10 text-white/80 rounded-lg transition-all border border-white/20 hover:border-white/30 font-medium text-sm"
                >
                  Remove Admin
                </button>
              )}

              {/* Kick Button */}
              {onKick && (
                <button
                  onClick={() => {
                    if (confirm(`Kick ${member.username} from the server?`)) {
                      onKick();
                      onClose();
                    }
                  }}
                  className="w-full px-4 py-2.5 bg-yellow-500/10 hover:bg-yellow-500/20 text-yellow-400 rounded-lg transition-all border border-yellow-500/30 hover:border-yellow-500/50 font-medium text-sm"
                >
                  Kick Member
                </button>
              )}

              {/* Ban Button */}
              {onBan && (
                <button
                  onClick={() => {
                    onBan();
                    onClose();
                  }}
                  className="w-full px-4 py-2.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-all border border-red-500/30 hover:border-red-500/50 font-bold text-sm"
                >
                  Ban Member
                </button>
              )}
            </div>
          )}

          {/* Self indicator */}
          {isSelf && (
            <div className="mt-4 px-3 py-2 bg-[#4fdfff]/10 rounded-lg border border-[#4fdfff]/30 text-center">
              <p className="text-xs text-[#4fdfff] font-medium">This is you!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

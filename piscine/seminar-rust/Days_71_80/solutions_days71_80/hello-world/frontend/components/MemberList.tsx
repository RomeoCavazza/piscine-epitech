import { ServerMember } from "@/lib/api-server";

interface MemberListProps {
  members: ServerMember[];
  currentUserId?: string;
  onMemberClick: (member: ServerMember) => void;
}

export default function MemberList({ members, currentUserId, onMemberClick }: MemberListProps) {
  const owners = members.filter(m => m.role === "Owner");
  const regularMembers = members.filter(m => m.role !== "Owner");

  const getMemberAvatar = (member: ServerMember) => {
    if (member.avatar_url) {
      const url = member.avatar_url.startsWith('/') 
        ? `http://localhost:3001${member.avatar_url}` 
        : member.avatar_url;
      return url;
    }
    const hex = member.user_id.replace(/-/g, '').slice(0, 2);
    const num = parseInt(hex, 16);
    const avatarNum = (num % 100) + 1;
    return `/avatars/avatar${avatarNum}.png`;
  };

  return (
    <div className="flex-1 overflow-y-auto p-2">
      {members.length === 0 ? (
        <p className="text-sm text-white/40 italic px-2">Aucun membre</p>
      ) : (
        <>
          {/* Owners */}
          {owners.length > 0 && (
            <div className="mb-4">
              <p className="text-[10px] text-[#ff3333] font-bold mb-2 px-2 tracking-wider uppercase">
                PROPRIÉTAIRE
              </p>
              {owners.map((member) => (
                <div
                  key={member.user_id}
                  className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-white/5 cursor-pointer transition-colors"
                  onClick={() => onMemberClick(member)}
                >
                  <div className="relative">
                    <img 
                      src={getMemberAvatar(member)} 
                      alt="Owner"
                      className="w-8 h-8 rounded-full object-cover border border-[#ff3333]/50"
                    />
                    <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-[rgba(5,10,15,0.95)] rounded-full" />
                  </div>
                  <span className="text-sm text-white/90 truncate">
                    {member.username}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Regular Members */}
          {regularMembers.length > 0 && (
            <div>
              <p className="text-[10px] text-white/50 font-bold mb-2 px-2 tracking-wider uppercase">
                MEMBRES
              </p>
              {regularMembers.map((member) => (
                <div
                  key={member.user_id}
                  className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-white/5 transition-colors cursor-pointer"
                  onClick={() => onMemberClick(member)}
                >
                  <div className="relative">
                    <img 
                      src={getMemberAvatar(member)} 
                      alt="Member"
                      className="w-8 h-8 rounded-full object-cover border border-[#4fdfff]/30"
                    />
                    <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-gray-500 border-2 border-[rgba(5,10,15,0.95)] rounded-full" />
                  </div>
                  <span className="text-sm text-white/70 truncate flex-1">
                    {member.username}
                  </span>
                  {member.role === "Admin" && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#4fdfff]/20 text-[#4fdfff] font-bold">
                      ADMIN
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

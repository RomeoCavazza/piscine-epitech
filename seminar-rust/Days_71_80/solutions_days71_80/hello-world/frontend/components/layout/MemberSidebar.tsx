"use client";

import { Server, ServerMember, User } from "@/lib/api-server";
import { getAvatar } from "@/lib/avatar";
import { useState } from "react";

type Props = {
  selectedServer: Server | null;
  members: ServerMember[];
  currentUser: User | null;
  authUser: User | null;
  onInviteClick: () => void;
  onKickMember?: (userId: string) => Promise<void>;
  onUpdateRole?: (userId: string, role: "Admin" | "Member") => Promise<void>;
};

export default function MemberSidebar({
  selectedServer,
  members,
  currentUser,
  authUser,
  onInviteClick,
  onKickMember,
  onUpdateRole,
}: Props) {
  const userForAvatar = currentUser || authUser;
  const [showMenu, setShowMenu] = useState<string | null>(null);

  const authMember = members.find((m) => m.user_id === authUser?.id);
  const canManage = authMember?.role === "Owner" || authMember?.role === "Admin";

  const handleKick = async (userId: string) => {
    if (confirm("Are you sure you want to kick this member?")) {
      await onKickMember?.(userId);
      setShowMenu(null);
    }
  };

  const handleRoleChange = async (userId: string, role: "Admin" | "Member") => {
    await onUpdateRole?.(userId, role);
    setShowMenu(null);
  };

  return (
    <aside className="w-[260px] p-5 bg-[rgba(20,20,20,0.85)] backdrop-blur-[12px] flex flex-col border-l-2 border-[#4fdfff] rounded-xl shadow-[0_20px_60px_rgba(0,0,0,0.5)] animate-fade-in" style={{ animationDelay: "0.3s" }}>
      {/* Header + bouton + */}
      <div className="flex items-center justify-between mt-[15px] mb-[6px]">
        <h3 className="text-[12px] tracking-wider uppercase text-[#4fdfff] font-bold">
          MEMBERS {selectedServer && `(${members.length})`}
        </h3>

        {selectedServer && (
          <button
            onClick={onInviteClick}
            className="text-[#4fdfff] hover:text-white text-lg font-bold"
            title="Invite member"
          >
            +
          </button>
        )}
      </div>

      {!selectedServer ? (
        <p className="text-[14px] text-white/40 italic">Select a server</p>
      ) : members.length === 0 ? (
        <p className="text-[14px] text-white/40 italic">No members</p>
      ) : (
        <>
          {/* Owners */}
          {members.filter((m) => m.role === "Owner").length > 0 && (
            <div className="mb-4">
              <p className="text-[10px] text-[#ff3333] font-bold mb-2 tracking-wider uppercase">
                OWNER
              </p>

              {members
                .filter((m) => m.role === "Owner")
                .map((member) => (
                  <div
                    key={member.user_id}
                    className="flex items-center gap-2 py-2 px-2 rounded-lg hover:bg-white/5 cursor-pointer transition-colors relative"
                  >
                    <div className="relative">
                      <img
                        src={getAvatar(member.user_id, userForAvatar)}
                        alt="Owner"
                        className="w-8 h-8 rounded-full object-cover border-2 border-[#ff3333]/50"
                      />
                      <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-[rgba(20,20,20,0.85)] rounded-full" />
                    </div>

                    <span className="text-sm text-white/80 truncate flex-1">
                      {member.user_id.slice(0, 8)}...
                    </span>
                  </div>
                ))}
            </div>
          )}

          {/* Members */}
          {members.filter((m) => m.role !== "Owner").length > 0 && (
            <div>
              <p className="text-[10px] text-white/50 font-bold mb-2 tracking-wider uppercase">
                MEMBERS
              </p>

              {members
                .filter((m) => m.role !== "Owner")
                .map((member) => {
                  const isOwner = member.role === "Owner";
                  const isSelf = member.user_id === authUser?.id;

                  return (
                    <div
                      key={member.user_id}
                      className="flex items-center gap-2 py-2 px-2 rounded-lg hover:bg-white/5 cursor-pointer transition-colors relative"
                      onContextMenu={(e) => {
                        if (canManage && !isOwner && !isSelf) {
                          e.preventDefault();
                          setShowMenu(showMenu === member.user_id ? null : member.user_id);
                        }
                      }}
                    >
                      <div className="relative">
                        <img
                          src={getAvatar(member.user_id, userForAvatar)}
                          alt="Member"
                          className="w-8 h-8 rounded-full object-cover border border-[#4fdfff]/30"
                        />
                        <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-gray-500 border-2 border-[rgba(20,20,20,0.85)] rounded-full" />
                      </div>

                      <span className="text-sm text-white/60 truncate flex-1">
                        {member.user_id.slice(0, 8)}...
                      </span>

                      {member.role === "Admin" && (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-[#4fdfff]/20 text-[#4fdfff] font-bold">
                          ADMIN
                        </span>
                      )}

                      {canManage && !isOwner && !isSelf && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowMenu(showMenu === member.user_id ? null : member.user_id);
                          }}
                          className="text-white/40 hover:text-white text-lg px-1"
                        >
                          ⋮
                        </button>
                      )}

                      {/* Context Menu */}
                      {showMenu === member.user_id && (
                        <div className="absolute right-0 top-full mt-1 bg-[#1a1a1a] border border-[#4fdfff]/30 rounded-lg shadow-lg z-50 min-w-[120px]">
                          {member.role === "Member" && (
                            <button
                              onClick={() => handleRoleChange(member.user_id, "Admin")}
                              className="w-full px-3 py-2 text-left text-sm text-white/80 hover:bg-white/10 rounded-t-lg"
                            >
                              Make Admin
                            </button>
                          )}
                          {member.role === "Admin" && (
                            <button
                              onClick={() => handleRoleChange(member.user_id, "Member")}
                              className="w-full px-3 py-2 text-left text-sm text-white/80 hover:bg-white/10 rounded-t-lg"
                            >
                              Remove Admin
                            </button>
                          )}
                          <button
                            onClick={() => handleKick(member.user_id)}
                            className="w-full px-3 py-2 text-left text-sm text-red-400 hover:bg-red-500/10 rounded-b-lg"
                          >
                            Kick Member
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
            </div>
          )}
        </>
      )}

      {/* Server info */}
      {selectedServer && (
        <div className="mt-auto pt-4 border-t border-[#4fdfff]/30">
          <h3 className="text-[12px] tracking-wider uppercase text-[#4fdfff] mb-2 font-bold">
            SERVER INFO
          </h3>
          <p className="text-[14px] text-white/80">{selectedServer.name}</p>
          <p className="text-[10px] text-white/40 font-mono mt-1">
            ID: {selectedServer.id.slice(0, 8)}...
          </p>
        </div>
      )}
    </aside>
  );
}
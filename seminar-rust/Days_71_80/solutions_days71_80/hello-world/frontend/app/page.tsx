"use client";
import { useState } from "react";
import Image from "next/image";
import { logout } from "@/lib/auth/actions";
import { useServers, useChannels, useMessages, useMembers, useAuth } from "@/hooks";
import ProfileCard from "@/components/ProfileCard";
import InviteModal from "@/modals/InviteModal";
import MemberProfileModal from "@/components/modals/MemberProfileModal";
import { User, ServerMember } from "@/lib/api-server";
import Button from "@/components/ui/Button";

/**
 * Normalise le chemin d'avatar (ancien format → nouveau format)
 */
function normalizeAvatarUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  // Convertit l'ancien chemin vers le nouveau
  if (url.includes('/space_invaders_avatars/space_invader_')) {
    return url
      .replace('/space_invaders_avatars/', '/avatars/')
      .replace('space_invader_', 'avatar_');
  }
  return url;
}

/**
 * Génère une URL d'avatar déterministe basée sur un UUID
 * Utilise le premier caractère hexa pour choisir parmi les 100 avatars
 */
function getAvatarFromId(id: string): string {
  // Prend les 2 premiers caractères hexa et les convertit en nombre (0-255)
  const hex = id.replace(/-/g, '').slice(0, 2);
  const num = parseInt(hex, 16);
  // Map sur 1-100
  const avatarNum = (num % 100) + 1;
  return `/avatars/avatar_${String(avatarNum).padStart(3, '0')}.png`;
}

/**
 * Retourne l'avatar approprié : si c'est l'utilisateur connecté, utilise son avatar réel
 */
function getAvatar(userId: string, currentUser: User | null): string {
  if (currentUser && userId === currentUser.id) {
    return normalizeAvatarUrl(currentUser.avatar_url) || getAvatarFromId(userId);
  }
  return getAvatarFromId(userId);
}

/**
 * Génère l'URL d'avatar pour un membre avec avatar_url optionnel
 */
function getMemberAvatar(member: { user_id: string; avatar_url?: string }): string {
  return normalizeAvatarUrl(member.avatar_url) || getAvatarFromId(member.user_id);
}

/**
 * Page principale - Design Moderne Cyberpunk
 * Layout: SERVER SIDEBAR (72px) | CHANNEL SIDEBAR (240px) | CHAT CENTER | MEMBERS SIDEBAR (240px)
 */
export default function Home() {
  const { user } = useAuth();
  const {
    servers,
    selectedServer,
    selectServer,
    createServer,
    updateServer,
    deleteServer,
    loading: serversLoading,
    error: serversError,
  } = useServers();

  const { channels, selectedChannel, selectChannel, createChannel, deleteChannel, loading: channelsLoading, error: channelsError } = useChannels(
    selectedServer?.id ?? null
  );

  const { messages, sendMessage, updateMessage, loading: messagesLoading, error: messagesError } = useMessages(selectedChannel?.id ?? null);
  const { members, updateRole, kickMember: kickMemberHook, banMember: banMemberHook } = useMembers(selectedServer?.id ?? null);

  const [showCreateServer, setShowCreateServer] = useState(false);
  const [newServerName, setNewServerName] = useState("");
  const [showCreateChannel, setShowCreateChannel] = useState(false);
  const [newChannelName, setNewChannelName] = useState("");
  const [messageInput, setMessageInput] = useState("");
  const [showProfile, setShowProfile] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showMemberMenu, setShowMemberMenu] = useState<string | null>(null);
  const [selectedMember, setSelectedMember] = useState<ServerMember | null>(null);
  const [showServerMenu, setShowServerMenu] = useState(false);
  const [editingMessage, setEditingMessage] = useState<{id: string, content: string} | null>(null);

  // Initialize currentUser from useAuth
  if (user && !currentUser) {
    setCurrentUser(user as User);
  }

  // Style des boutons action (rouge + bordure cyan)

  // Handlers
  const handleCreateServer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newServerName.trim()) return;
    const server = await createServer(newServerName.trim());
    if (server) {
      setNewServerName("");
      setShowCreateServer(false);
    }
  };

  const handleCreateChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newChannelName.trim()) return;
    await createChannel(newChannelName.trim());
    setNewChannelName("");
    setShowCreateChannel(false);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim()) return;
    await sendMessage(messageInput.trim());
    setMessageInput("");
  };

  if (serversLoading) {
    return (
      <main className="flex w-full h-screen gap-2 p-2 items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-2 border-[#4fdfff] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-[#4fdfff] font-mono text-sm tracking-widest animate-pulse">
            INITIALIZING SYSTEM...
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex w-full h-screen">
      
      {/* ========== SERVER SIDEBAR (72px) - Compacte avec icônes circulaires ========== */}
      <aside className="w-[72px] bg-[rgba(0,0,0,0.95)] border-r border-[#4fdfff]/20 flex flex-col items-center py-3 gap-2">
        {/* Logo */}
        <button
          onClick={() => selectServer(null)}
          className="w-12 h-12 rounded-2xl bg-[#4fdfff]/10 border border-[#4fdfff]/50 flex items-center justify-center mb-2 hover:rounded-xl hover:bg-[#4fdfff]/20 transition-all cursor-pointer group"
          title="Hello World"
        >
          <Image
            src="/logo.png"
            alt="HW"
            width={32}
            height={32}
            className="group-hover:scale-110 transition-transform"
          />
        </button>

        <div className="w-8 h-[2px] bg-[#4fdfff]/20 rounded-full" />

        {/* Server list */}
        <div className="flex-1 w-full overflow-y-auto flex flex-col items-center gap-2 py-2">
          {servers.map((server) => (
            <button
              key={server.id}
              onClick={() => selectServer(server)}
              className={`w-12 h-12 rounded-[24px] flex items-center justify-center text-lg font-bold transition-all duration-200 relative group ${
                selectedServer?.id === server.id
                  ? "bg-[#4fdfff] text-black rounded-xl shadow-[0_0_12px_rgba(79,223,255,0.6)]"
                  : "bg-[rgba(20,30,40,0.8)] text-[#4fdfff] hover:bg-[#4fdfff]/20 hover:rounded-xl"
              }`}
              title={server.name}
            >
              {server.name.charAt(0).toUpperCase()}
              {/* Indicator bar */}
              <span
                className={`absolute left-0 w-1 bg-[#4fdfff] rounded-r transition-all ${
                  selectedServer?.id === server.id ? "h-10" : "h-0 group-hover:h-5"
                }`}
              />
            </button>
          ))}
        </div>

        {/* Add server button */}
        <button
          onClick={() => setShowCreateServer(true)}
          className="w-12 h-12 rounded-[24px] bg-[rgba(20,30,40,0.8)] border border-dashed border-[#4fdfff]/30 flex items-center justify-center text-[#4fdfff] hover:bg-[#4fdfff]/10 hover:border-[#4fdfff] hover:rounded-xl transition-all group"
          title="Créer un serveur"
        >
          <span className="text-2xl group-hover:rotate-90 transition-transform">+</span>
        </button>

        {/* Logout */}
        <button
          onClick={() => logout()}
          className="w-12 h-12 rounded-[24px] bg-[rgba(40,10,10,0.8)] flex items-center justify-center text-[#ff3333] hover:bg-[#ff3333]/20 hover:rounded-xl transition-all mt-2"
          title="Déconnexion"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </aside>

      {/* ========== CHANNEL SIDEBAR (240px) ========== */}
      {selectedServer ? (
        <aside className="w-60 bg-[rgba(5,10,15,0.95)] border-r border-[#4fdfff]/20 flex flex-col">
          {/* Server header with dropdown menu */}
          <div className="relative group h-12 px-4 flex items-center border-b border-[#4fdfff]/30 shadow-lg bg-[rgba(0,0,0,0.3)]">
            <h2 className="font-bold text-white truncate flex-1">{selectedServer.name}</h2>
            <button
              onClick={() => setShowServerMenu(!showServerMenu)}
              className="text-[#4fdfff] text-xs font-mono hover:text-white transition-colors"
            >
              ▼
            </button>
            
            {/* Server dropdown menu */}
            {showServerMenu && (
              <div className="absolute top-full left-0 right-0 bg-[rgba(10,10,10,0.98)] border border-[#4fdfff]/30 rounded-b-lg shadow-2xl z-50 py-2">
                <button
                  onClick={async () => {
                    const newName = prompt("New server name:", selectedServer.name);
                    if (newName && newName.trim() && newName !== selectedServer.name) {
                      await updateServer(selectedServer.id, newName.trim());
                      setShowServerMenu(false);
                    }
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-white/80 hover:bg-white/10 transition-colors"
                >
                  Rename Server
                </button>
                <button
                  onClick={async () => {
                    if (confirm(`Delete server "${selectedServer.name}"? This will delete ALL channels and messages. This cannot be undone.`)) {
                      const success = await deleteServer(selectedServer.id);
                      if (success) {
                        selectServer(null);
                        setShowServerMenu(false);
                      }
                    }
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-red-500/20 transition-colors font-bold"
                >
                  Delete Server
                </button>
              </div>
            )}
          </div>

          {/* Channels */}
          <div className="flex-1 overflow-y-auto p-2">
            <div className="flex items-center justify-between px-2 mb-2">
              <span className="text-[10px] font-bold text-white/50 tracking-widest uppercase">
                CHANNELS TEXTUELS
              </span>
              <button
                onClick={() => setShowCreateChannel(true)}
                className="text-white/50 hover:text-[#4fdfff] transition-colors text-lg font-bold"
                title="Créer un channel"
              >
                +
              </button>
            </div>

            <div className="space-y-[2px]">
              {channelsLoading ? (
                <div className="px-2 py-2 text-white/40 text-sm">Chargement...</div>
              ) : channelsError ? (
                <div className="px-2 py-2 text-[#ff3333] text-sm">{channelsError}</div>
              ) : channels.length === 0 ? (
                <div className="px-2 py-2 text-white/40 text-sm italic">Aucun channel</div>
              ) : (
                channels.map((channel) => (
                  <div
                    key={channel.id}
                    className={`group relative w-full text-left px-2 py-1.5 rounded flex items-center gap-2 transition-colors ${
                      selectedChannel?.id === channel.id
                        ? "bg-[#4fdfff]/15 text-white"
                        : "text-white/60 hover:bg-white/5 hover:text-white"
                    }`}
                  >
                    <button
                      onClick={() => selectChannel(channel)}
                      className="flex-1 flex items-center gap-2 min-w-0"
                    >
                      <span className="text-white/40">#</span>
                      <span className="truncate text-sm">{channel.name}</span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        e.preventDefault();
                        setTimeout(async () => {
                          await deleteChannel(channel.id);
                          if (selectedChannel?.id === channel.id) {
                            selectChannel(null);
                          }
                        }, 100);
                      }}
                      className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-all px-1"
                      title="Delete channel"
                    >
                      ✕
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* User info footer */}
          <div className="h-14 px-2 flex items-center gap-2 bg-[rgba(0,0,0,0.5)] border-t border-[#4fdfff]/20">
            <button
              onClick={() => setShowProfile(true)}
              className="flex items-center gap-2 flex-1 min-w-0 hover:bg-white/5 rounded p-1 transition-colors"
            >
              <div className="relative flex-shrink-0">
                {(currentUser || user)?.avatar_url ? (
                  <img 
                    src={normalizeAvatarUrl((currentUser || user)?.avatar_url) || ''} 
                    alt="Avatar" 
                    className="w-8 h-8 rounded-full object-cover border border-[#4fdfff]/50"
                  />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-[#4fdfff]/20 border border-[#4fdfff]/50 flex items-center justify-center">
                    <span className="text-[#4fdfff] text-xs font-bold">
                      {(currentUser || user)?.username?.charAt(0).toUpperCase() || "?"}
                    </span>
                  </div>
                )}
                {/* Status indicator */}
                <span className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 border-2 border-[rgba(5,10,15,0.95)] rounded-full ${
                  (currentUser || user)?.status?.toLowerCase() === "online" ? "bg-green-500" :
                  (currentUser || user)?.status?.toLowerCase() === "dnd" ? "bg-red-500" :
                  (currentUser || user)?.status?.toLowerCase() === "invisible" ? "bg-gray-400" :
                  "bg-gray-500"
                }`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{(currentUser || user)?.username || "Guest"}</p>
                <p className="text-[10px] text-[#4fdfff] font-mono uppercase">
                  {(currentUser || user)?.status || "CONNECTED"}
                </p>
              </div>
            </button>
          </div>
        </aside>
      ) : (
        <aside className="w-60 bg-[rgba(5,10,15,0.95)] border-r border-[#4fdfff]/20 flex flex-col items-center justify-center">
          <p className="text-white/40 text-sm text-center px-4">Sélectionnez un serveur</p>
        </aside>
      )}

      {/* ========== CHAT CENTER ========== */}
      <div className="flex-1 flex flex-col bg-[rgba(10,15,20,0.98)]">
        {/* Header */}
        <header className="h-12 px-4 flex items-center border-b border-[#4fdfff]/20 bg-[rgba(0,0,0,0.3)] shadow-sm">
          <h1 className="text-white font-semibold text-sm flex items-center gap-2">
            {selectedChannel ? (
              <>
                <span className="text-white/40">#</span>
                <span>{selectedChannel.name}</span>
              </>
            ) : selectedServer ? (
              <>
                <span className="text-[#4fdfff]">{selectedServer.name}</span>
                <span className="text-white/40 text-xs font-normal">- Sélectionnez un canal</span>
              </>
            ) : (
              <>
                <span className="text-[#4fdfff]">HELLO WORLD</span>
                <span className="text-white/40 text-xs font-normal">- Sélectionnez un serveur</span>
              </>
            )}
          </h1>
        </header>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-4">
          {!selectedChannel ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="w-24 h-24 rounded-full bg-[#4fdfff]/10 border-2 border-[#4fdfff]/30 flex items-center justify-center mb-6 mx-auto">
                  <span className="text-5xl text-[#4fdfff]">#</span>
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  {selectedServer ? "Sélectionnez un canal" : "Sélectionnez un serveur"}
                </h2>
                <p className="text-white/50 text-sm">
                  {selectedServer ? "Choisissez un canal pour commencer à discuter" : "Choisissez un serveur pour commencer"}
                </p>
              </div>
            </div>
          ) : messagesLoading ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="w-8 h-8 border-2 border-[#4fdfff] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                <p className="text-[#4fdfff] text-sm">Chargement des messages...</p>
              </div>
            </div>
          ) : messagesError ? (
            <div className="h-full flex items-center justify-center">
              <p className="text-[#ff3333]">{messagesError}</p>
            </div>
          ) : Array.isArray(messages) && messages.length > 0 ? (
            <div className="space-y-4">
              {messages.map((msg) => {
                const messageMember = members.find(m => m.user_id === msg.author_id);
                return (
                  <div key={msg.id} className="flex items-start gap-3 px-4 py-2 rounded hover:bg-white/5 transition-colors group">
                    <img 
                      src={getAvatar(msg.author_id, currentUser || user)} 
                      alt={msg.username}
                      onClick={() => {
                        if (msg.author_id === user?.id) {
                          setShowProfile(true);
                        } else if (messageMember) {
                          setSelectedMember(messageMember);
                        }
                      }}
                      className="w-10 h-10 rounded-full object-cover border border-[#4fdfff]/30 flex-shrink-0 group-hover:border-[#4fdfff]/50 transition-colors cursor-pointer"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline gap-2 mb-1">
                        <span 
                          onClick={() => {
                            if (msg.author_id === user?.id) {
                              setShowProfile(true);
                            } else if (messageMember) {
                              setSelectedMember(messageMember);
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
                      </div>
                      {editingMessage?.id === msg.id ? (
                        <div className="flex-1">
                          <input
                            type="text"
                            value={editingMessage.content}
                            onChange={(e) => setEditingMessage({ ...editingMessage, content: e.target.value })}
                            onBlur={async () => {
                              if (editingMessage.content.trim() && editingMessage.content !== msg.content) {
                                await updateMessage(editingMessage.id, editingMessage.content);
                              }
                              setEditingMessage(null);
                            }}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                e.currentTarget.blur();
                              } else if (e.key === 'Escape') {
                                setEditingMessage(null);
                              }
                            }}
                            autoFocus
                            className="w-full px-3 py-1.5 bg-black/50 border border-[#4fdfff] rounded text-white text-sm outline-none"
                          />
                          <p className="text-xs text-white/40 mt-1">Entrée pour sauver • Échap pour annuler</p>
                        </div>
                      ) : (
                        <p 
                          className="text-white/90 leading-relaxed break-words cursor-text hover:bg-white/5 px-2 py-1 rounded transition-colors"
                          onDoubleClick={() => {
                            if (msg.author_id === user?.id) {
                              const createdAt = new Date(msg.created_at).getTime();
                              const now = Date.now();
                              const fiveMinutes = 5 * 60 * 1000;
                              if (now - createdAt < fiveMinutes) {
                                setEditingMessage({ id: msg.id, content: msg.content });
                              }
                            }
                          }}
                        >
                          {msg.content}
                          {msg.edited_at && <span className="text-xs text-white/30 ml-2 italic">(modifié)</span>}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center px-4">
              <div className="w-20 h-20 rounded-full bg-[#4fdfff]/10 border-2 border-[#4fdfff]/30 flex items-center justify-center mb-4">
                <span className="text-4xl text-[#4fdfff]">#</span>
              </div>
              <h4 className="text-xl font-semibold text-white mb-2">
                Bienvenue dans #{selectedChannel.name}
              </h4>
              <p className="text-white/50 text-sm">
                C'est le début de ce canal. Envoyez un message pour commencer !
              </p>
            </div>
          )}
        </div>

        {/* Message input */}
        {selectedChannel && (
          <footer className="px-4 py-3 border-t border-[#4fdfff]/20 bg-[rgba(0,0,0,0.2)]">
            <form onSubmit={handleSendMessage}>
              <input 
                type="text"
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                placeholder={`Message #${selectedChannel.name}`}
                className="w-full px-4 py-2.5 bg-[rgba(20,20,20,0.8)] border border-[#4fdfff]/30 rounded-lg text-white placeholder:text-white/40 outline-none focus:border-[#4fdfff] focus:bg-[rgba(20,20,20,0.95)] focus:shadow-[0_0_8px_rgba(79,223,255,0.3)] transition-all"
              />
            </form>
          </footer>
        )}
      </div>

      {/* ========== MEMBERS SIDEBAR (240px) ========== */}
      {selectedServer ? (
        <aside className="w-60 bg-[rgba(5,10,15,0.95)] border-l border-[#4fdfff]/20 flex flex-col">
          {/* Header */}
          <div className="h-12 px-4 flex items-center justify-between border-b border-[#4fdfff]/20 bg-[rgba(0,0,0,0.3)]">
            <h3 className="text-xs font-bold text-white/60 uppercase tracking-wider">
              MEMBRES — {members.length}
            </h3>
            <button
              onClick={() => setShowInviteModal(true)}
              className="text-[#4fdfff] hover:text-white text-lg font-bold"
              title="Invite member"
            >
              +
            </button>
          </div>

          {/* Members list */}
          <div className="flex-1 overflow-y-auto p-2">
            {members.length === 0 ? (
              <p className="text-sm text-white/40 italic px-2">Aucun membre</p>
            ) : (
              <>
                {/* Owners */}
                {members.filter((m) => m.role === "Owner").length > 0 && (
                  <div className="mb-4">
                    <p className="text-[10px] text-[#ff3333] font-bold mb-2 px-2 tracking-wider uppercase">
                      PROPRIÉTAIRE
                    </p>
                    {members
                      .filter((m) => m.role === "Owner")
                      .map((member) => {
                        return (
                          <div
                            key={member.user_id}
                            className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-white/5 cursor-pointer transition-colors"
                            onClick={() => {
                              if (member.user_id === user?.id) {
                                setShowProfile(true);
                              } else {
                                setSelectedMember(member);
                              }
                            }}
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
                        );
                      })}
                  </div>
                )}

                {/* Regular members */}
                {members.filter((m) => m.role !== "Owner").length > 0 && (
                  <div>
                    <p className="text-[10px] text-white/50 font-bold mb-2 px-2 tracking-wider uppercase">
                      MEMBRES
                    </p>
                    {members
                      .filter((m) => m.role !== "Owner")
                      .map((member) => {
                        const isOwner = member.role === "Owner";
                        const isSelf = member.user_id === user?.id;
                        const authMember = members.find(m => m.user_id === user?.id);
                        const canManage = authMember?.role === "Owner" || authMember?.role === "Admin";

                        return (
                          <div
                            key={member.user_id}
                            className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-white/5 transition-colors relative"
                            onContextMenu={(e) => {
                              if (canManage && !isOwner && !isSelf) {
                                e.preventDefault();
                                setShowMemberMenu(showMemberMenu === member.user_id ? null : member.user_id);
                              }
                            }}
                          >
                            <div 
                              className="relative cursor-pointer"
                            onClick={() => {
                              if (member.user_id === user?.id) {
                                setShowProfile(true);
                              } else {
                                setSelectedMember(member);
                              }
                            }}
                          >
                            <img 
                              src={getMemberAvatar(member)} 
                              alt="Member"
                              className="w-8 h-8 rounded-full object-cover border border-[#4fdfff]/30"
                            />
                            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-gray-500 border-2 border-[rgba(5,10,15,0.95)] rounded-full" />
                          </div>
                          <span 
                            className="text-sm text-white/70 truncate flex-1 cursor-pointer hover:text-white transition-colors"
                            onClick={() => {
                              if (member.user_id === user?.id) {
                                setShowProfile(true);
                              } else {
                                setSelectedMember(member);
                              }
                            }}
                            >
                              {member.username}
                            </span>
                            {member.role === "Admin" && (
                              <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#4fdfff]/20 text-[#4fdfff] font-bold">
                                ADMIN
                              </span>
                            )}
                            {canManage && !isOwner && !isSelf && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setShowMemberMenu(showMemberMenu === member.user_id ? null : member.user_id);
                                }}
                                className="text-white/40 hover:text-white text-lg px-1"
                              >
                                ⋮
                              </button>
                            )}

                            {/* Context Menu */}
                            {showMemberMenu === member.user_id && (
                              <div className="absolute right-0 top-full mt-1 bg-[#1a1a1a] border border-[#4fdfff]/30 rounded-lg shadow-lg z-50 min-w-[120px]">
                                {member.role === "Member" && (
                                  <button
                                    onClick={async () => {
                                      await updateRole(member.user_id, "Admin");
                                      setShowMemberMenu(null);
                                    }}
                                    className="w-full px-3 py-2 text-left text-sm text-white/80 hover:bg-white/10 rounded-t-lg"
                                  >
                                    Make Admin
                                  </button>
                                )}
                                {member.role === "Admin" && (
                                  <button
                                    onClick={async () => {
                                      await updateRole(member.user_id, "Member");
                                      setShowMemberMenu(null);
                                    }}
                                    className="w-full px-3 py-2 text-left text-sm text-white/80 hover:bg-white/10 rounded-t-lg"
                                  >
                                    Remove Admin
                                  </button>
                                )}
                                <button
                                  onClick={async (e) => {
                                    e.stopPropagation();
                                    e.preventDefault();
                                    await kickMemberHook(member.user_id);
                                    setShowMemberMenu(null);
                                  }}
                                  className="w-full px-3 py-2 text-left text-sm text-yellow-400 hover:bg-yellow-500/10"
                                >
                                  Kick Member
                                </button>
                                <button
                                  onClick={async (e) => {
                                    e.stopPropagation();
                                    e.preventDefault();
                                    await banMemberHook(member.user_id, {
                                      reason: 'Banned by admin',
                                      is_permanent: true,
                                    });
                                    setShowMemberMenu(null);
                                  }}
                                  className="w-full px-3 py-2 text-left text-sm text-red-500 hover:bg-red-500/20 rounded-b-lg font-bold"
                                >
                                  Ban Member (Permanent)
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
          </div>
        </aside>
      ) : (
        <aside className="w-60 bg-[rgba(5,10,15,0.95)] border-l border-[#4fdfff]/20 flex flex-col items-center justify-center">
          <p className="text-white/40 text-sm text-center px-4">Sélectionnez un serveur</p>
        </aside>
      )}

      {/* ========== MODAL CREATE SERVER ========== */}
      {showCreateServer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setShowCreateServer(false)} />
          <div className="relative bg-[rgba(20,20,20,0.98)] border-2 border-[#4fdfff] rounded-xl p-6 w-full max-w-md shadow-[0_0_40px_rgba(79,223,255,0.3)]">
            <h2 className="text-xl font-bold text-center text-white mb-1">CREATE SERVER</h2>
            <p className="text-center text-white/50 text-sm mb-6">
              Your server will be your discussion space
            </p>
            {serversError && (
              <div className="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-4 text-sm">
                {serversError}
              </div>
            )}
            <form onSubmit={handleCreateServer}>
              <label className="block text-[10px] font-bold text-[#4fdfff] tracking-widest uppercase mb-2">
                SERVER NAME
              </label>
              <input
                type="text"
                value={newServerName}
                onChange={(e) => setNewServerName(e.target.value)}
                placeholder="My Server"
                autoFocus
                className="w-full px-4 py-3 bg-black/50 border-2 border-[#4fdfff]/50 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:border-[#4fdfff] focus:shadow-[0_0_10px_rgba(79,223,255,0.3)] mb-6 transition-all"
              />
              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  size="md"
                  onClick={() => setShowCreateServer(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  disabled={!newServerName.trim()}
                  className="flex-1 uppercase"
                >
                  Create
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========== MODAL CREATE CHANNEL ========== */}
      {showCreateChannel && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setShowCreateChannel(false)} />
          <div className="relative bg-[rgba(20,20,20,0.98)] border-2 border-[#4fdfff] rounded-xl p-6 w-full max-w-md shadow-[0_0_40px_rgba(79,223,255,0.3)]">
            <h2 className="text-xl font-bold text-center text-white mb-1">CREATE CHANNEL</h2>
            <p className="text-center text-white/50 text-sm mb-6">
              in {selectedServer?.name}
            </p>
            <form onSubmit={handleCreateChannel}>
              <label className="block text-[10px] font-bold text-[#4fdfff] tracking-widest uppercase mb-2">
                CHANNEL NAME
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40 pointer-events-none">#</span>
                <input
                  type="text"
                  value={newChannelName}
                  onChange={(e) => setNewChannelName(e.target.value)}
                  placeholder="general"
                  autoFocus
                  className="w-full pl-8 pr-4 py-3 bg-black/50 border-2 border-[#4fdfff]/50 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:border-[#4fdfff] focus:shadow-[0_0_10px_rgba(79,223,255,0.3)] mb-6 transition-all"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowCreateChannel(false)}
                  className="flex-1 py-2.5 text-white/60 hover:text-white hover:underline transition-colors"
                >
                  Cancel
                </button>
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  disabled={!newChannelName.trim()}
                  className="flex-1 uppercase"
                >
                  Create
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========== MODAL PROFILE CARD ========== */}
      {showProfile && (currentUser || user) && (
        <ProfileCard
          user={(currentUser || user) as User}
          onClose={() => setShowProfile(false)}
          onUpdate={(updatedUser) => setCurrentUser(updatedUser)}
        />
      )}

      {/* ========== MODAL INVITE ========== */}
      {showInviteModal && selectedServer && (
        <InviteModal
          serverId={selectedServer.id}
          serverName={selectedServer.name}
          onClose={() => setShowInviteModal(false)}
        />
      )}

      {/* ========== MODAL MEMBER PROFILE ========== */}
      {selectedMember && (
        <MemberProfileModal
          member={selectedMember}
          currentUser={currentUser}
          onClose={() => {
            setSelectedMember(null);
            setShowMemberMenu(null);
          }}
          onChangeRole={async (role) => {
            await updateRole(selectedMember.user_id, role);
          }}
          onKick={async () => {
            if (confirm(`Kick ${selectedMember.username} from the server?`)) {
              await kickMemberHook(selectedMember.user_id);
            }
          }}
          onBan={async () => {
            const reason = prompt("Reason for ban (optional):");
            const isPermanent = confirm("Permanent ban? (Cancel for temporary 7-day ban)");
            const expires = isPermanent ? undefined : new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
            
            if (confirm(`Ban ${selectedMember.username}${isPermanent ? ' permanently' : ' for 7 days'}?`)) {
              await banMemberHook(selectedMember.user_id, {
                reason: reason || undefined,
                expires_at: expires,
                is_permanent: isPermanent,
              });
            }
          }}
          canManage={(() => {
            const authMember = members.find(m => m.user_id === user?.id);
            return authMember?.role === "Owner" || authMember?.role === "Admin";
          })()}
        />
      )}
    </main>
  );
}

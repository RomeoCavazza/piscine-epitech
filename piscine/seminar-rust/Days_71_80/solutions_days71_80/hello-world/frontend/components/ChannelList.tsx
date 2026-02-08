import { Channel } from "@/lib/api-server";

interface ChannelListProps {
  channels: Channel[];
  selectedChannelId: string | null;
  loading: boolean;
  error: string | null;
  onSelectChannel: (channel: Channel) => void;
  onDeleteChannel: (channelId: string) => void;
  onCreateChannel: () => void;
}

export default function ChannelList({
  channels,
  selectedChannelId,
  loading,
  error,
  onSelectChannel,
  onDeleteChannel,
  onCreateChannel
}: ChannelListProps) {
  return (
    <div className="flex-1 overflow-y-auto p-2">
      <div className="flex items-center justify-between px-2 mb-2">
        <span className="text-[10px] font-bold text-white/50 tracking-widest uppercase">
          CHANNELS TEXTUELS
        </span>
        <button
          onClick={onCreateChannel}
          className="text-white/50 hover:text-[#4fdfff] transition-colors text-lg font-bold"
          title="Créer un channel"
        >
          +
        </button>
      </div>

      <div className="space-y-[2px]">
        {loading ? (
          <div className="px-2 py-2 text-white/40 text-sm">Chargement...</div>
        ) : error ? (
          <div className="px-2 py-2 text-[#ff3333] text-sm">{error}</div>
        ) : channels.length === 0 ? (
          <div className="px-2 py-2 text-white/40 text-sm italic">Aucun channel</div>
        ) : (
          channels.map((channel) => (
            <div
              key={channel.id}
              className={`group relative w-full text-left px-2 py-1.5 rounded flex items-center gap-2 transition-colors ${
                selectedChannelId === channel.id
                  ? "bg-[#4fdfff]/15 text-white"
                  : "text-white/60 hover:bg-white/5 hover:text-white"
              }`}
            >
              <button
                onClick={() => onSelectChannel(channel)}
                className="flex-1 flex items-center gap-2 min-w-0"
              >
                <span className="text-white/40">#</span>
                <span className="truncate text-sm">{channel.name}</span>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteChannel(channel.id);
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
  );
}

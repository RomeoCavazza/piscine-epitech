"use client";

import { useState, useEffect, useCallback } from "react";
import { 
  listMembers, 
  ServerMember, 
  updateMemberRole, 
  kickMember as kickMemberApi, 
  banMember as banMemberApi,
  BanPayload
} from "@/lib/api-server";
import { handleAuthError, isAuthError, getErrorMessage } from "@/lib/auth/utils";
import { useWebSocket } from "./useWebSocket";
import { ServerEvent } from "@/lib/gateway";

export function useMembers(serverId: string | null) {
  const [members, setMembers] = useState<ServerMember[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // État pour stocker les statuts des utilisateurs (user_id -> status)
  const [userStatuses, setUserStatuses] = useState<Map<string, string>>(new Map());
  const { onEvent } = useWebSocket();

  const loadMembers = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await listMembers(id);
      setMembers(data);
    } catch (err) {
      const errorMessage = getErrorMessage(err, "Failed to load members");
      if (isAuthError(errorMessage)) {
        handleAuthError();
        return;
      }
      setError(errorMessage);
      setMembers([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (serverId) {
      loadMembers(serverId);
    } else {
      setMembers([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [serverId]);

  // Écouter les événements PRESENCE_UPDATE pour mettre à jour les statuts en temps réel
  useEffect(() => {
    const unsubscribe = onEvent((event: ServerEvent) => {
      if (event.op === "PRESENCE_UPDATE") {
        const { user_id, status } = event.d;
        setUserStatuses((prev) => {
          const next = new Map(prev);
          next.set(user_id, status);
          return next;
        });
      }
    });

    return unsubscribe;
  }, [onEvent]);

  const refresh = useCallback(() => {
    if (serverId) {
      loadMembers(serverId);
    }
  }, [serverId, loadMembers]);

  // Fonction helper pour obtenir le statut d'un utilisateur
  const getUserStatus = useCallback((userId: string): string => {
    return userStatuses.get(userId) || "offline";
  }, [userStatuses]);

  // Update member role
  const updateRole = useCallback(async (userId: string, role: "Admin" | "Member") => {
    if (!serverId) return;
    try {
      await updateMemberRole(serverId, userId, role);
      await loadMembers(serverId); // Refresh after update
    } catch (err) {
      const errorMessage = getErrorMessage(err, "Failed to update role");
      if (isAuthError(errorMessage)) {
        handleAuthError();
        return;
      }
      setError(errorMessage);
      throw err;
    }
  }, [serverId, loadMembers]);

  // Kick member
  const kickMember = useCallback(async (userId: string) => {
    if (!serverId) return;
    try {
      await kickMemberApi(serverId, userId);
      await loadMembers(serverId);
    } catch (err) {
      const errorMessage = getErrorMessage(err, "Failed to kick member");
      if (isAuthError(errorMessage)) {
        handleAuthError();
        return;
      }
      setError(errorMessage);
      throw err;
    }
  }, [serverId, loadMembers]);

  // Ban member
  const banMember = useCallback(async (userId: string, payload: BanPayload) => {
    if (!serverId) return;
    try {
      await banMemberApi(serverId, userId, payload);
      await loadMembers(serverId);
    } catch (err) {
      const errorMessage = getErrorMessage(err, "Failed to ban member");
      if (isAuthError(errorMessage)) {
        handleAuthError();
        return;
      }
      setError(errorMessage);
      throw err;
    }
  }, [serverId, loadMembers]);

  return {
    members,
    loading,
    error,
    refresh,
    getUserStatus,
    updateRole,
    kickMember,
    banMember,
  };
}


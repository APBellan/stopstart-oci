import { apiClient } from "./api";
import type { NavigationLevel } from "../types";

/**
 * Backend:
 * GET /api/v1/navigation?compartment_id=...
 */
export async function getNavigationLevel(
  compartmentId?: string
): Promise<NavigationLevel> {
  const query = compartmentId ? `?compartment_id=${compartmentId}` : "";
  return apiClient.get<NavigationLevel>(`/api/v1/navigation${query}`);
}

import { apiClient } from "./api";
import type { InstanceConfigResponse, InstanceConfig } from "../types";

/**
 * Backend:
 * GET /api/v1/instances/{instance_id}/config
 */
export async function getInstanceConfig(
  instanceId: string
): Promise<InstanceConfigResponse> {
  return apiClient.get<InstanceConfigResponse>(
    `/api/v1/instances/${instanceId}/config`
  );
}

/**
 * Backend:
 * PUT /api/v1/instances/{instance_id}/config
 */
export async function updateInstanceConfig(
  instanceId: string,
  data: InstanceConfig
): Promise<InstanceConfigResponse> {
  return apiClient.put<InstanceConfigResponse>(
    `/api/v1/instances/${instanceId}/config`,
    data
  );
}

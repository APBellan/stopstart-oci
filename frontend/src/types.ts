export interface Compartment {
  id: string;
  name: string;
  ocid: string;
}

export interface Instance {
  id: string;
  name: string;
  ocid: string;
  region: string;
  lifecycle_state: string;
}

export interface NavigationLevel {
  current_compartment: Compartment | null;
  breadcrumb: Compartment[];
  child_compartments: Compartment[];
  instances: Instance[];
}

export interface InstanceConfig {
  id?: string;
  instance_id: string;
  enabled: boolean;
  timezone: string;
  start_time: string | null; // "HH:MM"
  stop_time: string | null;  // "HH:MM"
  days_of_week: string[];    // ["MON", "TUE"...]
}

export interface InstanceConfigResponse extends InstanceConfig {}

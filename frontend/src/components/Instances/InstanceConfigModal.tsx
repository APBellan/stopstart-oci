import React, { useEffect, useState } from "react";
import type { Instance, InstanceConfig } from "../../types";
import {
  getInstanceConfig,
  updateInstanceConfig,
} from "../../services/instanceConfig";

interface Props {
  instance: Instance | null;
  open: boolean;
  onClose: () => void;
}

const DAYS = [
  { value: "MON", label: "Seg" },
  { value: "TUE", label: "Ter" },
  { value: "WED", label: "Qua" },
  { value: "THU", label: "Qui" },
  { value: "FRI", label: "Sex" },
  { value: "SAT", label: "Sáb" },
  { value: "SUN", label: "Dom" },
];

export function InstanceConfigModal({ instance, open, onClose }: Props) {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<InstanceConfig | null>(null);

  useEffect(() => {
    if (open && instance) {
      setLoading(true);
      setError(null);

      getInstanceConfig(instance.id)
        .then((cfg) => {
          setForm({
            instance_id: instance.id,
            enabled: cfg.enabled ?? false,
            timezone: cfg.timezone ?? "America/Sao_Paulo",
            start_time: cfg.start_time ?? null,
            stop_time: cfg.stop_time ?? null,
            days_of_week: cfg.days_of_week ?? [],
          });
        })
        .catch((err) => {
          console.error(err);
          // Se não existir config ainda, cria um default
          setForm({
            instance_id: instance.id,
            enabled: false,
            timezone: "America/Sao_Paulo",
            start_time: null,
            stop_time: null,
            days_of_week: [],
          });
        })
        .finally(() => setLoading(false));
    } else {
      setForm(null);
      setError(null);
    }
  }, [open, instance]);

  if (!open || !instance) return null;

  const handleChange = (field: keyof InstanceConfig, value: unknown) => {
    if (!form) return;
    setForm({ ...form, [field]: value } as InstanceConfig);
  };

  const toggleDay = (day: string) => {
    if (!form) return;
    const exists = form.days_of_week.includes(day);
    const days = exists
      ? form.days_of_week.filter((d) => d !== day)
      : [...form.days_of_week, day];
    handleChange("days_of_week", days);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form) return;
    setSaving(true);
    setError(null);
    try {
      await updateInstanceConfig(instance.id, form);
      onClose();
    } catch (err: any) {
      console.error(err);
      setError(err.message ?? "Erro ao salvar configuração");
    } finally {
      setSaving(false);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-md shadow-lg w-full max-w-md p-4">
        <h2 className="text-lg font-semibold mb-2">
          Configuração – {instance.name}
        </h2>

        {loading && <p>Carregando configuração...</p>}

        {!loading && form && (
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="flex items-center gap-2">
              <input
                id="enabled"
                type="checkbox"
                checked={form.enabled}
                onChange={(e) => handleChange("enabled", e.target.checked)}
              />
              <label htmlFor="enabled">Habilitar automação</label>
            </div>

            <div>
              <label className="block text-sm mb-1">Timezone</label>
              <input
                type="text"
                className="border rounded w-full px-2 py-1 text-sm"
                value={form.timezone}
                onChange={(e) => handleChange("timezone", e.target.value)}
              />
            </div>

            <div className="flex gap-2">
              <div className="flex-1">
                <label className="block text-sm mb-1">Horário de Start</label>
                <input
                  type="time"
                  className="border rounded w-full px-2 py-1 text-sm"
                  value={form.start_time ?? ""}
                  onChange={(e) =>
                    handleChange(
                      "start_time",
                      e.target.value ? e.target.value : null
                    )
                  }
                />
              </div>
              <div className="flex-1">
                <label className="block text-sm mb-1">Horário de Stop</label>
                <input
                  type="time"
                  className="border rounded w-full px-2 py-1 text-sm"
                  value={form.stop_time ?? ""}
                  onChange={(e) =>
                    handleChange(
                      "stop_time",
                      e.target.value ? e.target.value : null
                    )
                  }
                />
              </div>
            </div>

            <div>
              <label className="block text-sm mb-1">Dias da semana</label>
              <div className="flex flex-wrap gap-2">
                {DAYS.map((day) => {
                  const active = form.days_of_week.includes(day.value);
                  return (
                    <button
                      key={day.value}
                      type="button"
                      className={`px-2 py-1 text-xs border rounded ${
                        active
                          ? "bg-blue-600 text-white"
                          : "bg-white text-slate-800"
                      }`}
                      onClick={() => toggleDay(day.value)}
                    >
                      {day.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                className="px-3 py-1 text-sm border rounded"
                onClick={onClose}
                disabled={saving}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-3 py-1 text-sm rounded bg-blue-600 text-white"
                disabled={saving}
              >
                {saving ? "Salvando..." : "Salvar"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

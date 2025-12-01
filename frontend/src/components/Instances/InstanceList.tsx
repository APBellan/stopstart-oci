import React from "react";
import type { Instance } from "../../types";

interface Props {
  instances: Instance[];
  onConfigure: (instance: Instance) => void;
}

export function InstanceList({ instances, onConfigure }: Props) {
  if (!instances.length) {
    return <p className="text-sm text-slate-500">Nenhuma instância aqui.</p>;
  }

  return (
    <div>
      <h2 className="font-semibold mb-2">Instâncias</h2>
      <ul className="border rounded bg-white divide-y">
        {instances.map((inst) => (
          <li
            key={inst.id}
            className="flex justify-between items-center px-3 py-2"
          >
            <div>
              <div className="font-medium">{inst.name}</div>
              <div className="text-xs text-slate-500">
                {inst.region} · {inst.lifecycle_state}
              </div>
            </div>
            <button
              className="text-sm text-blue-600 hover:underline"
              onClick={() => onConfigure(inst)}
            >
              Configurar
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

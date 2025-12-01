import React from "react";
import type { Compartment } from "../../types";

interface Props {
  compartments: Compartment[];
  onEnter: (compartmentId: string) => void;
}

export function CompartmentList({ compartments, onEnter }: Props) {
  if (!compartments.length) {
    return <p className="text-sm text-slate-500">Nenhum sub-compartment.</p>;
  }

  return (
    <div className="mb-6">
      <h2 className="font-semibold mb-2">Sub-compartments</h2>
      <ul className="border rounded bg-white divide-y">
        {compartments.map((c) => (
          <li
            key={c.id}
            className="flex justify-between items-center px-3 py-2"
          >
            <span>{c.name}</span>
            <button
              className="text-sm text-blue-600 hover:underline"
              onClick={() => onEnter(c.id)}
            >
              Entrar
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

import React from "react";
import type { Compartment } from "../../types";

interface Props {
  breadcrumb: Compartment[];
  onSelect: (compartmentId?: string) => void;
}

export function CompartmentBreadcrumb({ breadcrumb, onSelect }: Props) {
  const handleRootClick = () => onSelect(undefined);

  return (
    <nav className="text-sm mb-4">
      <button
        className="text-blue-600 hover:underline"
        onClick={handleRootClick}
      >
        Raiz
      </button>

      {breadcrumb.map((comp, index) => (
        <span key={comp.id}>
          {" / "}
          <button
            className="text-blue-600 hover:underline"
            onClick={() => onSelect(comp.id)}
          >
            {comp.name}
          </button>
        </span>
      ))}
    </nav>
  );
}

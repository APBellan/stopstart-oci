import React, { PropsWithChildren } from "react";

export function PageLayout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-slate-900 text-white px-6 py-4">
        <h1 className="text-xl font-semibold">
          Stop/Start OCI - Gerenciador de Instâncias
        </h1>
      </header>

      <main className="px-6 py-4">{children}</main>
    </div>
  );
}

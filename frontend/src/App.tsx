import React, { useEffect, useState } from "react";
import { PageLayout } from "./components/Layout/PageLayout";
import { CompartmentBreadcrumb } from "./components/Navigation/CompartmentBreadcrumb";
import { CompartmentList } from "./components/Compartments/CompartmentList";
import { InstanceList } from "./components/Instances/InstanceList";
import { InstanceConfigModal } from "./components/Instances/InstanceConfigModal";
import { getNavigationLevel } from "./services/navigation";
import type {
  Compartment,
  Instance,
  NavigationLevel,
} from "./types";

function App() {
  const [currentCompartmentId, setCurrentCompartmentId] = useState<
    string | undefined
  >(undefined);
  const [data, setData] = useState<NavigationLevel | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedInstance, setSelectedInstance] = useState<Instance | null>(
    null
  );
  const [configOpen, setConfigOpen] = useState(false);

  const loadLevel = async (compartmentId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const level = await getNavigationLevel(compartmentId);
      setData(level);
    } catch (err: any) {
      console.error(err);
      setError(err.message ?? "Erro ao carregar navegação");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLevel(currentCompartmentId);
  }, [currentCompartmentId]);

  const handleBreadcrumbSelect = (compartmentId?: string) => {
    setCurrentCompartmentId(compartmentId);
  };

  const handleEnterCompartment = (compartmentId: string) => {
    setCurrentCompartmentId(compartmentId);
  };

  const handleConfigureInstance = (instance: Instance) => {
    setSelectedInstance(instance);
    setConfigOpen(true);
  };

  const handleCloseModal = () => {
    setConfigOpen(false);
    setSelectedInstance(null);
  };

  const breadcrumb: Compartment[] = data?.breadcrumb ?? [];
  const childCompartments: Compartment[] = data?.child_compartments ?? [];
  const instances: Instance[] = data?.instances ?? [];

  return (
    <PageLayout>
      <CompartmentBreadcrumb
        breadcrumb={breadcrumb}
        onSelect={handleBreadcrumbSelect}
      />

      {loading && <p>Carregando...</p>}
      {error && <p className="text-sm text-red-600 mb-2">{error}</p>}

      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <CompartmentList
            compartments={childCompartments}
            onEnter={handleEnterCompartment}
          />
          <InstanceList instances={instances} onConfigure={handleConfigureInstance} />
        </div>
      )}

      <InstanceConfigModal
        instance={selectedInstance}
        open={configOpen}
        onClose={handleCloseModal}
      />
    </PageLayout>
  );
}

export default App;

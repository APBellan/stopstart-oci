# StopStart OCI

Aplicação para gerenciar stop/start de instâncias no OCI, com:

- Mapeamento automático por compartments via SDK OCI
- Navegação hierárquica de compartments
- Configuração individual de instâncias via popup
- Scheduler para aplicar stop/start/reboot

## Desenvolvimento

### Requisitos

- Docker + Docker Compose
- Git
- VSCode (recomendado)

### Subir ambiente de desenvolvimento

```bash
cd deploy
docker compose -f docker-compose.dev.yml up --build

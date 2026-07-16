# Pilot Runbook

## Objetivo
Desplegar y monitorear 5-10 negocios piloto durante 2 semanas.

## Criterios de Selección de Negocios Piloto
- Negocio pequeño/mediano (1-3 empleados)
- Flujo de turnos simple
- Disponibilidad para dar feedback
- Representa variedad de industrias (peluquería, consultorio, taller)

## Pre-lanzamiento

### 1. Configuración
```bash
# Variables de producción
export DJANGO_SETTINGS_MODULE=config.settings.production
export DJANGO_SECRET_KEY=<generated-secret>
export ALLOWED_HOSTS=yourdomain.com
export POSTGRES_DB=appointments_prod
export POSTGRES_USER=appointments_prod
export POSTGRES_PASSWORD=<strong-password>
export REDIS_URL=redis://redis:6379/0
export WHATSAPP_ACCESS_TOKEN=<from-meta>
export WHATSAPP_VERIFY_TOKEN=<unique-token>
```

### 2. Migraciones
```bash
docker compose -f compose.yml -f compose.prod.yml exec web python manage.py migrate --noinput
```

### 3. Crear superuser admin
```bash
docker compose -f compose.yml -f compose.prod.yml exec web python manage.py createsuperuser
```

### 4. Verificación
```bash
# Health check
curl https://yourdomain.com/health/

# Logs sin errores
docker compose -f compose.yml -f compose.prod.yml logs web | grep -i error
```

## Monitoreo Durante Piloto

### Métricas Diarias
- [ ] Turnos creados por día
- [ ] Turnos cancelados
- [ ] Conversaciones de WhatsApp
- [ ] Tiempo medio de respuesta de webhook
- [ ] Errores 5xx

### Feedback Semanal
- [ ] Feedback de owners sobre UX
- [ ] Problemas reportados
- [ ] Bugs encontrados
- [ ] Features faltantes críticas

### Alertas
- [ ] Error rate > 1%
- [ ] Response time p95 > 2s
- [ ] Disco > 80%
- [ ] Memoria > 90%

## Rollback Procedure

Si hay problemas críticos:
```bash
# Identificar la versión anterior
git log --oneline -10

# Rollback código
git revert <commit-hash>

# Rebuild y restart
docker compose -f compose.yml -f compose.prod.yml build web
docker compose -f compose.yml -f compose.prod.yml up -d web
```

## Criterios de Éxito del Piloto

| Métrica | Target |
|---------|--------|
| Uptime | > 99% |
| Error rate | < 1% |
| NPS (feedback) | > 40 |
| Turnos por negocio/semana | > 10 |
| Conversión WhatsApp→Turno | > 60% |

## Contactos de Emergencia

| Rol | Contacto |
|-----|----------|
| Dev Lead | TBD |
| DevOps | TBD |
| Meta Business Support | business.facebook.com |

## Checklist de Cierre de Piloto

- [ ] Documentar todos los bugs encontrados
- [ ] Compilar feedback de owners
- [ ] Identificar features para siguiente sprint
- [ ] Validar que métricas cumplen objetivos
- [ ] Decidir expansión a más negocios o iterar producto

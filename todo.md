# DaleBot - WhatsApp Appointments SaaS

## Estado del Proyecto: En Desarrollo

---

## ✅ Completado

### Backend
- [x] Django monolith con 12 apps modulares
- [x] Multi-tenant architecture (Business → Users, Staff, Customers, etc.)
- [x] Modelos: Accounts, Businesses, Services, Staff, Availability, Appointments, Customers, Conversations, Notifications, Subscriptions, Billing, Audit, Analytics, WhatsApp
- [x] Authentication con Django Auth + custom User model
- [x] Celery tasks para reminders y notificaciones
- [x] WhatsApp webhook handler
- [x] API endpoints básicos

### Base de Datos
- [x] PostgreSQL con Docker
- [x] Redis para caching y Celery broker
- [x] Migraciones iniciales aplicadas

### Testing
- [x] 43 tests unitarios pasando
- [x] Tests: accounts, appointments, subscriptions, whatsapp, tasks
- [x] Coverage configurado

### CI/CD
- [x] GitHub Actions workflow (lint, typecheck, test)
- [x] Ruff linting passing (0 errors)
- [x] Docker Compose para desarrollo local

### Frontend HTMX
- [x] Base template con Tailwind CSS + HTMX
- [x] Login/Logout con Django auth
- [x] Dashboard con stats
- [x] Página de Turnos (Lista + Crear + Cancelar)
- [x] Página de Clientes (Lista + Crear)
- [x] Página de Servicios (Lista + Crear)
- [x] Mensajes de error amigables en español
- [x] Nav menu: Dashboard | Turnos | Clientes | Servicios | Admin

### Commits
```
- Initial commit: WhatsApp Appointments SaaS with 43 passing tests
- ci: improve GitHub Actions workflow for testing
- feat(frontend): add HTMX frontend with login and dashboard
- feat(frontend): add appointments CRUD pages with HTMX
- fix: all URL namespaces corrected, nav links working
- fix(frontend): improve appointment form error handling and modal
- fix(frontend): improve user-friendly error messages in Spanish
- feat(frontend): add Customers and Services pages with HTMX
```

---

## 🔄 Por Hacer

### Frontend
- [x] Página de Staff (listar, crear)
- [ ] Detalle de Turno (ver info completa)
- [ ] Confirmar turno (cambiar estado)
- [ ] Filtros funcionales en lista de turnos (pendientes, confirmados)
- [ ] Página de Configuración del negocio

### WhatsApp Integration
- [ ] Conectar con WhatsApp Business API real
- [ ] Configurar verify token y access token
- [ ] Probar webhook con número real

### Funcionalidades de Negocio
- [ ] Onboarding flow para nuevos negocios
- [ ] Gestión de planes y límites (Free, Basic, Pro)
- [ ] Notificaciones por WhatsApp reales
- [ ] Confirmación de turnos por mensaje

### Deployment
- [ ] Deploy a staging (Railway/Render/Fly.io)
- [ ] Configurar producción (nginx, gunicorn)
- [ ] Variables de entorno seguras
- [ ] SSL/HTTPS

### Testing
- [ ] Más tests de integración
- [ ] Tests del frontend
- [ ] Tests de WhatsApp handlers

### Documentación
- [ ] README actualizado
- [ ] Docs de setup para nuevos desarrolladores
- [ ] API documentation

---

## 📁 Estructura del Proyecto

```
dalebot/
├── apps/
│   ├── accounts/       # Users, auth, permissions
│   ├── businesses/     # Business model, onboarding
│   ├── services/       # Services offered
│   ├── staff/          # Staff members
│   ├── availability/   # Availability schedules
│   ├── appointments/   # Appointments CRUD
│   ├── customers/      # Customer management
│   ├── conversations/   # WhatsApp conversations
│   ├── notifications/   # Notifications system
│   ├── subscriptions/   # Plans and limits
│   ├── billing/        # Billing (placeholder)
│   ├── audit/          # Audit logs
│   ├── analytics/      # Metrics
│   ├── whatsapp/       # WhatsApp integration
│   └── frontend/       # HTMX views
├── config/            # Django settings
├── templates/         # HTML templates
├── docker-compose.yml  # Docker setup
└── pyproject.toml     # Dependencies
```

---

## 🔗 Links

- **Local:** http://localhost:8000
- **Admin:** http://localhost:8000/admin/
- **Dashboard:** http://localhost:8000/dashboard/
- **Turnos:** http://localhost:8000/appointments/
- **Clientes:** http://localhost:8000/customers/
- **Servicios:** http://localhost:8000/services/
- **Personal:** http://localhost:8000/staff/
- **Repo:** https://github.com/marcusjgb/dalebot

---

## 🏃 Próximo Paso Recomendado

Detalle de **Turno** o **Confirmar turno** para completar la gestión de turnos.

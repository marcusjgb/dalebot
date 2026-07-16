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
- [x] GitHub Actions workflow (lint, test)
- [x] Ruff linting passing (0 errors)
- [x] Docker Compose para desarrollo local

### Frontend HTMX
- [x] Base template con Tailwind CSS + HTMX
- [x] Login/Logout con Django auth
- [x] Dashboard con stats
- [x] Página de Turnos (Lista + Crear + Detalle + Editar + Confirmar + Cancelar + Filtros)
- [x] Página de Clientes (Lista + Crear)
- [x] Página de Servicios (Lista + Crear)
- [x] Página de Staff (Lista + Crear usuario + staff juntos)
- [x] Configuración del Negocio (nombre, teléfono, email, dirección, zona horaria)
- [x] Mensajes de error amigables en español
- [x] Nav menu responsive con hamburger en mobile
- [x] Tablas responsive con scroll horizontal en mobile
- [x] Filtros de turnos por estado (Todos, Pendientes, Confirmados, Completados, Cancelados)
- [x] Menú hamburguesa para mobile (overlay en vez de empujar contenido)

### WhatsApp Integration
- [x] Configuración de tokens en negocio (phone_number_id, verify_token, access_token)
- [x] Webhook receiver para recibir mensajes de Meta
- [x] Conversation flow completo para booking:
  - Saludo → Lista de servicios → Selección de staff → Fecha → Hora → Confirmación
  - Crea turno real en base de datos al confirmar
  - Manejo de errores (horario no disponible, sin staff, fecha inválida)
- [ ] Conectar con WhatsApp Business API real (pendiente: comprar chip)
- [ ] Registrar webhook en Meta Business Console

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
- feat(frontend): allow creating new users from Staff page
- feat(appointments): add appointment detail modal
- fix(appointments): modal close behavior on confirm/cancel
- fix(appointments): add csrf token to confirm button
- fix(appointments): correct htmx event syntax and swap strategy
- feat(appointments): add edit appointment functionality
- feat(appointments): add status filters to appointments list
- feat(business): add business settings page
- fix: hide Admin link for non-superuser business users
- feat: add mobile hamburger menu for navigation
- fix: make mobile menu overlay content instead of pushing down
- fix: make tables responsive on mobile with overflow-x-auto
- fix: make filter buttons scroll horizontally on mobile
- feat(whatsapp): add WhatsApp configuration to business settings
- feat(whatsapp): implement full booking conversation flow
```

---

## 🔄 Por Hacer

### Frontend
- [x] Detalle de Turno (ver info completa)
- [x] Confirmar turno (cambiar estado)
- [x] Editar Turno (modificar datos)
- [x] Filtros funcionales en lista de turnos (pendientes, confirmados)
- [x] Página de Configuración del negocio
- [ ] Dashboard con gráficos/stats más detallados
- [ ] Página de Conversations/Mensajes (ver historial WhatsApp)

### WhatsApp Integration
- [x] Configuración de tokens en negocio
- [x] Conversation flow completo para booking
- [ ] Probar webhook con número real (pendiente: comprar chip)
- [ ] Registrar webhook URL en Meta Business Console

### Funcionalidades de Negocio
- [ ] Onboarding flow para nuevos negocios
- [ ] Gestión de planes y límites (Free, Basic, Pro)
- [ ] Notificaciones por email reales
- [ ] Plantillas de mensajes de WhatsApp (templates aprobados por Meta)

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
- **Config:** http://localhost:8000/settings/
- **Repo:** https://github.com/marcusjgb/dalebot

---

## 🏃 Próximo Paso Recomendado

1. **Probar WhatsApp** - Una vez que tengas el chip y configures los tokens en Meta
2. **Dashboard stats** - Agregar gráficos de turnos por día/semana
3. **Ver historial de conversaciones** - Página para ver las conversaciones de WhatsApp

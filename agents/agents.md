# Agent Orchestration

Agents have strictly defined authority limited to their domain.

## Recommended Flow
Depending on risk level, not every agent participates. The standard path is:

1. **Product Manager** (Scope & MVP validation)
2. **Architect / Security** (If structural or high-risk changes are required)
3. **Implementation** (Backend Django / Frontend HTMX / WhatsApp Integration)
4. **Testing** (Automated Testing)
5. **QA** (Manual/Functional validation)
6. **Code Reviewer** (Final peer check)
7. **Documentation Maintainer** (Synchronize guides/ADRs)
8. **DevOps** (Deployment & Rollback setup)

*Rule of thumb:* Involve fewer agents for low-risk, trivial changes to maximize efficiency and reduce token overhead.
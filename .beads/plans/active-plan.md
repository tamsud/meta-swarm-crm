# Active Plan: Authentication Module
<!-- approved: 2026-06-17T14:00:00Z -->
<!-- gate-iterations: 2 -->
<!-- user-approved: true -->
<!-- status: in-progress -->

## Work Units

| WU | Description | Status |
|----|-------------|--------|
| WU-AUTH-1 | JWT Utility | pending |
| WU-AUTH-2 | Password Utility | completed (prior) |
| WU-AUTH-3 | Current-User Dependency | pending |
| WU-AUTH-4 | Auth Router (login + me) | pending |
| WU-AUTH-5 | Retrofit Permission Gates | pending |
| WU-AUTH-6 | Frontend AuthContext | pending |
| WU-AUTH-7 | Frontend Axios Interceptors | pending |
| WU-AUTH-8 | Login Page + Route Guards | pending |
| WU-AUTH-9 | Integration Tests | pending |

## Execution Order

1. WU-AUTH-1 (JWT utility - no deps)
2. WU-AUTH-3 (depends on AUTH-1, uses verify_credentials from Users)
3. WU-AUTH-4 (depends on AUTH-1,2,3)
4. WU-AUTH-5 (depends on AUTH-3 - retrofit existing routers)
5. WU-AUTH-6 (depends on AUTH-4 - frontend context)
6. WU-AUTH-7 (depends on AUTH-6 - axios interceptors)
7. WU-AUTH-8 (depends on AUTH-6,7 - login page + guards)
8. WU-AUTH-9 (depends on AUTH-4-8 - integration tests)

## Reference Docs

- specs/authentication/spec.md
- specs/authentication/plan.md
- specs/authentication/tasks.md
- specs/authentication/work-units.md

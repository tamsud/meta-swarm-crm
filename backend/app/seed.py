"""Basic seed script for development data.

Creates sample custom roles with varied permission sets.
Run with: python -m app.seed
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.permission import Permission
from app.models.role import Role


CUSTOM_ROLES = [
    {
        "name": "Sales Team Lead",
        "description": "Can manage team's leads and opportunities",
        "permission_codes": [
            "accounts:read",
            "accounts:update",
            "contacts:read",
            "contacts:update",
            "leads:manage-all",
            "opportunities:create",
            "opportunities:read",
            "opportunities:update",
            "activities:manage-all",
        ],
    },
    {
        "name": "Account Executive",
        "description": "Full access to accounts and contacts, own leads",
        "permission_codes": [
            "accounts:create",
            "accounts:read",
            "accounts:update",
            "contacts:create",
            "contacts:read",
            "contacts:update",
            "leads:manage-own",
            "opportunities:create",
            "opportunities:read",
            "opportunities:update",
            "activities:manage-own",
        ],
    },
    {
        "name": "Marketing Coordinator",
        "description": "Read-only access to pipeline data",
        "permission_codes": [
            "accounts:read",
            "contacts:read",
            "leads:manage-own",
            "opportunities:read",
            "activities:manage-own",
        ],
    },
    {
        "name": "Support Specialist",
        "description": "Contact and activity management only",
        "permission_codes": [
            "accounts:read",
            "contacts:read",
            "contacts:update",
            "activities:manage-own",
        ],
    },
]


async def get_permission_id_map(db: AsyncSession) -> dict[str, int]:
    """Get mapping of permission codes to IDs."""
    stmt = select(Permission)
    result = await db.execute(stmt)
    permissions = result.scalars().all()
    return {p.code: p.id for p in permissions}


async def seed_custom_roles(db: AsyncSession) -> tuple[int, int]:
    """Create custom roles if they don't exist.

    Returns:
        Tuple of (created_count, skipped_count)
    """
    perm_map = await get_permission_id_map(db)

    existing_stmt = select(Role.name)
    result = await db.execute(existing_stmt)
    existing_names = set(result.scalars().all())

    created = 0
    skipped = 0

    for role_data in CUSTOM_ROLES:
        if role_data["name"] in existing_names:
            skipped += 1
            continue

        permission_ids = [
            perm_map[code]
            for code in role_data["permission_codes"]
            if code in perm_map
        ]

        from app.models.role import RolePermission

        role = Role(
            name=role_data["name"],
            description=role_data["description"],
            is_system=False,
        )
        db.add(role)
        await db.flush()

        for perm_id in permission_ids:
            db.add(RolePermission(role_id=role.id, permission_id=perm_id))

        created += 1

    await db.commit()
    return created, skipped


async def main() -> None:
    """Run the seed script."""
    async with AsyncSessionLocal() as db:
        created, skipped = await seed_custom_roles(db)
        print(f"Created {created} roles, skipped {skipped} (already exist)")


if __name__ == "__main__":
    asyncio.run(main())

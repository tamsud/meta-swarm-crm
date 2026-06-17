"""Comprehensive seed script for development data.

Creates demo data for all CRM modules:
- Custom roles with varied permission sets
- Demo accounts (companies)
- Demo contacts (people at accounts)
- Demo opportunities (sales pipeline)
- Demo leads (all 4 statuses, 1 converted)
- Demo activities (all 3 types, single + dual-linked)
- Demo mock emails

Run with: python -m app.seed
"""

import asyncio
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import random

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.activity import Activity, ActivityType
from app.models.account import Account
from app.models.contact import Contact
from app.models.lead import Lead, LeadStatus
from app.models.mock_email import MockEmail
from app.models.opportunity import Opportunity, OpportunityStage
from app.models.permission import Permission
from app.models.role import Role, RolePermission


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


DEMO_ACCOUNTS = [
    {"name": "Acme Corporation", "industry": "Manufacturing", "website": "https://acme.example.com", "phone": "+1 (555) 100-1000", "address": "123 Industrial Way, Chicago, IL 60601"},
    {"name": "TechStart Inc", "industry": "Technology", "website": "https://techstart.io", "phone": "+1 (555) 200-2000", "address": "456 Innovation Blvd, San Francisco, CA 94105"},
    {"name": "Global Finance Partners", "industry": "Financial Services", "website": "https://globalfinance.com", "phone": "+1 (555) 300-3000", "address": "789 Wall Street, New York, NY 10005"},
    {"name": "HealthCare Solutions", "industry": "Healthcare", "website": "https://healthcaresol.com", "phone": "+1 (555) 400-4000", "address": "321 Medical Center Dr, Boston, MA 02115"},
    {"name": "EduLearn Systems", "industry": "Education", "website": "https://edulearn.edu", "phone": "+1 (555) 500-5000", "address": "654 Campus Way, Austin, TX 78701"},
    {"name": "GreenEnergy Corp", "industry": "Energy", "website": "https://greenenergy.com", "phone": "+1 (555) 600-6000", "address": "987 Solar Lane, Denver, CO 80202"},
    {"name": "RetailMax Group", "industry": "Retail", "website": "https://retailmax.com", "phone": "+1 (555) 700-7000", "address": "147 Shopping Center Rd, Miami, FL 33101"},
    {"name": "LogiTrans Shipping", "industry": "Logistics", "website": "https://logitrans.com", "phone": "+1 (555) 800-8000", "address": "258 Harbor Blvd, Seattle, WA 98101"},
    {"name": "MediaWave Studios", "industry": "Media", "website": "https://mediawave.tv", "phone": "+1 (555) 900-9000", "address": "369 Sunset Strip, Los Angeles, CA 90028"},
    {"name": "BioTech Innovations", "industry": "Biotechnology", "website": "https://biotechinno.com", "phone": "+1 (555) 111-1111", "address": "741 Research Park, San Diego, CA 92121"},
]


DEMO_CONTACTS = [
    {"first_name": "John", "last_name": "Smith", "email": "john.smith@acme.example.com", "job_title": "CEO", "phone": "+1 (555) 100-1001"},
    {"first_name": "Sarah", "last_name": "Johnson", "email": "sarah.johnson@acme.example.com", "job_title": "CTO", "phone": "+1 (555) 100-1002"},
    {"first_name": "Michael", "last_name": "Chen", "email": "m.chen@techstart.io", "job_title": "VP Engineering", "phone": "+1 (555) 200-2001"},
    {"first_name": "Emily", "last_name": "Davis", "email": "emily.davis@techstart.io", "job_title": "Product Manager", "phone": "+1 (555) 200-2002"},
    {"first_name": "Robert", "last_name": "Williams", "email": "r.williams@globalfinance.com", "job_title": "CFO", "phone": "+1 (555) 300-3001"},
    {"first_name": "Jennifer", "last_name": "Brown", "email": "j.brown@globalfinance.com", "job_title": "Director of Operations", "phone": "+1 (555) 300-3002"},
    {"first_name": "David", "last_name": "Miller", "email": "david.miller@healthcaresol.com", "job_title": "Chief Medical Officer", "phone": "+1 (555) 400-4001"},
    {"first_name": "Lisa", "last_name": "Anderson", "email": "l.anderson@healthcaresol.com", "job_title": "Head of Procurement", "phone": "+1 (555) 400-4002"},
    {"first_name": "James", "last_name": "Taylor", "email": "james.taylor@edulearn.edu", "job_title": "Dean of Technology", "phone": "+1 (555) 500-5001"},
    {"first_name": "Amanda", "last_name": "Martinez", "email": "a.martinez@edulearn.edu", "job_title": "Curriculum Director", "phone": "+1 (555) 500-5002"},
    {"first_name": "Christopher", "last_name": "Garcia", "email": "c.garcia@greenenergy.com", "job_title": "CEO", "phone": "+1 (555) 600-6001"},
    {"first_name": "Michelle", "last_name": "Robinson", "email": "m.robinson@greenenergy.com", "job_title": "Sustainability Director", "phone": "+1 (555) 600-6002"},
    {"first_name": "Daniel", "last_name": "Lee", "email": "d.lee@retailmax.com", "job_title": "VP Merchandising", "phone": "+1 (555) 700-7001"},
    {"first_name": "Jessica", "last_name": "White", "email": "j.white@retailmax.com", "job_title": "Store Operations Manager", "phone": "+1 (555) 700-7002"},
    {"first_name": "Matthew", "last_name": "Harris", "email": "m.harris@logitrans.com", "job_title": "Logistics Director", "phone": "+1 (555) 800-8001"},
    {"first_name": "Ashley", "last_name": "Clark", "email": "a.clark@logitrans.com", "job_title": "Fleet Manager", "phone": "+1 (555) 800-8002"},
    {"first_name": "Andrew", "last_name": "Lewis", "email": "a.lewis@mediawave.tv", "job_title": "Creative Director", "phone": "+1 (555) 900-9001"},
    {"first_name": "Stephanie", "last_name": "Walker", "email": "s.walker@mediawave.tv", "job_title": "Head of Production", "phone": "+1 (555) 900-9002"},
    {"first_name": "Joshua", "last_name": "Hall", "email": "j.hall@biotechinno.com", "job_title": "Chief Science Officer", "phone": "+1 (555) 111-1112"},
    {"first_name": "Nicole", "last_name": "Allen", "email": "n.allen@biotechinno.com", "job_title": "VP Research", "phone": "+1 (555) 111-1113"},
]


DEMO_OPPORTUNITIES = [
    {"title": "Enterprise Software License", "stage": OpportunityStage.negotiation, "value": Decimal("150000"), "probability": 75},
    {"title": "Cloud Migration Project", "stage": OpportunityStage.proposal, "value": Decimal("280000"), "probability": 60},
    {"title": "Annual Support Contract", "stage": OpportunityStage.closed_won, "value": Decimal("45000"), "probability": 100},
    {"title": "Hardware Refresh Program", "stage": OpportunityStage.prospecting, "value": Decimal("320000"), "probability": 30},
    {"title": "Digital Transformation Initiative", "stage": OpportunityStage.prospecting, "value": Decimal("500000"), "probability": 15},
    {"title": "Security Audit Services", "stage": OpportunityStage.proposal, "value": Decimal("75000"), "probability": 55},
    {"title": "Training & Certification Package", "stage": OpportunityStage.closed_won, "value": Decimal("28000"), "probability": 100},
    {"title": "Data Analytics Platform", "stage": OpportunityStage.negotiation, "value": Decimal("195000"), "probability": 70},
    {"title": "IoT Implementation", "stage": OpportunityStage.prospecting, "value": Decimal("420000"), "probability": 25},
    {"title": "CRM System Integration", "stage": OpportunityStage.closed_lost, "value": Decimal("85000"), "probability": 0},
    {"title": "Mobile App Development", "stage": OpportunityStage.proposal, "value": Decimal("120000"), "probability": 50},
    {"title": "Infrastructure Monitoring", "stage": OpportunityStage.prospecting, "value": Decimal("65000"), "probability": 20},
    {"title": "Compliance Consulting", "stage": OpportunityStage.negotiation, "value": Decimal("110000"), "probability": 80},
    {"title": "AI/ML Pilot Project", "stage": OpportunityStage.prospecting, "value": Decimal("250000"), "probability": 35},
    {"title": "Managed Services Contract", "stage": OpportunityStage.closed_won, "value": Decimal("180000"), "probability": 100},
]


DEMO_EMAILS = [
    {"to_email": "john.smith@acme.example.com", "subject": "Follow-up: Enterprise License Discussion", "body": "Hi John,\n\nThank you for taking the time to discuss the enterprise license options with us yesterday. I wanted to follow up on a few points we covered.\n\nAs discussed, we can offer a 15% discount on the 3-year commitment. I've attached the updated proposal for your review.\n\nPlease let me know if you have any questions or if you'd like to schedule another call to go over the details.\n\nBest regards,\nSales Team"},
    {"to_email": "m.chen@techstart.io", "subject": "Technical Requirements Document", "body": "Hi Michael,\n\nPlease find attached the technical requirements document for the cloud migration project. We've addressed all the security concerns raised in our last meeting.\n\nKey highlights:\n- End-to-end encryption\n- SOC 2 compliance\n- 99.9% SLA guarantee\n\nLooking forward to your feedback.\n\nBest,\nTechnical Team"},
    {"to_email": "r.williams@globalfinance.com", "subject": "Q4 Contract Renewal", "body": "Dear Robert,\n\nI hope this email finds you well. Your current contract is set to expire at the end of Q4, and I wanted to reach out early to discuss renewal options.\n\nWe have some exciting new features launching next quarter that I think would be valuable for Global Finance Partners.\n\nWould you be available for a call next week to discuss?\n\nBest regards,\nAccount Management"},
    {"to_email": "david.miller@healthcaresol.com", "subject": "HIPAA Compliance Certification", "body": "Dr. Miller,\n\nGreat news! We've completed our annual HIPAA compliance audit and received our updated certification. I've attached the documentation for your records.\n\nThis certification covers all the systems and processes related to our healthcare solutions.\n\nPlease let me know if you need any additional documentation.\n\nBest,\nCompliance Team"},
    {"to_email": "james.taylor@edulearn.edu", "subject": "New Learning Management Features", "body": "Hi James,\n\nI'm excited to share some new features we've added to the learning management system:\n\n1. AI-powered course recommendations\n2. Enhanced analytics dashboard\n3. Mobile app improvements\n4. Accessibility upgrades (WCAG 2.1 AA compliant)\n\nWould you like to schedule a demo to see these in action?\n\nBest,\nProduct Team"},
    {"to_email": "c.garcia@greenenergy.com", "subject": "Sustainability Report Integration", "body": "Hi Christopher,\n\nFollowing up on our discussion about integrating sustainability metrics into your reporting dashboard.\n\nWe can include:\n- Carbon footprint tracking\n- Energy consumption analytics\n- Renewable energy percentage\n- ESG scoring\n\nLet me know when you'd like to proceed with the integration.\n\nBest regards,\nSolutions Team"},
    {"to_email": "d.lee@retailmax.com", "subject": "Holiday Season Inventory Planning", "body": "Hi Daniel,\n\nWith the holiday season approaching, I wanted to check in about your inventory management needs.\n\nOur platform can help with:\n- Demand forecasting\n- Multi-location inventory sync\n- Automated reorder points\n- Real-time stock alerts\n\nLet's schedule a call to discuss your Q4 strategy.\n\nBest,\nRetail Solutions Team"},
    {"to_email": "m.harris@logitrans.com", "subject": "Fleet Tracking System Upgrade", "body": "Hi Matthew,\n\nWe have an exciting upgrade available for your fleet tracking system. The new version includes:\n\n- Real-time GPS with 10-second updates\n- Driver behavior scoring\n- Fuel efficiency analytics\n- Predictive maintenance alerts\n\nThe upgrade is included in your current contract. Would you like to schedule the migration?\n\nBest,\nLogistics Team"},
    {"to_email": "a.lewis@mediawave.tv", "subject": "Media Asset Management Proposal", "body": "Hi Andrew,\n\nThank you for the tour of MediaWave Studios last week. Based on our discussions, I've put together a proposal for the media asset management system.\n\nKey features:\n- 4K/8K video support\n- AI-powered tagging\n- Cloud-based collaboration\n- Archive and retrieval automation\n\nProposal attached. Looking forward to your feedback.\n\nBest,\nMedia Solutions"},
    {"to_email": "j.hall@biotechinno.com", "subject": "Research Data Platform Demo", "body": "Hi Joshua,\n\nI hope your research on the new compound is progressing well. I wanted to follow up on the research data platform demo we discussed.\n\nThe platform offers:\n- FAIR data principles compliance\n- Electronic lab notebook integration\n- Data versioning and audit trails\n- Collaboration tools for distributed teams\n\nWhen would be a good time for a demo with your research team?\n\nBest regards,\nLife Sciences Team"},
]


async def get_permission_id_map(db: AsyncSession) -> dict[str, int]:
    """Get mapping of permission codes to IDs."""
    stmt = select(Permission)
    result = await db.execute(stmt)
    permissions = result.scalars().all()
    return {p.code: p.id for p in permissions}


async def seed_custom_roles(db: AsyncSession) -> tuple[int, int]:
    """Create custom roles if they don't exist."""
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


async def seed_accounts(db: AsyncSession) -> tuple[int, int, list[Account]]:
    """Create demo accounts if they don't exist."""
    existing_stmt = select(Account.name)
    result = await db.execute(existing_stmt)
    existing_names = set(result.scalars().all())

    created = 0
    skipped = 0
    accounts = []

    for account_data in DEMO_ACCOUNTS:
        if account_data["name"] in existing_names:
            skipped += 1
            stmt = select(Account).where(Account.name == account_data["name"])
            result = await db.execute(stmt)
            accounts.append(result.scalar_one())
            continue

        account = Account(**account_data)
        db.add(account)
        await db.flush()
        accounts.append(account)
        created += 1

    await db.commit()
    return created, skipped, accounts


async def seed_contacts(db: AsyncSession, accounts: list[Account]) -> tuple[int, int, list[Contact]]:
    """Create demo contacts if they don't exist."""
    existing_stmt = select(Contact.email)
    result = await db.execute(existing_stmt)
    existing_emails = set(result.scalars().all())

    created = 0
    skipped = 0
    contacts = []

    for i, contact_data in enumerate(DEMO_CONTACTS):
        if contact_data["email"] in existing_emails:
            skipped += 1
            stmt = select(Contact).where(Contact.email == contact_data["email"])
            result = await db.execute(stmt)
            contacts.append(result.scalar_one())
            continue

        account_idx = i // 2
        account_id = accounts[account_idx].id if account_idx < len(accounts) else None

        contact = Contact(
            first_name=contact_data["first_name"],
            last_name=contact_data["last_name"],
            email=contact_data["email"],
            job_title=contact_data.get("job_title"),
            phone=contact_data.get("phone"),
            account_id=account_id,
        )
        db.add(contact)
        await db.flush()
        contacts.append(contact)
        created += 1

    await db.commit()
    return created, skipped, contacts


async def seed_opportunities(db: AsyncSession, accounts: list[Account], contacts: list[Contact]) -> tuple[int, int]:
    """Create demo opportunities if they don't exist."""
    existing_stmt = select(Opportunity.title)
    result = await db.execute(existing_stmt)
    existing_titles = set(result.scalars().all())

    created = 0
    skipped = 0
    today = date.today()

    for i, opp_data in enumerate(DEMO_OPPORTUNITIES):
        if opp_data["title"] in existing_titles:
            skipped += 1
            continue

        account_idx = i % len(accounts)
        contact_idx = i % len(contacts)

        days_offset = random.randint(7, 90)
        expected_close = today + timedelta(days=days_offset) if opp_data["stage"] not in [OpportunityStage.closed_won, OpportunityStage.closed_lost] else None

        opportunity = Opportunity(
            title=opp_data["title"],
            account_id=accounts[account_idx].id,
            contact_id=contacts[contact_idx].id if contacts else None,
            stage=opp_data["stage"],
            value=opp_data["value"],
            probability=opp_data["probability"],
            expected_close_date=expected_close,
        )
        db.add(opportunity)
        created += 1

    await db.commit()
    return created, skipped


async def seed_mock_emails(db: AsyncSession) -> tuple[int, int]:
    """Create demo mock emails if inbox is empty."""
    existing_stmt = select(MockEmail)
    result = await db.execute(existing_stmt)
    existing_count = len(result.scalars().all())

    if existing_count > 0:
        return 0, existing_count

    created = 0
    from_email = "sales@crm-demo.com"

    for i, email_data in enumerate(DEMO_EMAILS):
        status = "unread" if i < 5 else "read"

        email = MockEmail(
            to_email=email_data["to_email"],
            from_email=from_email,
            subject=email_data["subject"],
            body=email_data["body"],
            status=status,
        )
        db.add(email)
        created += 1

    await db.commit()
    return created, 0


DEMO_LEADS = [
    {"first_name": "Alice", "last_name": "Thompson", "email": "alice.thompson@startupxyz.com", "phone": "+1 (555) 010-0001", "company": "StartupXYZ", "status": LeadStatus.new, "source": "Website"},
    {"first_name": "Bob", "last_name": "Nakamura", "email": "bob.nakamura@techwave.io", "phone": "+1 (555) 010-0002", "company": "TechWave", "status": LeadStatus.contacted, "source": "LinkedIn"},
    {"first_name": "Carol", "last_name": "Singh", "email": "carol.singh@finpro.com", "phone": "+1 (555) 010-0003", "company": "FinPro", "status": LeadStatus.qualified, "source": "Referral"},
    {"first_name": "David", "last_name": "Park", "email": "david.park@meddevco.com", "phone": "+1 (555) 010-0004", "company": "MedDevCo", "status": LeadStatus.lost, "source": "Cold Call"},
    {"first_name": "Eva", "last_name": "Kowalski", "email": "eva.kowalski@ecomhub.net", "phone": "+1 (555) 010-0005", "company": "EcomHub", "status": LeadStatus.new, "source": "Trade Show"},
    {"first_name": "Frank", "last_name": "Osei", "email": "frank.osei@cloudpeak.co", "phone": "+1 (555) 010-0006", "company": "CloudPeak", "status": LeadStatus.contacted, "source": "Website"},
    {"first_name": "Grace", "last_name": "Fernandez", "email": "grace.fernandez@databridge.com", "phone": "+1 (555) 010-0007", "company": "DataBridge", "status": LeadStatus.qualified, "source": "LinkedIn"},
    {"first_name": "Henry", "last_name": "Johansson", "email": "henry.j@nordictech.se", "phone": "+1 (555) 010-0008", "company": "NordicTech", "status": LeadStatus.lost, "source": "Email Campaign"},
    {"first_name": "Iris", "last_name": "Patel", "email": "iris.patel@greenroofs.in", "phone": "+1 (555) 010-0009", "company": "GreenRoofs", "status": LeadStatus.new, "source": "Referral"},
    {"first_name": "Jack", "last_name": "Moreau", "email": "j.moreau@frenchlogistics.fr", "phone": "+1 (555) 010-0010", "company": "FrenchLogistics", "status": LeadStatus.contacted, "source": "Website"},
]


async def seed_leads(
    db: AsyncSession,
    admin_user_id: int,
) -> tuple[int, int, list[Lead]]:
    """Create demo leads if they don't exist. Returns created, skipped, list."""
    existing_stmt = select(Lead.email)
    result = await db.execute(existing_stmt)
    existing_emails = set(result.scalars().all())

    created = 0
    skipped = 0
    leads: list[Lead] = []

    for lead_data in DEMO_LEADS:
        if lead_data["email"] in existing_emails:
            skipped += 1
            stmt = select(Lead).where(Lead.email == lead_data["email"])
            result = await db.execute(stmt)
            leads.append(result.scalar_one())
            continue

        lead = Lead(
            first_name=lead_data["first_name"],
            last_name=lead_data["last_name"],
            email=lead_data["email"],
            phone=lead_data.get("phone"),
            company=lead_data.get("company"),
            status=lead_data["status"],
            source=lead_data.get("source"),
            created_by_user_id=admin_user_id,
        )
        db.add(lead)
        await db.flush()
        leads.append(lead)
        created += 1

    await db.commit()

    # Convert one qualified lead (Carol Singh / FinPro) to demonstrate atomic conversion
    qualified = next((l for l in leads if l.status == LeadStatus.qualified and l.converted_opportunity_id is None), None)
    if qualified is not None:
        try:
            from app.services.lead_service import convert_lead

            class _FakeUser:
                id = admin_user_id
                role = None

            await convert_lead(db, qualified.id, _FakeUser())  # type: ignore[arg-type]
        except Exception:
            pass  # Idempotent — already converted or FK issue

    return created, skipped, leads


async def seed_activities(
    db: AsyncSession,
    contacts: list[Contact],
    opportunities: list[Opportunity],
    admin_user_id: int,
) -> tuple[int, int]:
    """Create demo activities if none exist."""
    existing_count = (await db.execute(select(func.count(Activity.id)))).scalar_one()
    if existing_count >= 10:
        return 0, existing_count

    types = [ActivityType.call, ActivityType.email, ActivityType.meeting]
    subjects = [
        "Initial discovery call",
        "Follow-up on proposal",
        "Demo session",
        "Contract review meeting",
        "Technical requirements walkthrough",
        "Executive briefing",
        "Pricing discussion",
        "Implementation kickoff",
        "Quarterly business review",
        "Support escalation call",
    ]

    created = 0
    now = datetime.now(timezone.utc)

    for i in range(15):
        activity_type = types[i % 3]
        contact = contacts[i % len(contacts)] if contacts else None
        opp = opportunities[i % len(opportunities)] if opportunities else None

        # Mix: single-linked (contact only), single-linked (opp only), dual-linked
        if i % 3 == 0:
            contact_id = contact.id if contact else None
            opportunity_id = None
        elif i % 3 == 1:
            contact_id = None
            opportunity_id = opp.id if opp else None
        else:
            contact_id = contact.id if contact else None
            opportunity_id = opp.id if opp else None

        # Skip if would violate link constraint
        if contact_id is None and opportunity_id is None:
            if contact:
                contact_id = contact.id
            elif opp:
                opportunity_id = opp.id
            else:
                continue

        activity = Activity(
            type=activity_type,
            subject=subjects[i % len(subjects)],
            notes=f"Demo activity #{i + 1} — seeded for development.",
            activity_date=now - timedelta(days=i * 2),
            contact_id=contact_id,
            opportunity_id=opportunity_id,
            created_by_user_id=admin_user_id,
        )
        db.add(activity)
        created += 1

    await db.commit()
    return created, existing_count


async def seed_all(db: AsyncSession) -> dict[str, dict[str, int]]:
    """Run all seed functions. Idempotent — skips existing records."""
    from app.models.user import User as UserModel

    # Find admin user id
    admin_result = await db.execute(select(UserModel).where(UserModel.email == "admin@crm.dev"))
    admin_user = admin_result.scalar_one_or_none()
    admin_id = admin_user.id if admin_user else 1

    roles_c, roles_s = await seed_custom_roles(db)
    accts_c, accts_s, accounts = await seed_accounts(db)
    conts_c, conts_s, contacts = await seed_contacts(db, accounts)
    opps_c, opps_s = await seed_opportunities(db, accounts, contacts)

    # Reload opportunities list for activities
    opps_result = await db.execute(select(Opportunity))
    all_opps = list(opps_result.scalars().all())

    leads_c, leads_s, _ = await seed_leads(db, admin_id)
    acts_c, acts_s = await seed_activities(db, contacts, all_opps, admin_id)
    emails_c, emails_s = await seed_mock_emails(db)

    return {
        "roles": {"created": roles_c, "skipped": roles_s},
        "accounts": {"created": accts_c, "skipped": accts_s},
        "contacts": {"created": conts_c, "skipped": conts_s},
        "opportunities": {"created": opps_c, "skipped": opps_s},
        "leads": {"created": leads_c, "skipped": leads_s},
        "activities": {"created": acts_c, "skipped": acts_s},
        "mock_emails": {"created": emails_c, "skipped": emails_s},
    }


DEMO_USER_EMAILS = {"admin@crm.dev", "manager@crm.dev", "salesrep@crm.dev"}


async def clear_all(db: AsyncSession) -> dict[str, int]:
    """Delete all seeded CRM data in FK-safe order. Preserves permissions, roles, demo users."""
    results: dict[str, int] = {}

    async with db.begin():
        # 1. activities (references contacts + opportunities via RESTRICT)
        r = await db.execute(text("DELETE FROM activities"))
        results["activities"] = r.rowcount  # type: ignore[union-attr]

        # 2. leads (references opportunities via SET NULL — safe to delete now)
        r = await db.execute(text("DELETE FROM leads"))
        results["leads"] = r.rowcount  # type: ignore[union-attr]

        # 3. mock_emails (independent)
        r = await db.execute(text("DELETE FROM mock_emails"))
        results["mock_emails"] = r.rowcount  # type: ignore[union-attr]

        # 4. opportunities (references accounts via RESTRICT — must go before accounts)
        r = await db.execute(text("DELETE FROM opportunities"))
        results["opportunities"] = r.rowcount  # type: ignore[union-attr]

        # 5. contacts (references accounts via SET NULL)
        r = await db.execute(text("DELETE FROM contacts"))
        results["contacts"] = r.rowcount  # type: ignore[union-attr]

        # 6. accounts
        r = await db.execute(text("DELETE FROM accounts"))
        results["accounts"] = r.rowcount  # type: ignore[union-attr]

        # 7. non-demo users (keep admin@crm.dev, manager@crm.dev, salesrep@crm.dev)
        placeholders = ", ".join(f"'{e}'" for e in DEMO_USER_EMAILS)
        r = await db.execute(text(f"DELETE FROM users WHERE email NOT IN ({placeholders})"))
        results["users"] = r.rowcount  # type: ignore[union-attr]

    return results


async def main() -> None:
    """Run the seed script."""
    print("Starting CRM seed...")
    print("-" * 40)

    async with AsyncSessionLocal() as db:
        summary = await seed_all(db)
        for entity, counts in summary.items():
            print(f"{entity:<16} {counts['created']} created, {counts['skipped']} skipped")

    print("-" * 40)
    print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(main())

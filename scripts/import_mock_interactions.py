from __future__ import annotations

import argparse
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.config import LOCAL_CAMPAIGN_DATASET_XLSX, LOCAL_CAMPAIGN_IMAGE_DIR, SINGAPORE_TZ  # noqa: E402
from core.db import engine, get_session  # noqa: E402
from models import Base  # noqa: E402
from models.campaign import CampaignImage, CampaignViewRecord, FundraisingCampaign  # noqa: E402
from models.donation import DonationRecord, FavouriteCampaign  # noqa: E402
from models.user import UserAccount  # noqa: E402
from scripts.import_mock_campaigns import (  # noqa: E402
    MOCK_USER_EMAIL_TEMPLATE,
    MockCampaignRow,
    discover_campaign_images,
    excel_serial_to_date,
    get_or_create_mock_user,
    normalise_category,
    read_mock_campaigns,
    read_xlsx_rows,
    upsert_campaign,
)

DEFAULT_DONATION_XLSX = ROOT_DIR / "docs" / "Mock_Donation_Data_Full_Coverage.xlsx"
MOCK_DONOR_EMAIL_TEMPLATE = "mock-donor-{slug}@fireflyfund.local"
MOCK_VIEWER_EMAIL_TEMPLATE = "mock-viewer-{slug}@fireflyfund.local"
MOCK_FAVOURITE_EMAIL_TEMPLATE = "mock-favourite-{slug}@fireflyfund.local"
MOCK_PASSWORD_PREFIX = "MockInteraction"
INTERACTION_END_AT = datetime(2026, 5, 2, 23, 59, tzinfo=SINGAPORE_TZ)
RANDOM_SEED = 3142026


@dataclass(frozen=True)
class MockDonationRow:
    donation_id: str
    donor_name: str
    source_no: int
    campaign_title: str
    category: str
    campaign_goal: int
    amount: int
    donated_at: datetime


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or uuid4().hex[:10]


def parse_datetime(value: str) -> datetime:
    clean_value = value.strip()
    if not clean_value:
        raise RuntimeError("Donation time cannot be empty.")
    if re.fullmatch(r"\d+(?:\.\d+)?", clean_value):
        return excel_serial_to_date(clean_value)

    for date_format in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(clean_value, date_format)
            return parsed.replace(tzinfo=SINGAPORE_TZ)
        except ValueError:
            continue

    parsed = datetime.fromisoformat(clean_value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=SINGAPORE_TZ)
    return parsed.astimezone(SINGAPORE_TZ)


def read_mock_donations(xlsx_path: Path) -> list[MockDonationRow]:
    rows = read_xlsx_rows(xlsx_path)
    if not rows:
        raise RuntimeError("The donation workbook is empty.")

    headers = rows[0]
    required_headers = [
        "Donation ID",
        "Donor Name",
        "Campaign No.",
        "Campaign Title",
        "Category",
        "Campaign Goal",
        "Donation Amount",
        "Donation Time",
    ]
    missing_headers = [header for header in required_headers if header not in headers]
    if missing_headers:
        raise RuntimeError(f"Missing required donation columns: {', '.join(missing_headers)}")

    donations: list[MockDonationRow] = []
    for row in rows[1:]:
        if not any(value.strip() for value in row):
            continue
        row_data = {
            header: row[index].strip() if index < len(row) else ""
            for index, header in enumerate(headers)
        }
        donations.append(
            MockDonationRow(
                donation_id=row_data["Donation ID"],
                donor_name=row_data["Donor Name"],
                source_no=int(float(row_data["Campaign No."])),
                campaign_title=row_data["Campaign Title"],
                category=normalise_category(row_data["Category"]),
                campaign_goal=int(float(row_data["Campaign Goal"])),
                amount=int(float(row_data["Donation Amount"])),
                donated_at=parse_datetime(row_data["Donation Time"]),
            )
        )
    return donations


def get_or_create_interaction_user(
    session: Session,
    username: str,
    email_template: str,
    slug: str | None = None,
) -> UserAccount:
    clean_username = username.strip()
    clean_slug = slug or slugify(clean_username)
    email = email_template.format(slug=clean_slug)
    user = UserAccount.GetUserByEmail(session, email)
    if user:
        if user.username != clean_username:
            user.username = clean_username
            session.add(user)
        return user

    user = UserAccount.CreateUser(
        clean_username,
        email,
        f"{MOCK_PASSWORD_PREFIX}-{uuid4().hex[:12]}",
    )
    UserAccount.SaveUser(session, user)
    session.flush()
    return user


def get_existing_mock_interaction_user_ids(session: Session) -> list[int]:
    statement = select(UserAccount.id).where(
        or_(
            UserAccount.email.like("mock-donor-%@fireflyfund.local"),
            UserAccount.email.like("mock-viewer-%@fireflyfund.local"),
            UserAccount.email.like("mock-favourite-%@fireflyfund.local"),
        )
    )
    return list(session.scalars(statement))


def prepare_mock_campaigns(
    session: Session, campaign_rows: list[MockCampaignRow]
) -> dict[int, FundraisingCampaign]:
    campaigns_by_source_no: dict[int, FundraisingCampaign] = {}
    for campaign_row in campaign_rows:
        owner = get_or_create_mock_user(session, campaign_row.writer)
        campaign = upsert_campaign(session, campaign_row, owner)
        campaign.amount_raised = 0
        campaign.view_count = 0
        session.add(campaign)
        campaigns_by_source_no[campaign_row.source_no] = campaign
    session.flush()
    return campaigns_by_source_no


def clear_existing_mock_interactions(
    session: Session,
    campaign_ids: list[int],
    mock_user_ids: list[int],
) -> None:
    if not campaign_ids:
        return

    if mock_user_ids:
        session.execute(
            delete(DonationRecord).where(
                DonationRecord.campaign_id.in_(campaign_ids),
                DonationRecord.user_id.in_(mock_user_ids),
            )
        )
        session.execute(
            delete(FavouriteCampaign).where(
                FavouriteCampaign.campaign_id.in_(campaign_ids),
                FavouriteCampaign.user_id.in_(mock_user_ids),
            )
        )
        session.execute(
            delete(CampaignViewRecord).where(
                CampaignViewRecord.campaign_id.in_(campaign_ids),
                CampaignViewRecord.viewer_user_id.in_(mock_user_ids),
            )
        )

    for campaign in session.scalars(
        select(FundraisingCampaign).where(FundraisingCampaign.id.in_(campaign_ids))
    ):
        campaign.amount_raised = 0
        campaign.view_count = 0
        session.add(campaign)
    session.flush()


def refresh_local_campaign_images(
    session: Session,
    campaigns_by_source_no: dict[int, FundraisingCampaign],
    image_root: Path,
) -> int:
    images_by_number = discover_campaign_images(image_root)
    imported_image_count = 0

    for source_no, campaign in campaigns_by_source_no.items():
        image_paths = images_by_number.get(source_no, [])
        if not image_paths:
            continue

        CampaignImage.DeleteImageRecords(session, campaign.id)
        CampaignImage.SaveImageRecords(
            session,
            CampaignImage.StoreImages(
                campaign.id,
                [f"asset:{image_path.name}" for image_path in image_paths],
            ),
        )
        imported_image_count += len(image_paths)

    session.flush()
    return imported_image_count


def random_datetime_between(
    rng: random.Random,
    start_at: datetime,
    end_at: datetime = INTERACTION_END_AT,
) -> datetime:
    if start_at.tzinfo is None:
        start_at = start_at.replace(tzinfo=SINGAPORE_TZ)
    start_at = max(start_at.astimezone(SINGAPORE_TZ), datetime(2026, 1, 1, tzinfo=SINGAPORE_TZ))
    end_at = max(end_at, start_at)
    start_seconds = int(start_at.timestamp())
    end_seconds = int(end_at.timestamp())
    return datetime.fromtimestamp(rng.randint(start_seconds, end_seconds), tz=SINGAPORE_TZ)


def create_interaction_user_pool(
    session: Session,
    prefix: str,
    email_template: str,
    size: int,
) -> list[UserAccount]:
    users: list[UserAccount] = []
    for index in range(1, size + 1):
        users.append(
            get_or_create_interaction_user(
                session,
                f"Mock {prefix.title()} {index:03d}",
                email_template,
                slug=f"{index:03d}",
            )
        )
    return users


def import_donation_records(
    session: Session,
    donations: list[MockDonationRow],
    campaigns_by_source_no: dict[int, FundraisingCampaign],
) -> tuple[int, Counter[int], dict[int, int]]:
    donation_counts: Counter[int] = Counter()
    raised_amounts: dict[int, int] = defaultdict(int)

    for donation in donations:
        campaign = campaigns_by_source_no.get(donation.source_no)
        if campaign is None:
            raise RuntimeError(f"Donation references unknown campaign no. {donation.source_no}.")

        donor = get_or_create_interaction_user(
            session,
            donation.donor_name,
            MOCK_DONOR_EMAIL_TEMPLATE,
        )
        session.add(
            DonationRecord(
                user_id=donor.id,
                campaign_id=campaign.id,
                amount=donation.amount,
                campaign_category=campaign.category,
                donated_at=donation.donated_at,
            )
        )
        donation_counts[donation.source_no] += 1
        raised_amounts[donation.source_no] += donation.amount

    for source_no, amount_raised in raised_amounts.items():
        campaign = campaigns_by_source_no[source_no]
        campaign.amount_raised = int(amount_raised)
        session.add(campaign)

    return len(donations), donation_counts, dict(raised_amounts)


def simulate_view_and_favourite_records(
    session: Session,
    campaigns_by_source_no: dict[int, FundraisingCampaign],
    donation_counts: Counter[int],
) -> tuple[int, int]:
    rng = random.Random(RANDOM_SEED)
    viewer_users = create_interaction_user_pool(
        session,
        "viewer",
        MOCK_VIEWER_EMAIL_TEMPLATE,
        240,
    )
    favourite_users = create_interaction_user_pool(
        session,
        "favourite",
        MOCK_FAVOURITE_EMAIL_TEMPLATE,
        160,
    )

    total_views = 0
    total_favourites = 0
    for source_no, campaign in sorted(campaigns_by_source_no.items()):
        campaign_rng = random.Random(RANDOM_SEED + source_no)
        donation_count = donation_counts.get(source_no, 0)
        favourite_count = min(
            len(favourite_users),
            max(5, min(48, int(donation_count * 0.45) + campaign_rng.randint(6, 16))),
        )
        view_count = max(
            25,
            min(420, donation_count * 4 + favourite_count * 3 + campaign_rng.randint(20, 110)),
        )

        selected_favourite_users = campaign_rng.sample(favourite_users, favourite_count)
        for favourite_user in selected_favourite_users:
            session.add(
                FavouriteCampaign(
                    user_id=favourite_user.id,
                    campaign_id=campaign.id,
                    created_at=random_datetime_between(
                        campaign_rng,
                        campaign.published_at or campaign.created_at,
                    ),
                )
            )

        for _ in range(view_count):
            viewer = rng.choice(viewer_users)
            session.add(
                CampaignViewRecord(
                    campaign_id=campaign.id,
                    viewer_user_id=viewer.id,
                    viewed_at=random_datetime_between(
                        rng,
                        campaign.published_at or campaign.created_at,
                    ),
                )
            )

        campaign.view_count = view_count
        session.add(campaign)
        total_views += view_count
        total_favourites += favourite_count

    return total_views, total_favourites


def import_mock_interactions(
    donations_xlsx: Path,
    campaign_xlsx: Path,
    image_root: Path,
    dry_run: bool = False,
) -> None:
    donations = read_mock_donations(donations_xlsx)
    campaign_rows = read_mock_campaigns(campaign_xlsx)
    campaign_numbers = {campaign.source_no for campaign in campaign_rows}
    missing_campaigns = sorted(
        {donation.source_no for donation in donations} - campaign_numbers
    )
    if missing_campaigns:
        raise RuntimeError(
            "Donation workbook references campaign numbers not found in the local dataset: "
            + ", ".join(str(number) for number in missing_campaigns)
        )

    print(f"Prepared {len(donations)} donation records for {len(campaign_rows)} campaigns.")
    if dry_run:
        unique_donors = len({donation.donor_name for donation in donations})
        covered_campaigns = len({donation.source_no for donation in donations})
        print(f"Unique donors: {unique_donors}")
        print(f"Campaigns covered by donations: {covered_campaigns}")
        print("Dry run complete. No database data was changed.")
        return

    Base.metadata.create_all(bind=engine)
    session = get_session()
    try:
        campaigns_by_source_no = prepare_mock_campaigns(session, campaign_rows)
        image_total = refresh_local_campaign_images(
            session,
            campaigns_by_source_no,
            image_root,
        )
        campaign_ids = [campaign.id for campaign in campaigns_by_source_no.values()]
        clear_existing_mock_interactions(
            session,
            campaign_ids,
            get_existing_mock_interaction_user_ids(session),
        )
        donation_total, donation_counts, raised_amounts = import_donation_records(
            session,
            donations,
            campaigns_by_source_no,
        )
        view_total, favourite_total = simulate_view_and_favourite_records(
            session,
            campaigns_by_source_no,
            donation_counts,
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(f"Imported {donation_total} donation records.")
    print(f"Imported {image_total} local campaign image records.")
    print(f"Generated {view_total} campaign view records.")
    print(f"Generated {favourite_total} favourite campaign records.")
    print(f"Updated raised totals for {len(raised_amounts)} campaigns.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import mock donation, view, and favourite records for local campaigns."
    )
    parser.add_argument(
        "--donations-xlsx",
        type=Path,
        default=DEFAULT_DONATION_XLSX,
        help="Path to the mock donation workbook.",
    )
    parser.add_argument(
        "--campaign-xlsx",
        type=Path,
        default=LOCAL_CAMPAIGN_DATASET_XLSX,
        help="Path to the local campaign workbook.",
    )
    parser.add_argument(
        "--image-root",
        type=Path,
        default=LOCAL_CAMPAIGN_IMAGE_DIR,
        help="Folder containing numbered local campaign images.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate records without changing database data.",
    )
    args = parser.parse_args()
    import_mock_interactions(
        args.donations_xlsx.expanduser(),
        args.campaign_xlsx.expanduser(),
        args.image_root.expanduser(),
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()

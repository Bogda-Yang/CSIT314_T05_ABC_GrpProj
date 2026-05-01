from __future__ import annotations

import argparse
import mimetypes
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from pathlib import Path
from uuid import uuid4
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from sqlalchemy import select
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.config import (  # noqa: E402
    CAMPAIGN_CATEGORY_OPTIONS,
    SINGAPORE_TZ,
    SUPABASE_CAMPAIGN_BUCKET,
)
from core.db import get_session  # noqa: E402
from core.security import now_dt  # noqa: E402
from core.storage import SupabaseStorage  # noqa: E402
from models.campaign import CampaignImage, FundraisingCampaign  # noqa: E402
from models.user import UserAccount  # noqa: E402

XLSX_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SUPABASE_IMAGE_BYTES = 5 * 1024 * 1024
MOCK_USER_EMAIL_TEMPLATE = "mock-{writer}@fireflyfund.local"
MOCK_USER_PASSWORD_PREFIX = "MockUser"


@dataclass(frozen=True)
class MockCampaignRow:
    writer: str
    source_no: int
    title: str
    category: str
    goal_amount: int
    published_at: datetime
    deadline: str
    description: str


def column_index(cell_reference: str) -> int:
    letters = "".join(character for character in cell_reference if character.isalpha())
    index = 0
    for letter in letters:
        index = index * 26 + ord(letter.upper()) - 64
    return index - 1


def read_shared_strings(zip_file: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zip_file.namelist():
        return []
    root = ET.fromstring(zip_file.read("xl/sharedStrings.xml"))
    return [
        "".join(
            text_node.text or ""
            for text_node in item.iter(
                "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
            )
        )
        for item in root.findall("m:si", XLSX_NS)
    ]


def read_xlsx_rows(xlsx_path: Path) -> list[list[str]]:
    with ZipFile(xlsx_path) as zip_file:
        shared_strings = read_shared_strings(zip_file)
        sheet = ET.fromstring(zip_file.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for row_node in sheet.findall(".//m:sheetData/m:row", XLSX_NS):
            row_values: list[str] = []
            for cell in row_node.findall("m:c", XLSX_NS):
                cell_ref = cell.attrib.get("r", "A1")
                index = column_index(cell_ref)
                while len(row_values) <= index:
                    row_values.append("")

                value_node = cell.find("m:v", XLSX_NS)
                value = "" if value_node is None else value_node.text or ""
                cell_type = cell.attrib.get("t")
                if cell_type == "s" and value:
                    value = shared_strings[int(value)]
                elif cell_type == "inlineStr":
                    value = "".join(
                        text_node.text or ""
                        for text_node in cell.iter(
                            "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
                        )
                    )
                row_values[index] = str(value).strip()
            rows.append(row_values)
        return rows


def excel_serial_to_date(value: str) -> datetime:
    try:
        serial_number = float(value)
    except ValueError:
        parsed_date = datetime.fromisoformat(value)
        return parsed_date.replace(tzinfo=SINGAPORE_TZ)
    parsed_date = datetime(1899, 12, 30) + timedelta(days=serial_number)
    return datetime.combine(parsed_date.date(), time.min, tzinfo=SINGAPORE_TZ)


def normalise_category(category: str) -> str:
    category_lookup = {
        label.lower(): value for value, label in CAMPAIGN_CATEGORY_OPTIONS
    }
    category_lookup.update({value.lower(): value for value, _ in CAMPAIGN_CATEGORY_OPTIONS})
    clean_category = category.strip().lower().replace("-", " ").replace("_", " ")
    clean_category = re.sub(r"\s+", " ", clean_category)
    if clean_category in category_lookup:
        return category_lookup[clean_category]
    underscored_category = clean_category.replace(" ", "_")
    if underscored_category in category_lookup:
        return category_lookup[underscored_category]
    return "other"


def read_mock_campaigns(xlsx_path: Path) -> list[MockCampaignRow]:
    rows = read_xlsx_rows(xlsx_path)
    if not rows:
        raise RuntimeError("The workbook is empty.")

    headers = rows[0]
    required_headers = [
        "Writer",
        "No.",
        "Title",
        "Category",
        "Goal",
        "Start Time",
        "Deadline",
        "Description",
    ]
    missing_headers = [header for header in required_headers if header not in headers]
    if missing_headers:
        raise RuntimeError(f"Missing required columns: {', '.join(missing_headers)}")

    campaigns: list[MockCampaignRow] = []
    for row in rows[1:]:
        if not any(value.strip() for value in row):
            continue
        row_data = {
            header: row[index].strip() if index < len(row) else ""
            for index, header in enumerate(headers)
        }
        source_no = int(float(row_data["No."]))
        published_at = excel_serial_to_date(row_data["Start Time"])
        deadline = excel_serial_to_date(row_data["Deadline"]).date().isoformat()
        campaigns.append(
            MockCampaignRow(
                writer=row_data["Writer"].strip(),
                source_no=source_no,
                title=row_data["Title"].strip(),
                category=normalise_category(row_data["Category"]),
                goal_amount=int(float(row_data["Goal"])),
                published_at=published_at,
                deadline=deadline,
                description=row_data["Description"].strip(),
            )
        )
    return campaigns


def discover_campaign_images(image_root: Path) -> dict[int, list[Path]]:
    image_pattern = re.compile(r"^(\d+)(?:[.-](\d+))?$")
    images_by_number: dict[int, list[tuple[int, Path]]] = {}
    for image_path in image_root.rglob("*"):
        if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        match = image_pattern.match(image_path.stem)
        if not match:
            continue
        source_no = int(match.group(1))
        image_order = int(match.group(2) or 1)
        images_by_number.setdefault(source_no, []).append((image_order, image_path))

    return {
        source_no: [path for _, path in sorted(image_paths, key=lambda item: (item[0], item[1].name))]
        for source_no, image_paths in images_by_number.items()
    }


def content_type_for(image_path: Path) -> str:
    guessed_type, _ = mimetypes.guess_type(image_path.name)
    if guessed_type in {"image/jpeg", "image/png", "image/webp"}:
        return guessed_type
    if image_path.suffix.lower() == ".jpg":
        return "image/jpeg"
    raise RuntimeError(f"Unsupported image type: {image_path}")


def prepare_image_upload(image_path: Path) -> tuple[bytes, str, str]:
    original_bytes = image_path.read_bytes()
    if len(original_bytes) <= MAX_SUPABASE_IMAGE_BYTES:
        return original_bytes, image_path.suffix.lower(), content_type_for(image_path)

    with tempfile.TemporaryDirectory(prefix="firefly-mock-image-") as temp_dir:
        output_path = Path(temp_dir) / f"{image_path.stem}.jpg"
        for quality in (85, 75, 65, 55, 45):
            subprocess.run(
                [
                    "sips",
                    "-s",
                    "format",
                    "jpeg",
                    "-s",
                    "formatOptions",
                    str(quality),
                    str(image_path),
                    "--out",
                    str(output_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            compressed_bytes = output_path.read_bytes()
            if len(compressed_bytes) <= MAX_SUPABASE_IMAGE_BYTES:
                return compressed_bytes, ".jpg", "image/jpeg"

    raise RuntimeError(
        f"Image remains larger than 5MB after compression: {image_path}"
    )


def get_or_create_mock_user(session: Session, writer: str) -> UserAccount:
    clean_writer = writer.strip()
    if not clean_writer:
        raise RuntimeError("Writer cannot be empty.")
    email = MOCK_USER_EMAIL_TEMPLATE.format(writer=clean_writer.lower())
    user = UserAccount.GetUserByEmail(session, email)
    if user:
        if user.username != clean_writer:
            user.username = clean_writer
            session.add(user)
        return user

    user = UserAccount.CreateUser(
        clean_writer,
        email,
        f"{MOCK_USER_PASSWORD_PREFIX}-{uuid4().hex[:12]}",
    )
    UserAccount.SaveUser(session, user)
    session.flush()
    return user


def get_existing_campaign(
    session: Session, owner_id: int, title: str
) -> FundraisingCampaign | None:
    return session.scalar(
        select(FundraisingCampaign).where(
            FundraisingCampaign.owner_id == owner_id,
            FundraisingCampaign.title == title,
        )
    )


def upsert_campaign(
    session: Session,
    row: MockCampaignRow,
    owner: UserAccount,
) -> FundraisingCampaign:
    campaign = get_existing_campaign(session, owner.id, row.title)
    if campaign is None:
        campaign = FundraisingCampaign.CreateCampaign(owner.id, row.title, row.category)
        campaign.amount_raised = 0
        campaign.view_count = 0
        FundraisingCampaign.SaveCampaignDraft(session, campaign)
        session.flush()

    campaign.title = row.title
    campaign.category = row.category
    campaign.goal_amount = row.goal_amount
    campaign.description = row.description
    campaign.deadline = row.deadline
    campaign.workflow_stage = 5
    campaign.status = "published"
    campaign.created_at = row.published_at
    campaign.submitted_at = row.published_at
    campaign.reviewed_at = row.published_at
    campaign.published_at = row.published_at
    campaign.updated_at = now_dt()
    session.add(campaign)
    session.flush()
    return campaign


def upload_images_for_campaign(
    session: Session,
    campaign: FundraisingCampaign,
    source_no: int,
    image_paths: list[Path],
) -> int:
    existing_paths = {
        image_record.image_path
        for image_record in CampaignImage.GetImageDetails(session, campaign.id)
    }
    uploaded_count = 0

    for index, image_path in enumerate(image_paths, start=1):
        file_bytes, storage_suffix, content_type = prepare_image_upload(image_path)
        storage_path = (
            f"mock-campaigns/{source_no:03d}/"
            f"{index:02d}-{image_path.stem.lower().replace('.', '-')}{storage_suffix}"
        )
        SupabaseStorage.UploadPublicObject(
            SUPABASE_CAMPAIGN_BUCKET,
            storage_path,
            file_bytes,
            content_type,
        )
        if storage_path not in existing_paths:
            CampaignImage.SaveImageRecords(
                session,
                CampaignImage.StoreImages(campaign.id, [storage_path]),
            )
        uploaded_count += 1

    return uploaded_count


def validate_input(campaigns: list[MockCampaignRow], images_by_number: dict[int, list[Path]]) -> None:
    campaign_numbers = {campaign.source_no for campaign in campaigns}
    missing_images = sorted(number for number in campaign_numbers if number not in images_by_number)
    if missing_images:
        raise RuntimeError(
            "Missing image files for campaign numbers: "
            + ", ".join(str(number) for number in missing_images)
        )


def import_mock_campaigns(
    xlsx_path: Path,
    image_root: Path,
    dry_run: bool,
) -> None:
    campaigns = read_mock_campaigns(xlsx_path)
    images_by_number = discover_campaign_images(image_root)
    validate_input(campaigns, images_by_number)

    total_images = sum(len(images_by_number[campaign.source_no]) for campaign in campaigns)
    print(f"Prepared {len(campaigns)} campaigns and {total_images} campaign images.")

    if dry_run:
        writers = sorted({campaign.writer for campaign in campaigns})
        categories = sorted({campaign.category for campaign in campaigns})
        print(f"Writers: {', '.join(writers)}")
        print(f"Categories: {', '.join(categories)}")
        print("Dry run complete. No Supabase data was changed.")
        return

    if not SupabaseStorage.IsConfigured():
        raise RuntimeError(
            "Supabase Storage is not configured. Add SUPABASE_SERVICE_ROLE_KEY to .env "
            "before importing campaign images."
        )

    SupabaseStorage.EnsurePublicBucket(SUPABASE_CAMPAIGN_BUCKET)
    session = get_session()
    try:
        imported_campaigns = 0
        imported_images = 0
        for campaign_row in campaigns:
            owner = get_or_create_mock_user(session, campaign_row.writer)
            campaign = upsert_campaign(session, campaign_row, owner)
            imported_images += upload_images_for_campaign(
                session,
                campaign,
                campaign_row.source_no,
                images_by_number[campaign_row.source_no],
            )
            imported_campaigns += 1
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(f"Imported {imported_campaigns} campaigns.")
    print(f"Uploaded or refreshed {imported_images} images.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import mock campaign data into Supabase.")
    parser.add_argument(
        "--xlsx",
        type=Path,
        default=Path("/Users/apple/Desktop/模拟数据/Mock up data.xlsx"),
        help="Path to the mock campaign workbook.",
    )
    parser.add_argument(
        "--image-root",
        type=Path,
        default=Path("/Users/apple/Desktop/模拟数据"),
        help="Folder containing numbered mock campaign images.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the workbook and image mapping without changing Supabase data.",
    )
    args = parser.parse_args()
    import_mock_campaigns(args.xlsx, args.image_root, args.dry_run)


if __name__ == "__main__":
    main()

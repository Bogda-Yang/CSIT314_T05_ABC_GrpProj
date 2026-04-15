import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request as UrlRequest, urlopen

from core.config import (
    SUPABASE_AVATAR_BUCKET,
    SUPABASE_CAMPAIGN_BUCKET,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_STORAGE_ENABLED,
    SUPABASE_URL,
)


class SupabaseStorage:
    @staticmethod
    def IsConfigured() -> bool:
        return SUPABASE_STORAGE_ENABLED

    @staticmethod
    def _request(
        method: str,
        path: str,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
        expected_statuses: tuple[int, ...] = (200,),
    ) -> bytes:
        if not SupabaseStorage.IsConfigured():
            raise RuntimeError("Supabase Storage is not configured.")

        request_headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        }
        if headers:
            request_headers.update(headers)

        request = UrlRequest(
            f"{SUPABASE_URL}{path}",
            data=data,
            headers=request_headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=20) as response:
                response_body = response.read()
                response_status = getattr(response, "status", response.getcode())
                if response_status not in expected_statuses:
                    raise RuntimeError(
                        f"Supabase Storage request failed with status {response_status}."
                    )
                return response_body
        except HTTPError as error:
            error_body = error.read().decode("utf-8", errors="ignore")
            if error.code in expected_statuses:
                return error_body.encode("utf-8")
            raise RuntimeError(
                f"Supabase Storage request failed with status {error.code}: "
                f"{error_body or error.reason}"
            ) from error
        except URLError as error:
            raise RuntimeError(f"Unable to reach Supabase Storage: {error.reason}") from error

    @staticmethod
    def EnsurePublicBucket(bucket_name: str) -> None:
        payload = json.dumps(
            {
                "id": bucket_name,
                "name": bucket_name,
                "public": True,
                "file_size_limit": 5 * 1024 * 1024,
                "allowed_mime_types": ["image/jpeg", "image/jpg", "image/png", "image/webp"],
            }
        ).encode("utf-8")
        try:
            SupabaseStorage._request(
                "POST",
                "/storage/v1/bucket",
                data=payload,
                headers={"Content-Type": "application/json"},
                expected_statuses=(200, 201),
            )
        except RuntimeError as error:
            error_message = str(error).lower()
            if (
                "already exists" in error_message
                or "duplicate" in error_message
                or "status 409" in error_message
                or "bucketid already exists" in error_message
            ):
                return
            raise

    @staticmethod
    def BuildPublicUrl(bucket_name: str, object_path: str) -> str:
        clean_object_path = normalize_storage_path(object_path)
        return (
            f"{SUPABASE_URL}/storage/v1/object/public/"
            f"{quote(bucket_name)}/{quote(clean_object_path, safe='/')}"
        )

    @staticmethod
    def UploadPublicObject(
        bucket_name: str, object_path: str, file_bytes: bytes, content_type: str
    ) -> None:
        clean_object_path = normalize_storage_path(object_path)
        SupabaseStorage._request(
            "POST",
            f"/storage/v1/object/{quote(bucket_name)}/{quote(clean_object_path, safe='/')}",
            data=file_bytes,
            headers={
                "Content-Type": content_type,
                "x-upsert": "true",
                "Cache-Control": "3600",
            },
            expected_statuses=(200, 201),
        )

    @staticmethod
    def DeleteObject(bucket_name: str, object_path: str) -> None:
        clean_object_path = normalize_storage_path(object_path)
        try:
            SupabaseStorage._request(
                "DELETE",
                f"/storage/v1/object/{quote(bucket_name)}/{quote(clean_object_path, safe='/')}",
                expected_statuses=(200, 204, 404),
            )
        except RuntimeError as error:
            if "status 404" in str(error).lower():
                return
            raise


def normalize_storage_path(stored_path: str) -> str:
    clean_path = stored_path.strip().replace("\\", "/").lstrip("/")
    if not clean_path:
        raise RuntimeError("Storage path cannot be empty.")
    return clean_path


def is_supabase_storage_path(stored_path: str | None) -> bool:
    return bool(stored_path and "/" in stored_path)


def write_local_upload(base_dir: Path, stored_path: str, file_bytes: bytes) -> None:
    local_file_path = base_dir / normalize_storage_path(stored_path)
    local_file_path.parent.mkdir(parents=True, exist_ok=True)
    local_file_path.write_bytes(file_bytes)


def delete_local_upload(base_dir: Path, stored_path: str | None) -> None:
    if not stored_path:
        return
    local_file_path = base_dir / normalize_storage_path(stored_path)
    if local_file_path.exists():
        local_file_path.unlink()


def store_uploaded_asset(
    bucket_name: str,
    local_dir: Path,
    stored_path: str,
    file_bytes: bytes,
    content_type: str,
) -> None:
    if SupabaseStorage.IsConfigured():
        SupabaseStorage.UploadPublicObject(bucket_name, stored_path, file_bytes, content_type)
        return
    write_local_upload(local_dir, stored_path, file_bytes)


def delete_uploaded_asset(bucket_name: str, local_dir: Path, stored_path: str | None) -> None:
    if not stored_path:
        return
    if SupabaseStorage.IsConfigured() and is_supabase_storage_path(stored_path):
        SupabaseStorage.DeleteObject(bucket_name, stored_path)
        return
    delete_local_upload(local_dir, stored_path)


def build_avatar_url(avatar_path: str | None) -> str | None:
    if not avatar_path:
        return None
    if SupabaseStorage.IsConfigured() and is_supabase_storage_path(avatar_path):
        return SupabaseStorage.BuildPublicUrl(SUPABASE_AVATAR_BUCKET, avatar_path)
    return f"/user-uploads/{avatar_path}"


def build_campaign_image_url(image_path: str | None) -> str | None:
    if not image_path:
        return None
    if SupabaseStorage.IsConfigured() and is_supabase_storage_path(image_path):
        return SupabaseStorage.BuildPublicUrl(SUPABASE_CAMPAIGN_BUCKET, image_path)
    return f"/campaign-uploads/{image_path}"

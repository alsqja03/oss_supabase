"""Supabase 기반 회원가입, 로그인, 회원탈퇴 기능.

주의:
- 이 모듈은 database.py의 get_supabase_client()와 hash_password()를 사용합니다.
- Supabase SQL Editor에서 public.users 테이블을 먼저 생성해야 합니다.
- 현재는 기존 프로젝트와의 호환성을 위해 public.users에 비밀번호 해시를 저장합니다.
  신규/실서비스에서는 직접 비밀번호를 저장하는 대신 Supabase Auth 사용을 권장합니다.
"""

from __future__ import annotations

from typing import Any

from postgrest.exceptions import APIError

from database import (
    DatabaseOperationError,
    get_supabase_client,
    hash_password,
)


def create_user(username: str, password: str) -> bool:
    """새 사용자를 생성합니다.

    Args:
        username: 사용자가 선택한 아이디
        password: 평문 비밀번호(데이터베이스에는 해시만 저장)

    Returns:
        True: 회원가입 성공
        False: 아이디 중복

    Raises:
        ValueError: 입력값이 유효하지 않은 경우
        DatabaseOperationError: 그 외 Supabase 작업이 실패한 경우
    """
    if not isinstance(username, str) or not username.strip():
        raise ValueError("아이디를 입력해주세요.")
    if not isinstance(password, str) or not password:
        raise ValueError("비밀번호를 입력해주세요.")

    clean_username = username.strip()

    try:
        response = (
            get_supabase_client()
            .table("users")
            .insert(
                {
                    "username": clean_username,
                    "password": hash_password(password),
                }
            )
            .execute()
        )
        return bool(response.data)
    
    except APIError as exc:
        # 아이디 중복
        if getattr(exc, "code", None) == "23505":
            return False

        # 실제 Supabase 오류 확인
        error_code = getattr(exc, "code", "UNKNOWN")
        error_message = getattr(exc, "message", str(exc))

        raise DatabaseOperationError(
            f"회원가입 실패 (코드: {error_code}): {error_message}"
        ) from exc
    except (ValueError, TypeError):
        raise
    except Exception as exc:
        raise DatabaseOperationError("회원가입 중 Supabase 오류가 발생했습니다.") from exc


def check_login(username: str, password: str) -> int | str | None:
    """아이디와 비밀번호 해시가 일치하면 사용자 ID를 반환합니다.

    로그인 실패 시 None을 반환합니다. 데이터베이스 연결 문제는 예외로 전달합니다.
    """
    if not isinstance(username, str) or not username.strip():
        return None
    if not isinstance(password, str) or not password:
        return None

    try:
        response = (
            get_supabase_client()
            .table("users")
            .select("id")
            .eq("username", username.strip())
            .eq("password", hash_password(password))
            .limit(1)
            .execute()
        )
    except Exception as exc:
        raise DatabaseOperationError(
            "로그인 정보를 확인하지 못했습니다. Supabase 연결을 확인해주세요."
        ) from exc

    rows: list[dict[str, Any]] = response.data or []
    if not rows:
        return None
    return rows[0].get("id")


def delete_user(user_id: int | str) -> bool:
    """사용자 계정을 삭제합니다.

    SQL 스키마에서 외래 키에 ON DELETE CASCADE가 설정되어 있으면 관련 데이터도
    함께 삭제됩니다. 삭제할 사용자가 없으면 False를 반환합니다.
    """
    if user_id is None or (isinstance(user_id, str) and not user_id.strip()):
        raise ValueError("유효한 사용자 ID가 필요합니다.")

    try:
        response = (
            get_supabase_client()
            .table("users")
            .delete()
            .eq("id", user_id)
            .execute()
        )
    except Exception as exc:
        raise DatabaseOperationError(
            "회원 탈퇴에 실패했습니다. Supabase 연결과 테이블 설정을 확인해주세요."
        ) from exc

    return bool(response.data)
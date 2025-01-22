from pathlib import Path

import pytest
from httpx import AsyncClient
from starlette import status

BASE_DIR = Path(__file__).parent

FIXTURES_PATH = BASE_DIR / "fixtures"


@pytest.mark.parametrize(
    ("username", "password", "fixtures", "expected_status"),
    [
        (
            "test_client",
            "secret",
            [
                FIXTURES_PATH / "book.json",
            ],
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures("_common_api_fixture")
async def test_get_book(
    client: AsyncClient,
    expected_status,
) -> None:
    response = await client.get("/api/book")
    assert response.status_code == expected_status
    assert len(response.json()) >= 1

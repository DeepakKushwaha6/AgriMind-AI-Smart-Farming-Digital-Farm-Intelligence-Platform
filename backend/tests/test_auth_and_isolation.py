import pytest
from app.core.security import encrypt_api_key, decrypt_api_key, mask_api_key


@pytest.mark.asyncio
async def test_user_registration_and_login(client):
    # Register Farmer A
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "farmer.a@example.com",
            "password": "Password123!",
            "name": "Farmer A",
            "village": "Jarga",
            "district": "Hazaribagh"
        }
    )
    assert reg_resp.status_code == 200
    data = reg_resp.json()
    assert "access_token" in data
    token_a = data["access_token"]

    # Access /me
    me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "farmer.a@example.com"


@pytest.mark.asyncio
async def test_cross_user_key_isolation(client):
    """Proves User A cannot view, test, or delete User B's API keys."""
    # Register User A
    res_a = await client.post(
        "/api/v1/auth/register",
        json={"email": "usera@example.com", "password": "Password123!", "name": "User A"}
    )
    token_a = res_a.json()["access_token"]

    # Register User B
    res_b = await client.post(
        "/api/v1/auth/register",
        json={"email": "userb@example.com", "password": "Password123!", "name": "User B"}
    )
    token_b = res_b.json()["access_token"]

    # User A saves an OpenWeatherMap key
    save_resp = await client.put(
        "/api/v1/user/api-keys",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "category": "weather",
            "provider_name": "openweathermap",
            "api_key": "secret_key_user_a_12345"
        }
    )
    assert save_resp.status_code == 200
    key_a_id = save_resp.json()["id"]
    # Ensure key is masked
    assert "secret_key_user_a_12345" not in save_resp.json()["key_preview"]
    assert "••••2345" in save_resp.json()["key_preview"]

    # User B lists their keys -> Should be empty, NOT seeing User A's key
    list_b = await client.get("/api/v1/user/api-keys", headers={"Authorization": f"Bearer {token_b}"})
    assert list_b.status_code == 200
    assert len(list_b.json()) == 0

    # User B attempts to delete User A's key -> HTTP 404 forbidden/not found (IDOR protected)
    del_resp = await client.delete(
        f"/api/v1/user/api-keys/{key_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert del_resp.status_code == 404


def test_encryption_and_masking():
    plain = "sk-or-v1-9876543210abcdef"
    cipher = encrypt_api_key(plain)
    assert cipher != plain
    recovered = decrypt_api_key(cipher)
    assert recovered == plain

    masked = mask_api_key(plain)
    assert "sk-••••cdef" in masked
    assert "9876" not in masked

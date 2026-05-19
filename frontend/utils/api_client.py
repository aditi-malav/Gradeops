import requests

BASE_URL = "http://localhost:8000"


def register(email: str, password: str, role: str):
    return requests.post(
        f"{BASE_URL}/register",
        json={
            "email": email,
            "password": password,
            "role": role
        }
    )


def login(email: str, password: str):
    return requests.post(
        f"{BASE_URL}/login",
        json={
            "email": email,
            "password": password
        }
    )


def get_current_user(token: str):
    return requests.get(
        f"{BASE_URL}/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )


def create_course(name: str, code: str, token: str):
    return requests.post(
        f"{BASE_URL}/courses",
        json={
            "name": name,
            "code": code
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )


def get_courses(token: str):
    return requests.get(
        f"{BASE_URL}/courses",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
const API_URL = "http://127.0.0.1:8000/api"

export function getAuthHeaders() {
    const token = localStorage.getItem("access")
    return {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
    }
}

export async function login(pin) {
    const res = await fetch(`${API_URL}/auth/pin-login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pin })
    })

    const data = await res.json()

    if (data.access) {
        localStorage.setItem("access", data.access)
    }

    return data
}
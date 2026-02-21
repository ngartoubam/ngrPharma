import http from "./http";

/**
 * Login pharmacie via PIN
 */
export async function login(pharmacyId, pin) {
    const res = await http.post("/auth/pin-login/", {
        pharmacy_id: pharmacyId,
        pin: pin,
    });

    return res.data;
}

/**
 * Login SaaS Admin (email + password)
 */
export async function adminLogin(email, password) {
    const res = await http.post("/auth/admin-login/", {
        email,
        password,
    });

    return res.data;
}

/**
 * Refresh token
 */
export async function refreshToken(refresh) {
    const res = await http.post("/auth/token/refresh/", {
        refresh,
    });

    return res.data;
}

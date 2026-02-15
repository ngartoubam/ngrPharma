// frontend/src/api/authApi.js
import http from "./http";

/**
 * Login pharmacie via PIN
 * @param {string} pharmacyId - UUID de la pharmacie
 * @param {string} pin - PIN utilisateur (pharmacien / gérant)
 */
export async function login(pharmacyId, pin) {
    const res = await http.post("/auth/pin-login/", {
        pharmacy_id: pharmacyId,
        pin: pin,
    });

    return res.data;
}

/**
 * (Option future)
 * Refresh token
 */
export async function refreshToken(refresh) {
    const res = await http.post("/auth/token/refresh/", {
        refresh,
    });

    return res.data;
}

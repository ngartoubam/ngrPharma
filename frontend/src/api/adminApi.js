// frontend/src/api/adminApi.js
import http from "./http";

/**
 * GET all pharmacies
 */
export async function getPharmacies() {
    const res = await http.get("/admin/pharmacies/");
    return res.data;
}

/**
 * CREATE pharmacy
 */
export async function createPharmacy(data) {
    const res = await http.post("/admin/pharmacies/", data);
    return res.data;
}

/**
 * UPDATE pharmacy
 */
export async function updatePharmacy(id, data) {
    const res = await http.put(`/admin/pharmacies/${id}/`, data);
    return res.data;
}

/**
 * DELETE pharmacy
 */
export async function deletePharmacy(id) {
    const res = await http.delete(`/admin/pharmacies/${id}/`);
    return res.data;
}

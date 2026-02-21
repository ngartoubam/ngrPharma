import { useEffect, useMemo, useState } from "react";
import http from "../../api/http";

const TYPE_OPTIONS = [
  { value: "pharmacie", label: "Pharmacie" },
  { value: "depot", label: "Dépôt" },
];

export default function PharmaciesPage() {
  const [pharmacies, setPharmacies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({
    name: "",
    city: "",
    country: "",
    type: "pharmacie",
  });

  // ================= LOAD =================
  const loadPharmacies = async () => {
    try {
      setLoading(true);
      setError(null);

      const res = await http.get("/admin/pharmacies/");
      const data = res.data?.results ?? res.data ?? [];
      setPharmacies(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setError("Impossible de charger les pharmacies.");
      setPharmacies([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPharmacies();
  }, []);

  // ================= KPI CALCUL =================
  const kpis = useMemo(() => {
    const total = pharmacies.length;
    const active = pharmacies.filter(
      (p) => p.subscription_status === "active",
    ).length;
    const pastDue = pharmacies.filter(
      (p) => p.subscription_status === "past_due",
    ).length;
    const canceled = pharmacies.filter(
      (p) => p.subscription_status === "canceled",
    ).length;
    return { total, active, pastDue, canceled };
  }, [pharmacies]);

  // ================= EDIT =================
  const startEdit = (pharmacy) => {
    setEditingId(pharmacy.id);
    setEditForm({
      name: pharmacy.name ?? "",
      city: pharmacy.city ?? "",
      country: pharmacy.country ?? "",
      type: pharmacy.type ?? "pharmacie",
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditForm({ name: "", city: "", country: "", type: "pharmacie" });
  };

  const saveEdit = async (id) => {
    try {
      // PATCH: name/city/country/type
      await http.patch(`/admin/pharmacies/${id}/`, {
        name: editForm.name,
        city: editForm.city,
        country: editForm.country,
        type: editForm.type,
      });

      cancelEdit();
      loadPharmacies();
    } catch (e) {
      console.error(e);
      alert("Erreur lors de la mise à jour.");
    }
  };

  const deletePharmacy = async (id) => {
    if (!window.confirm("Supprimer cette pharmacie ?")) return;
    try {
      await http.delete(`/admin/pharmacies/${id}/`);
      loadPharmacies();
    } catch (e) {
      console.error(e);
      alert("Erreur lors de la suppression.");
    }
  };

  // ================= SUSPEND / ACTIVATE =================
  const toggleStatus = async (pharmacy) => {
    const isActive = pharmacy.is_active !== false; // par défaut true
    const action = isActive ? "suspend" : "activate";

    try {
      if (action === "suspend") {
        const reason =
          window.prompt("Raison de suspension (optionnel) :") || "";
        await http.post(`/admin/pharmacies/${pharmacy.id}/suspend/`, {
          suspended_reason: reason,
        });
      } else {
        await http.post(`/admin/pharmacies/${pharmacy.id}/activate/`);
      }
      loadPharmacies();
    } catch (e) {
      console.error(e);
      alert("Erreur action activation/suspension.");
    }
  };

  // ================= STATUS BADGE =================
  const StatusBadge = ({ status }) => {
    const base = "px-2 py-1 rounded-full text-xs font-medium";
    const styles = {
      active: "bg-green-100 text-green-700",
      trialing: "bg-blue-100 text-blue-700",
      past_due: "bg-yellow-100 text-yellow-700",
      canceled: "bg-red-100 text-red-700",
      inactive: "bg-gray-100 text-gray-700",
    };

    return (
      <span className={`${base} ${styles[status] || styles.inactive}`}>
        {status || "inactive"}
      </span>
    );
  };

  const ActiveBadge = ({ isActive }) => {
    const base = "px-2 py-1 rounded-full text-xs font-medium";
    return (
      <span
        className={`${base} ${isActive ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}
      >
        {isActive ? "enabled" : "suspended"}
      </span>
    );
  };

  // ================= RENDER =================
  if (loading) return <div className="p-8">Chargement...</div>;
  if (error) return <div className="p-8 text-red-600">{error}</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">
        Gestion des Pharmacies (SaaS Admin)
      </h1>

      {/* ================= KPI CARDS ================= */}
      <div className="grid grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-4 rounded-xl shadow">
          <p className="text-sm text-gray-500">Total</p>
          <p className="text-2xl font-bold">{kpis.total}</p>
        </div>

        <div className="bg-white p-4 rounded-xl shadow">
          <p className="text-sm text-gray-500">Actives (Stripe)</p>
          <p className="text-2xl font-bold text-green-600">{kpis.active}</p>
        </div>

        <div className="bg-white p-4 rounded-xl shadow">
          <p className="text-sm text-gray-500">Past Due</p>
          <p className="text-2xl font-bold text-yellow-600">{kpis.pastDue}</p>
        </div>

        <div className="bg-white p-4 rounded-xl shadow">
          <p className="text-sm text-gray-500">Canceled</p>
          <p className="text-2xl font-bold text-red-600">{kpis.canceled}</p>
        </div>
      </div>

      {/* ================= TABLE ================= */}
      <div className="bg-white rounded-xl shadow p-6 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-gray-600">
              <th className="text-left py-2">Code</th>
              <th className="text-left py-2">Nom</th>
              <th className="text-left py-2">Pays</th>
              <th className="text-left py-2">Ville</th>
              <th className="text-left py-2">Type</th>
              <th className="text-left py-2">Stripe</th>
              <th className="text-left py-2">Platform</th>
              <th className="text-left py-2">Actions</th>
            </tr>
          </thead>

          <tbody>
            {pharmacies.map((pharmacy) => {
              const isEditing = editingId === pharmacy.id;
              const isActive = pharmacy.is_active !== false;

              return (
                <tr key={pharmacy.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 font-medium">{pharmacy.code}</td>

                  <td className="py-2">
                    {isEditing ? (
                      <input
                        className="border rounded px-2 py-1 w-full"
                        value={editForm.name}
                        onChange={(e) =>
                          setEditForm({ ...editForm, name: e.target.value })
                        }
                      />
                    ) : (
                      pharmacy.name
                    )}
                  </td>

                  <td className="py-2">
                    {isEditing ? (
                      <input
                        className="border rounded px-2 py-1 w-full"
                        placeholder="Ex: Mali, Tchad..."
                        value={editForm.country}
                        onChange={(e) =>
                          setEditForm({ ...editForm, country: e.target.value })
                        }
                      />
                    ) : (
                      pharmacy.country || "-"
                    )}
                  </td>

                  <td className="py-2">
                    {isEditing ? (
                      <input
                        className="border rounded px-2 py-1 w-full"
                        value={editForm.city}
                        onChange={(e) =>
                          setEditForm({ ...editForm, city: e.target.value })
                        }
                      />
                    ) : (
                      pharmacy.city || "-"
                    )}
                  </td>

                  <td className="py-2">
                    {isEditing ? (
                      <select
                        className="border rounded px-2 py-1"
                        value={editForm.type}
                        onChange={(e) =>
                          setEditForm({ ...editForm, type: e.target.value })
                        }
                      >
                        {TYPE_OPTIONS.map((t) => (
                          <option key={t.value} value={t.value}>
                            {t.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                      pharmacy.type
                    )}
                  </td>

                  <td className="py-2">
                    <StatusBadge status={pharmacy.subscription_status} />
                  </td>

                  <td className="py-2">
                    <ActiveBadge isActive={isActive} />
                  </td>

                  <td className="py-2 space-x-3">
                    {isEditing ? (
                      <>
                        <button
                          onClick={() => saveEdit(pharmacy.id)}
                          className="text-green-600 font-medium"
                        >
                          Save
                        </button>
                        <button onClick={cancelEdit} className="text-gray-500">
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={() => startEdit(pharmacy)}
                          className="text-blue-600 font-medium"
                        >
                          Edit
                        </button>

                        <button
                          onClick={() => toggleStatus(pharmacy)}
                          className="text-orange-600 font-medium"
                        >
                          {isActive ? "Suspend" : "Activate"}
                        </button>

                        <button
                          onClick={() => deletePharmacy(pharmacy.id)}
                          className="text-red-600 font-medium"
                        >
                          Delete
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

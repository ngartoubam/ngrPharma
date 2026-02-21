import { useEffect, useState } from "react";
import http from "../../api/http";

export default function PharmaciesPage() {
  const [pharmacies, setPharmacies] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  // ================= LOAD =================
  const loadPharmacies = async () => {
    const res = await http.get("/admin/pharmacies/");
    setPharmacies(res.data);
  };

  useEffect(() => {
    loadPharmacies();
  }, []);

  // ================= START EDIT =================
  const startEdit = (pharmacy) => {
    setEditingId(pharmacy.id);
    setEditForm({
      name: pharmacy.name,
      city: pharmacy.city,
      type: pharmacy.type,
    });
  };

  // ================= SAVE EDIT =================
  const saveEdit = async (id) => {
    await http.patch(`/admin/pharmacies/${id}/`, editForm);
    setEditingId(null);
    loadPharmacies();
  };

  // ================= DELETE =================
  const deletePharmacy = async (id) => {
    if (!window.confirm("Supprimer cette pharmacie ?")) return;
    await http.delete(`/admin/pharmacies/${id}/`);
    loadPharmacies();
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">
        Gestion des Pharmacies (SaaS Admin)
      </h1>

      <div className="bg-white rounded-xl shadow p-6">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Code</th>
              <th className="text-left py-2">Nom</th>
              <th className="text-left py-2">Ville</th>
              <th className="text-left py-2">Type</th>
              <th className="text-left py-2">Actions</th>
            </tr>
          </thead>

          <tbody>
            {pharmacies.map((pharmacy) => (
              <tr key={pharmacy.id} className="border-b">
                <td className="py-2">{pharmacy.code}</td>

                {/* ========= NAME ========= */}
                <td className="py-2">
                  {editingId === pharmacy.id ? (
                    <input
                      className="border rounded px-2 py-1"
                      value={editForm.name}
                      onChange={(e) =>
                        setEditForm({ ...editForm, name: e.target.value })
                      }
                    />
                  ) : (
                    pharmacy.name
                  )}
                </td>

                {/* ========= CITY ========= */}
                <td className="py-2">
                  {editingId === pharmacy.id ? (
                    <input
                      className="border rounded px-2 py-1"
                      value={editForm.city || ""}
                      onChange={(e) =>
                        setEditForm({ ...editForm, city: e.target.value })
                      }
                    />
                  ) : (
                    pharmacy.city
                  )}
                </td>

                {/* ========= TYPE ========= */}
                <td className="py-2">
                  {editingId === pharmacy.id ? (
                    <select
                      className="border rounded px-2 py-1"
                      value={editForm.type}
                      onChange={(e) =>
                        setEditForm({ ...editForm, type: e.target.value })
                      }
                    >
                      <option value="pharmacie">Pharmacie</option>
                      <option value="depot">Dépôt</option>
                    </select>
                  ) : (
                    pharmacy.type
                  )}
                </td>

                {/* ========= ACTIONS ========= */}
                <td className="py-2 space-x-3">
                  {editingId === pharmacy.id ? (
                    <>
                      <button
                        onClick={() => saveEdit(pharmacy.id)}
                        className="text-green-600"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        className="text-gray-500"
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => startEdit(pharmacy)}
                        className="text-blue-600"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deletePharmacy(pharmacy.id)}
                        className="text-red-600"
                      >
                        Delete
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

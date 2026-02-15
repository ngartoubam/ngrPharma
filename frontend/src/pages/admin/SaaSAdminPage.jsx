export default function SaaSAdminPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold">Admin SaaS</h1>
        <p className="text-sm text-slate-600">
          Gestion multi-pharmacies, abonnements, paiements, plans, et
          utilisateurs.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl bg-white p-4 border shadow-sm">
          <div className="text-sm text-slate-500">Pharmacies</div>
          <div className="mt-2 text-2xl font-bold">—</div>
          <div className="mt-2 text-xs text-slate-500">
            Liste + création + activation
          </div>
        </div>

        <div className="rounded-2xl bg-white p-4 border shadow-sm">
          <div className="text-sm text-slate-500">Abonnements</div>
          <div className="mt-2 text-2xl font-bold">—</div>
          <div className="mt-2 text-xs text-slate-500">
            Plan, statut, renouvellement
          </div>
        </div>

        <div className="rounded-2xl bg-white p-4 border shadow-sm">
          <div className="text-sm text-slate-500">Paiements</div>
          <div className="mt-2 text-2xl font-bold">—</div>
          <div className="mt-2 text-xs text-slate-500">
            Historique, factures, échecs
          </div>
        </div>
      </div>

      <div className="rounded-2xl bg-white p-4 border shadow-sm">
        <div className="font-semibold">Roadmap backend nécessaire</div>
        <ul className="mt-3 list-disc pl-6 text-sm text-slate-700 space-y-1">
          <li>Models: Organization, Pharmacy, Subscription, Plan, Payment</li>
          <li>RBAC: superadmin SaaS / admin pharmacy / gerant / vendeur</li>
          <li>
            Endpoints: /saas/pharmacies/, /saas/subscriptions/, /saas/payments/
          </li>
          <li>
            Tenant isolation: request.user.pharmacy (déjà en place) + admin
            global
          </li>
        </ul>
      </div>
    </div>
  );
}

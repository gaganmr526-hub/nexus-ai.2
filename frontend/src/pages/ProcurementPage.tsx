import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCompany } from '@/hooks/useCompany'
import { getRequisitions, createRequisition } from '@/api/procurement'
import { getSuppliers } from '@/api/suppliers'
import type { PurchaseOrder, ColumnDef } from '@/types'
import DemoBanner from '@/components/DemoBanner'
import DataTable from '@/components/DataTable'
import StatusBadge from '@/components/StatusBadge'
import Modal from '@/components/Modal'
import toast from 'react-hot-toast'
import { PlusIcon } from 'lucide-react'
import { format } from 'date-fns'

const schema = z.object({
  supplier_id: z.string().min(1, 'Select a supplier'),
  total_amount: z.coerce.number().min(0).optional(),
})
type FormData = z.infer<typeof schema>

export default function ProcurementPage() {
  const { selectedCompany } = useCompany()
  const qc = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'requisitions' | 'negotiation'>('requisitions')

  const { data: requisitions = [], isLoading } = useQuery({
    queryKey: ['requisitions', selectedCompany?.id],
    queryFn: () => getRequisitions(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const { data: suppliers = [] } = useQuery({
    queryKey: ['suppliers', selectedCompany?.id],
    queryFn: () => getSuppliers(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const createMutation = useMutation({
    mutationFn: (data: Partial<PurchaseOrder>) => createRequisition(data),
    onSuccess: () => {
      toast.success('Requisition created')
      qc.invalidateQueries({ queryKey: ['requisitions', selectedCompany?.id] })
      setCreateOpen(false)
      reset()
    },
    onError: () => toast.error('Failed to create requisition'),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = (data: FormData) => {
    if (!selectedCompany) return
    createMutation.mutate({
      ...data,
      company_id: selectedCompany.id,
      currency: 'USD',
    })
  }

  const columns: ColumnDef<Record<string, unknown>>[] = [
    { key: 'order_number', header: 'Requisition #', sortable: true, render: (v) => <span className="font-medium text-slate-200">{String(v ?? '—')}</span> },
    { key: 'supplier_id', header: 'Supplier', render: (v) => suppliers.find((supplier) => supplier.id === String(v))?.name ?? 'Unknown supplier' },
    { key: 'status', header: 'Status', render: (v) => <StatusBadge status={String(v)} /> },
    { key: 'total_amount', header: 'Est. Cost', render: (v, r) => v ? `$${Number(v).toLocaleString()} ${String(r.currency ?? 'USD')}` : '—' },
    { key: 'created_at', header: 'Created', sortable: true, render: (v) => <span className="text-xs text-slate-500">{format(new Date(String(v)), 'MMM d, yyyy')}</span> },
  ]

  // Demo negotiation suggestions
  const suggestions = [
    { supplier: 'TechComp Solutions', component: 'MCU-A4', suggestion: 'Negotiate 15% volume discount by committing to 6-month purchase schedule. Current market has 3 alternatives with 20-day lead times.', supporting: 'Lead time: 45 days | Alternatives: 3 | Market price trend: -8% YoY' },
    { supplier: 'ElectroBase Corp', component: 'PCB-X7', suggestion: 'Request dual-sourcing agreement. Leverage Quantum Parts Ltd as alternative to negotiate 10% price reduction.', supporting: 'Dependency risk: HIGH | Backup supplier: Quantum Parts | Switching cost: $12K' },
    { supplier: 'Global Logistics Hub', component: 'Shipping SLA', suggestion: 'Propose penalty clause for delays > 5 days. Port congestion risk detected in Southeast Asia region.', supporting: 'Avg delay: 8 days | Port risk: MEDIUM | On-time rate: 72%' },
  ]

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to manage procurement.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Procurement</h1>
          <p className="text-slate-500 text-sm">Requisitions, quotes, and negotiation intelligence</p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => setCreateOpen(true)}>
          <PlusIcon className="w-4 h-4" /> New Requisition
        </button>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      <div className="flex gap-1 border-b border-navy-800">
        {(['requisitions', 'negotiation'] as const).map((tab) => (
          <button
            key={tab}
            className={`px-4 py-2 text-sm font-medium transition-colors capitalize border-b-2 -mb-px ${
              activeTab === tab
                ? 'border-navy-400 text-slate-100'
                : 'border-transparent text-slate-500 hover:text-slate-300'
            }`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'negotiation' ? 'Negotiation Assistant' : tab}
          </button>
        ))}
      </div>

      {activeTab === 'requisitions' && (
        <div className="card">
          <DataTable
            data={requisitions as unknown as Record<string, unknown>[]}
            columns={columns}
            isLoading={isLoading}
            keyField="id"
          />
        </div>
      )}

      {activeTab === 'negotiation' && (
        <div className="space-y-4">
          <p className="text-slate-500 text-sm">
            AI-generated negotiation strategies based on your supply chain data, market conditions, and alternative availability.
          </p>
          {suggestions.map((s, i) => (
            <div key={i} className="card space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-slate-200 font-semibold">{s.supplier}</p>
                  <p className="text-slate-500 text-xs">{s.component}</p>
                </div>
                <span className="text-xs bg-navy-700 text-navy-300 px-2 py-0.5 rounded-full">AI Suggestion</span>
              </div>
              <p className="text-slate-300 text-sm">{s.suggestion}</p>
              <div className="p-2 bg-navy-800/50 rounded-lg">
                <p className="text-xs text-slate-500">{s.supporting}</p>
              </div>
              <button className="btn-secondary text-sm">Apply Strategy</button>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={createOpen} onClose={() => setCreateOpen(false)} title="New Requisition" size="md">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="label">Supplier</label>
            <select {...register('supplier_id')} className="input" defaultValue="">
              <option value="" disabled>Select a supplier</option>
              {suppliers.map((supplier) => (
                <option key={supplier.id} value={supplier.id}>{supplier.name}</option>
              ))}
            </select>
            {errors.supplier_id && <p className="text-red-400 text-xs mt-1">{errors.supplier_id.message}</p>}
          </div>
          <div>
            <label className="label">Estimated Cost (USD)</label>
            <input {...register('total_amount')} type="number" min="0" className="input" placeholder="50000" />
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" className="btn-secondary" onClick={() => setCreateOpen(false)}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Requisition'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

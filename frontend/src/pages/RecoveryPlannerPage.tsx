import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCompany } from '@/hooks/useCompany'
import { getRecoveryPlans, createRecoveryPlan, updateRecoveryPlan, getRecoveryActions, createRecoveryAction } from '@/api/recovery'
import type { RecoveryPlan, RecoveryAction } from '@/types'
import DemoBanner from '@/components/DemoBanner'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'
import StatusBadge from '@/components/StatusBadge'
import Modal from '@/components/Modal'
import toast from 'react-hot-toast'
import { PlusIcon, DownloadIcon, CheckIcon } from 'lucide-react'
import { format } from 'date-fns'

const planSchema = z.object({
  name: z.string().min(1),
  description: z.string().optional(),
})
const actionSchema = z.object({
  action_type: z.string().min(1),
  description: z.string().min(1),
  due_date: z.string().optional(),
  assignee: z.string().optional(),
})
type PlanForm = z.infer<typeof planSchema>
type ActionForm = z.infer<typeof actionSchema>

export default function RecoveryPlannerPage() {
  const { selectedCompany } = useCompany()
  const qc = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  const scenarioId = searchParams.get('scenario_id')
  const scenarioName = searchParams.get('scenario_name')
  const [createPlanOpen, setCreatePlanOpen] = useState(false)
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null)
  const [createActionOpen, setCreateActionOpen] = useState(false)

  const { data: plans = [], isLoading } = useQuery({
    queryKey: ['recovery-plans', selectedCompany?.id],
    queryFn: () => getRecoveryPlans(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const { data: actions = [] } = useQuery({
    queryKey: ['recovery-actions', selectedPlanId],
    queryFn: () => getRecoveryActions(selectedPlanId!),
    enabled: !!selectedPlanId,
  })

  const selectedPlan = plans.find((p) => p.id === selectedPlanId)

  const createPlanMutation = useMutation({
    mutationFn: (data: Partial<RecoveryPlan>) => createRecoveryPlan(data),
    onSuccess: (p) => {
      toast.success('Plan created')
      qc.setQueryData<RecoveryPlan[]>(['recovery-plans', p.company_id], (current = []) => [
        p,
        ...current.filter((plan) => plan.id !== p.id),
      ])
      qc.invalidateQueries({ queryKey: ['recovery-plans', selectedCompany?.id] })
      setSelectedPlanId(p.id)
      setCreatePlanOpen(false)
      planReset()
      setSearchParams({}, { replace: true })
    },
    onError: () => toast.error('Could not create recovery plan. Please try again.'),
  })

  const updatePlanMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<RecoveryPlan> }) =>
      updateRecoveryPlan(id, data),
    onSuccess: () => {
      toast.success('Plan updated')
      qc.invalidateQueries({ queryKey: ['recovery-plans', selectedCompany?.id] })
    },
  })

  const createActionMutation = useMutation({
    mutationFn: (data: Partial<RecoveryAction>) => createRecoveryAction(selectedPlanId!, data),
    onSuccess: () => {
      toast.success('Action added')
      qc.invalidateQueries({ queryKey: ['recovery-actions', selectedPlanId] })
      setCreateActionOpen(false)
      actionReset()
    },
  })

  const { register: planRegister, handleSubmit: planSubmit, reset: planReset, formState: { errors: planErrors } } = useForm<PlanForm>({ resolver: zodResolver(planSchema) })
  const { register: actionRegister, handleSubmit: actionSubmit, reset: actionReset, formState: { errors: actionErrors } } = useForm<ActionForm>({ resolver: zodResolver(actionSchema) })

  useEffect(() => {
    if (!scenarioId || !scenarioName) return
    planReset({
      name: `${scenarioName} Recovery Plan`,
      description: `Recovery actions for the ${scenarioName} disruption scenario.`,
    })
    setCreatePlanOpen(true)
  }, [scenarioId, scenarioName, planReset])

  const onCreatePlan = (data: PlanForm) => {
    if (!selectedCompany) return
    createPlanMutation.mutate({
      ...data,
      company_id: selectedCompany.id,
      scenario_id: scenarioId ?? undefined,
      status: 'draft',
    })
  }

  const closeCreatePlan = () => {
    setCreatePlanOpen(false)
    planReset()
    if (scenarioId || scenarioName) setSearchParams({}, { replace: true })
  }

  const onCreateAction = (data: ActionForm) => {
    createActionMutation.mutate({ ...data, status: 'pending' })
  }

  const exportCsv = () => {
    if (!actions.length) return
    const rows = [['Type', 'Description', 'Status', 'Due Date', 'Assignee'],
      ...actions.map((a) => [a.action_type, a.description, a.status, a.due_date ?? '', a.assignee ?? ''])]
    const csv = rows.map((r) => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'recovery-plan.csv'
    a.click()
  }

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to manage recovery plans.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Recovery Planner</h1>
          <p className="text-slate-500 text-sm">Create and manage supply chain recovery plans</p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => {
          planReset()
          setCreatePlanOpen(true)
        }}>
          <PlusIcon className="w-4 h-4" /> New Plan
        </button>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Plans List */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wide">Plans</h3>
          {isLoading ? (
            <div className="flex justify-center py-8"><LoadingSpinner /></div>
          ) : plans.length === 0 ? (
            <EmptyState title="No plans" description="Create a recovery plan to get started." />
          ) : (
            plans.map((plan) => (
              <div
                key={plan.id}
                className={`p-4 rounded-xl border cursor-pointer transition-colors ${
                  selectedPlanId === plan.id
                    ? 'border-navy-500 bg-navy-800/50'
                    : 'border-navy-800 bg-navy-900 hover:border-navy-700'
                }`}
                onClick={() => setSelectedPlanId(plan.id)}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-slate-200 font-medium text-sm">{plan.name}</p>
                  <StatusBadge status={plan.status} />
                </div>
                {plan.description && (
                  <p className="text-slate-500 text-xs mt-1 line-clamp-2">{plan.description}</p>
                )}
                <p className="text-slate-600 text-xs mt-2">
                  {format(new Date(plan.created_at), 'MMM d, yyyy')}
                </p>
              </div>
            ))
          )}
        </div>

        {/* Plan Detail */}
        <div className="lg:col-span-2 space-y-4">
          {!selectedPlan ? (
            <div className="card flex items-center justify-center h-48">
              <p className="text-slate-500 text-sm">Select a plan to view details</p>
            </div>
          ) : (
            <>
              <div className="card">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-slate-100">{selectedPlan.name}</h2>
                    <p className="text-slate-500 text-sm mt-1">{selectedPlan.description}</p>
                  </div>
                  <div className="flex gap-2">
                    <StatusBadge status={selectedPlan.status} />
                  </div>
                </div>

                <div className="flex gap-2 flex-wrap">
                  {selectedPlan.status === 'draft' && (
                    <button
                      className="btn-secondary text-sm"
                      onClick={() => updatePlanMutation.mutate({ id: selectedPlan.id, data: { status: 'pending_approval' } })}
                    >
                      Submit for Approval
                    </button>
                  )}
                  {selectedPlan.status === 'pending_approval' && (
                    <button
                      className="btn-primary text-sm flex items-center gap-1"
                      onClick={() => updatePlanMutation.mutate({ id: selectedPlan.id, data: { status: 'approved' } })}
                    >
                      <CheckIcon className="w-4 h-4" /> Approve
                    </button>
                  )}
                  {selectedPlan.status === 'approved' && (
                    <button
                      className="btn-primary text-sm"
                      onClick={() => updatePlanMutation.mutate({ id: selectedPlan.id, data: { status: 'active' } })}
                    >
                      Activate Plan
                    </button>
                  )}
                  <button className="btn-secondary text-sm flex items-center gap-1" onClick={exportCsv}>
                    <DownloadIcon className="w-4 h-4" /> Export
                  </button>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-300">Actions ({actions.length})</h3>
                  <button className="btn-secondary text-sm flex items-center gap-1" onClick={() => setCreateActionOpen(true)}>
                    <PlusIcon className="w-4 h-4" /> Add Action
                  </button>
                </div>

                {actions.length === 0 ? (
                  <EmptyState title="No actions" description="Add recovery actions to this plan." />
                ) : (
                  <div className="space-y-3">
                    {actions.map((action) => (
                      <div key={action.id} className="flex items-start gap-3 p-3 bg-navy-800/50 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs bg-navy-700 text-navy-300 px-2 py-0.5 rounded-full">
                              {action.action_type}
                            </span>
                            <StatusBadge status={action.status} />
                          </div>
                          <p className="text-slate-300 text-sm">{action.description}</p>
                          {(action.due_date || action.assignee) && (
                            <p className="text-slate-500 text-xs mt-1">
                              {action.assignee && `Assigned to: ${action.assignee}`}
                              {action.due_date && ` • Due: ${format(new Date(action.due_date), 'MMM d')}`}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <Modal isOpen={createPlanOpen} onClose={closeCreatePlan} title="Create Recovery Plan" size="md">
        <form onSubmit={planSubmit(onCreatePlan)} className="space-y-4">
          <div>
            <label className="label">Plan Name</label>
            <input {...planRegister('name')} className="input" placeholder="e.g. Semiconductor Shortage Response" />
            {planErrors.name && <p className="text-red-400 text-xs mt-1">{planErrors.name.message}</p>}
          </div>
          <div>
            <label className="label">Description</label>
            <textarea {...planRegister('description')} className="input min-h-[80px]" placeholder="Describe the recovery plan..." />
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" className="btn-secondary" onClick={closeCreatePlan}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={createPlanMutation.isPending}>
              {createPlanMutation.isPending ? 'Creating...' : 'Create Plan'}
            </button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={createActionOpen} onClose={() => setCreateActionOpen(false)} title="Add Recovery Action" size="md">
        <form onSubmit={actionSubmit(onCreateAction)} className="space-y-4">
          <div>
            <label className="label">Action Type</label>
            <select {...actionRegister('action_type')} className="input">
              <option value="">Select type...</option>
              <option value="supplier_switch">Supplier Switch</option>
              <option value="inventory_build">Inventory Build</option>
              <option value="demand_reduction">Demand Reduction</option>
              <option value="logistics_reroute">Logistics Reroute</option>
              <option value="contract_negotiation">Contract Negotiation</option>
              <option value="emergency_procurement">Emergency Procurement</option>
            </select>
            {actionErrors.action_type && <p className="text-red-400 text-xs mt-1">{actionErrors.action_type.message}</p>}
          </div>
          <div>
            <label className="label">Description</label>
            <textarea {...actionRegister('description')} className="input min-h-[80px]" placeholder="Describe the action..." />
            {actionErrors.description && <p className="text-red-400 text-xs mt-1">{actionErrors.description.message}</p>}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Due Date</label>
              <input {...actionRegister('due_date')} type="date" className="input" />
            </div>
            <div>
              <label className="label">Assignee</label>
              <input {...actionRegister('assignee')} className="input" placeholder="Name or team" />
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" className="btn-secondary" onClick={() => setCreateActionOpen(false)}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={createActionMutation.isPending}>
              {createActionMutation.isPending ? 'Adding...' : 'Add Action'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

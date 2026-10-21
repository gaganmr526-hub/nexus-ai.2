import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/store/auth'
import { useNavigate } from 'react-router-dom'
import { getCompanies, createCompany } from '@/api/companies'
import { apiClient } from '@/api/client'
import type { User, Company } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner'
import Modal from '@/components/Modal'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { PlusIcon, RefreshCwIcon, ServerIcon, MailIcon, DatabaseIcon, CheckCircleIcon } from 'lucide-react'

const companySchema = z.object({
  name: z.string().min(1),
  industry: z.string().min(1),
  description: z.string().optional(),
  is_demo: z.boolean().optional(),
})
type CompanyForm = z.infer<typeof companySchema>

export default function AdminPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [createCompanyOpen, setCreateCompanyOpen] = useState(false)

  const { data: companies = [], isLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: getCompanies,
  })

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await apiClient.get('/health')
      return res.data as { status: string; version: string }
    },
    retry: false,
  })

  const { data: users = [] } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await apiClient.get<User[]>('/auth/users')
      return res.data
    },
    enabled: user?.is_platform_admin === true,
    retry: false,
  })

  const createCompanyMutation = useMutation({
    mutationFn: (data: Partial<Company>) => createCompany(data),
    onSuccess: () => {
      toast.success('Company created')
      qc.invalidateQueries({ queryKey: ['companies'] })
      setCreateCompanyOpen(false)
      reset()
    },
    onError: () => toast.error('Failed to create company'),
  })

  const seedMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/admin/seed')
      return res.data
    },
    onSuccess: () => {
      toast.success('Demo data reset!')
      qc.invalidateQueries()
    },
    onError: () => toast.error('Seed failed'),
  })

  const { register, handleSubmit, reset, formState: { errors } } = useForm<CompanyForm>({
    resolver: zodResolver(companySchema),
  })

  if (!user?.is_platform_admin) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <p className="text-slate-500">You don't have admin access.</p>
        <button className="btn-secondary" onClick={() => navigate('/dashboard')}>
          Go to Dashboard
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Administration</h1>
        <p className="text-slate-500 text-sm">Platform management and configuration</p>
      </div>

      {/* System Health */}
      <div className="card space-y-4">
        <h3 className="text-sm font-semibold text-slate-300">System Status</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: 'API Backend', status: health?.status === 'ok' ? 'healthy' : 'unknown', icon: ServerIcon },
            { label: 'Database', status: health ? 'healthy' : 'unknown', icon: DatabaseIcon },
            { label: 'SMTP Email', status: 'not_configured', icon: MailIcon },
            { label: 'ERP Integration', status: 'not_configured', icon: DatabaseIcon },
          ].map(({ label, status, icon: Icon }) => (
            <div key={label} className="p-3 bg-navy-800/50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Icon className="w-4 h-4 text-slate-500" />
                <span className="text-xs text-slate-400">{label}</span>
              </div>
              <div className={`text-xs font-semibold ${
                status === 'healthy' ? 'text-green-400' :
                status === 'not_configured' ? 'text-slate-500' : 'text-amber-400'
              }`}>
                {status === 'healthy' ? '✓ Healthy' : status === 'not_configured' ? '— Not Configured' : '? Unknown'}
              </div>
            </div>
          ))}
        </div>
        {health && (
          <p className="text-slate-600 text-xs">API Version: {health.version}</p>
        )}
      </div>

      {/* Companies */}
      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-300">Companies ({companies.length})</h3>
          <button className="btn-primary text-sm flex items-center gap-1" onClick={() => setCreateCompanyOpen(true)}>
            <PlusIcon className="w-4 h-4" /> New Company
          </button>
        </div>
        {isLoading ? (
          <div className="flex justify-center py-4"><LoadingSpinner /></div>
        ) : (
          <div className="space-y-2">
            {companies.map((company) => (
              <div key={company.id} className="flex items-center justify-between p-3 bg-navy-800/50 rounded-lg">
                <div>
                  <p className="text-slate-200 text-sm font-medium">{company.name}</p>
                  <p className="text-slate-500 text-xs">{company.industry} • {company.tenant_id}</p>
                </div>
                <div className="flex items-center gap-2">
                  {company.is_demo && <span className="demo-badge">DEMO</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Users */}
      {users.length > 0 && (
        <div className="card space-y-4">
          <h3 className="text-sm font-semibold text-slate-300">Users ({users.length})</h3>
          <div className="space-y-2">
            {users.map((u) => (
              <div key={u.id} className="flex items-center justify-between p-3 bg-navy-800/50 rounded-lg">
                <div>
                  <p className="text-slate-200 text-sm font-medium">{u.full_name}</p>
                  <p className="text-slate-500 text-xs">{u.email}</p>
                </div>
                <div className="flex items-center gap-2">
                  {u.is_platform_admin && <span className="text-xs text-purple-400 bg-purple-900/30 px-2 py-0.5 rounded-full">Admin</span>}
                  {u.is_active
                    ? <CheckCircleIcon className="w-4 h-4 text-green-400" />
                    : <span className="text-xs text-red-400">Inactive</span>
                  }
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Danger Zone */}
      <div className="card border-red-900/50 space-y-4">
        <h3 className="text-sm font-semibold text-red-400">Danger Zone</h3>
        <div className="flex items-center justify-between p-3 bg-red-900/10 rounded-lg">
          <div>
            <p className="text-slate-300 text-sm font-medium">Reset Demo Data</p>
            <p className="text-slate-500 text-xs">Re-seed the database with fresh synthetic demo data.</p>
          </div>
          <button
            className="btn-danger text-sm flex items-center gap-2"
            onClick={() => seedMutation.mutate()}
            disabled={seedMutation.isPending}
          >
            {seedMutation.isPending ? <LoadingSpinner size="sm" /> : <RefreshCwIcon className="w-4 h-4" />}
            Reset Demo
          </button>
        </div>
      </div>

      <Modal isOpen={createCompanyOpen} onClose={() => setCreateCompanyOpen(false)} title="Create Company" size="md">
        <form onSubmit={handleSubmit((data) => createCompanyMutation.mutate(data))} className="space-y-4">
          <div>
            <label className="label">Company Name</label>
            <input {...register('name')} className="input" placeholder="Acme Corp" />
            {errors.name && <p className="text-red-400 text-xs mt-1">{errors.name.message}</p>}
          </div>
          <div>
            <label className="label">Industry</label>
            <input {...register('industry')} className="input" placeholder="Electronics, Automotive, etc." />
            {errors.industry && <p className="text-red-400 text-xs mt-1">{errors.industry.message}</p>}
          </div>
          <div>
            <label className="label">Description</label>
            <textarea {...register('description')} className="input min-h-[60px]" placeholder="Optional description..." />
          </div>
          <div className="flex items-center gap-2">
            <input {...register('is_demo')} type="checkbox" id="is_demo" className="accent-navy-400" />
            <label htmlFor="is_demo" className="text-sm text-slate-400">Mark as demo company</label>
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" className="btn-secondary" onClick={() => setCreateCompanyOpen(false)}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={createCompanyMutation.isPending}>
              {createCompanyMutation.isPending ? 'Creating...' : 'Create Company'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

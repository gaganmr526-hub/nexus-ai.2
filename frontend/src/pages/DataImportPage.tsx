import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useCompany } from '@/hooks/useCompany'
import { uploadImportFile, getImportJobs, confirmImport, downloadTemplate } from '@/api/imports'
import type { ImportJob, ColumnDef } from '@/types'
import DemoBanner from '@/components/DemoBanner'
import DataTable from '@/components/DataTable'
import StatusBadge from '@/components/StatusBadge'
import LoadingSpinner from '@/components/LoadingSpinner'
import toast from 'react-hot-toast'
import { UploadCloudIcon, DownloadIcon, CheckIcon, AlertCircleIcon } from 'lucide-react'
import { format } from 'date-fns'
import clsx from 'clsx'

const IMPORT_TYPES = [
  { value: 'suppliers', label: 'Suppliers' },
  { value: 'relationships', label: 'Relationships' },
  { value: 'components', label: 'Components' },
  { value: 'inventory', label: 'Inventory' },
  { value: 'purchase_orders', label: 'Purchase Orders' },
]

export default function DataImportPage() {
  const { selectedCompany } = useCompany()
  const qc = useQueryClient()
  const [importType, setImportType] = useState('suppliers')
  const [currentJob, setCurrentJob] = useState<ImportJob | null>(null)

  const { data: jobs = [], isLoading: jobsLoading } = useQuery({
    queryKey: ['import-jobs', selectedCompany?.id],
    queryFn: () => getImportJobs(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadImportFile(selectedCompany!.id, importType, file),
    onSuccess: (job) => {
      toast.success('File uploaded! Preview ready.')
      qc.invalidateQueries({ queryKey: ['import-jobs', selectedCompany?.id] })
      setCurrentJob(job)
    },
    onError: () => toast.error('Upload failed'),
  })

  const confirmMutation = useMutation({
    mutationFn: (id: string) => confirmImport(id),
    onSuccess: (job) => {
      toast.success('Import confirmed!')
      qc.invalidateQueries({ queryKey: ['import-jobs', selectedCompany?.id] })
      setCurrentJob(job)
    },
    onError: () => toast.error('Confirm failed'),
  })

  const onDrop = useCallback(
    (accepted: File[]) => {
      const file = accepted[0]
      if (!file) return
      if (!file.name.match(/\.(csv|xlsx|json)$/i)) {
        toast.error('Only CSV, XLSX, and JSON files are supported')
        return
      }
      if (!selectedCompany) { toast.error('Select a company first'); return }
      uploadMutation.mutate(file)
    },
    [uploadMutation, selectedCompany]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'], 'application/json': ['.json'] },
    maxFiles: 1,
  })

  const handleDownloadTemplate = async () => {
    try {
      const blob = await downloadTemplate(importType)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${importType}-template.csv`
      a.click()
    } catch {
      // Fallback: generate a simple CSV template
      const headers: Record<string, string[]> = {
        suppliers: ['name', 'supplier_type', 'tier_level', 'risk_score', 'geographic_region'],
        relationships: ['from_supplier_id', 'to_supplier_id', 'relationship_type', 'confidence_score'],
        components: ['name', 'sku', 'category', 'unit_cost', 'lead_time_days'],
        inventory: ['component_id', 'quantity', 'location', 'last_updated'],
        purchase_orders: ['supplier_id', 'order_number', 'total_amount', 'currency', 'delivery_date'],
      }
      const csv = headers[importType]?.join(',') ?? 'id,name'
      const blob2 = new Blob([csv], { type: 'text/csv' })
      const url2 = URL.createObjectURL(blob2)
      const a = document.createElement('a')
      a.href = url2
      a.download = `${importType}-template.csv`
      a.click()
    }
  }

  const jobColumns: ColumnDef<Record<string, unknown>>[] = [
    { key: 'filename', header: 'File', render: (v) => <span className="font-medium text-slate-200">{String(v)}</span> },
    { key: 'import_type', header: 'Type', render: (v) => <span className="capitalize">{String(v)}</span> },
    { key: 'status', header: 'Status', render: (v) => <StatusBadge status={String(v)} /> },
    { key: 'total_rows', header: 'Rows' },
    { key: 'valid_rows', header: 'Valid', render: (v) => <span className="text-green-400">{String(v ?? '—')}</span> },
    { key: 'error_count', header: 'Errors', render: (v) => Number(v) > 0 ? <span className="text-red-400">{String(v)}</span> : <span className="text-slate-500">0</span> },
    {
      key: 'created_at',
      header: 'Date',
      render: (v) => (
        <span className="text-xs text-slate-500">{format(new Date(String(v)), 'MMM d, HH:mm')}</span>
      ),
    },
  ]

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to import data.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Data Import</h1>
        <p className="text-slate-500 text-sm">Upload supplier, relationship, and component data</p>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Panel */}
        <div className="space-y-4">
          <div className="card space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-300">Upload File</h3>
              <button
                className="btn-secondary text-sm flex items-center gap-1"
                onClick={handleDownloadTemplate}
              >
                <DownloadIcon className="w-4 h-4" /> Sample Template
              </button>
            </div>

            <div>
              <label className="label">Import Type</label>
              <select
                className="input"
                value={importType}
                onChange={(e) => setImportType(e.target.value)}
              >
                {IMPORT_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>

            <div
              {...getRootProps()}
              className={clsx(
                'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors',
                isDragActive
                  ? 'border-navy-400 bg-navy-800/50'
                  : 'border-navy-700 hover:border-navy-600'
              )}
            >
              <input {...getInputProps()} />
              <UploadCloudIcon className="w-10 h-10 text-navy-600 mx-auto mb-3" />
              {uploadMutation.isPending ? (
                <div className="flex flex-col items-center gap-2">
                  <LoadingSpinner />
                  <p className="text-slate-400 text-sm">Uploading...</p>
                </div>
              ) : isDragActive ? (
                <p className="text-navy-300 text-sm">Drop the file here</p>
              ) : (
                <>
                  <p className="text-slate-400 text-sm mb-1">
                    Drag & drop a CSV or JSON file here, or click to browse
                  </p>
                  <p className="text-slate-600 text-xs">Supports .csv and .json formats</p>
                </>
              )}
            </div>
          </div>

          {/* Preview / Result */}
          {currentJob && (
            <div className="card space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-300">
                  {currentJob.filename}
                </h3>
                <StatusBadge status={currentJob.status} />
              </div>

              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-2 bg-navy-800/50 rounded-lg">
                  <p className="text-xl font-bold text-slate-100">{currentJob.total_rows ?? 0}</p>
                  <p className="text-xs text-slate-500">Total Rows</p>
                </div>
                <div className="p-2 bg-navy-800/50 rounded-lg">
                  <p className="text-xl font-bold text-green-400">{currentJob.valid_rows ?? 0}</p>
                  <p className="text-xs text-slate-500">Valid</p>
                </div>
                <div className="p-2 bg-navy-800/50 rounded-lg">
                  <p className="text-xl font-bold text-red-400">{currentJob.error_count ?? 0}</p>
                  <p className="text-xs text-slate-500">Errors</p>
                </div>
              </div>

              {(currentJob.error_count ?? 0) > 0 && (
                <div className="flex items-start gap-2 p-3 bg-red-900/20 border border-red-700/30 rounded-lg">
                  <AlertCircleIcon className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-red-300 text-xs">
                    {currentJob.error_count} rows have validation errors and will be skipped.
                  </p>
                </div>
              )}

              {currentJob.status === 'preview' && (
                <button
                  className="btn-primary w-full flex items-center justify-center gap-2"
                  onClick={() => confirmMutation.mutate(currentJob.id)}
                  disabled={confirmMutation.isPending}
                >
                  <CheckIcon className="w-4 h-4" />
                  {confirmMutation.isPending ? 'Importing...' : 'Confirm Import'}
                </button>
              )}
            </div>
          )}
        </div>

        {/* Import History */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Import History</h3>
          <DataTable
            data={jobs as unknown as Record<string, unknown>[]}
            columns={jobColumns}
            isLoading={jobsLoading}
            onRowClick={(row) => setCurrentJob(row as unknown as ImportJob)}
            keyField="id"
            pageSize={10}
            emptyMessage="No imports yet"
          />
        </div>
      </div>
    </div>
  )
}

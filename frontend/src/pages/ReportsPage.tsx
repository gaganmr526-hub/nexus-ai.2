import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useCompany } from '@/hooks/useCompany'
import { generateReport, exportReportCsv, exportReportJson } from '@/api/reports'
import DemoBanner from '@/components/DemoBanner'
import LoadingSpinner from '@/components/LoadingSpinner'
import toast from 'react-hot-toast'
import {
  FileTextIcon,
  NetworkIcon,
  ZapIcon,
  ShieldIcon,
  BarChart2Icon,
  DownloadIcon,
} from 'lucide-react'
import { format } from 'date-fns'

const REPORT_TYPES = [
  {
    type: 'executive_summary',
    label: 'Executive Summary',
    icon: BarChart2Icon,
    description: 'High-level KPIs, top risks, and recommended actions for leadership.',
  },
  {
    type: 'hidden_dependencies',
    label: 'Hidden Dependencies',
    icon: NetworkIcon,
    description: 'Full analysis of AI-detected shared upstream risks and dependency paths.',
  },
  {
    type: 'disruption_impact',
    label: 'Disruption Impact',
    icon: ZapIcon,
    description: 'Scenario simulation results with financial and operational impact assessment.',
  },
  {
    type: 'audit_trail',
    label: 'Audit Trail',
    icon: ShieldIcon,
    description: 'History of data imports, finding updates, and user actions.',
  },
  {
    type: 'supplier_risk',
    label: 'Supplier Risk Profile',
    icon: FileTextIcon,
    description: 'Per-supplier risk scores, verification status, and criticality breakdown.',
  },
  {
    type: 'recovery_status',
    label: 'Recovery Plan Status',
    icon: ShieldIcon,
    description: 'Current status of all recovery plans and open actions.',
  },
]

export default function ReportsPage() {
  const { selectedCompany } = useCompany()
  const [generatedReports, setGeneratedReports] = useState<Record<string, { id: string; generated_at: string; data: Record<string, unknown> }>>({})

  const generateMutation = useMutation({
    mutationFn: (reportType: string) => generateReport(selectedCompany!.id, reportType),
    onSuccess: (report) => {
      toast.success('Report generated!')
      setGeneratedReports((prev) => ({
        ...prev,
        [report.report_type]: {
          id: report.id,
          generated_at: report.generated_at,
          data: report.data,
        },
      }))
    },
    onError: () => toast.error('Failed to generate report'),
  })

  const handleExportCsv = async (reportId: string, type: string) => {
    try {
      const blob = await exportReportCsv(reportId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${type}-report.csv`
      a.click()
    } catch {
      toast.error('Export failed')
    }
  }

  const handleExportJson = async (reportId: string, type: string) => {
    try {
      const blob = await exportReportJson(reportId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${type}-report.json`
      a.click()
    } catch {
      toast.error('Export failed')
    }
  }

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to generate reports.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Reports</h1>
        <p className="text-slate-500 text-sm">Generate and export supply chain intelligence reports</p>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {REPORT_TYPES.map(({ type, label, icon: Icon, description }) => {
          const generated = generatedReports[type]
          const isPending = generateMutation.isPending && generateMutation.variables === type

          return (
            <div key={type} className="card space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 bg-navy-800 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Icon className="w-5 h-5 text-navy-400" />
                </div>
                <div>
                  <p className="text-slate-200 font-semibold text-sm">{label}</p>
                  <p className="text-slate-500 text-xs mt-0.5">{description}</p>
                </div>
              </div>

              {generated && (
                <div className="p-3 bg-navy-800/50 rounded-lg text-xs space-y-1">
                  <p className="text-green-400 font-medium">✓ Generated</p>
                  <p className="text-slate-500">
                    {format(new Date(generated.generated_at), 'MMM d, yyyy HH:mm')}
                  </p>
                </div>
              )}

              <div className="flex gap-2">
                <button
                  className="btn-primary flex-1 text-sm"
                  onClick={() => generateMutation.mutate(type)}
                  disabled={isPending}
                >
                  {isPending ? (
                    <span className="flex items-center justify-center gap-2">
                      <LoadingSpinner size="sm" /> Generating...
                    </span>
                  ) : (
                    'Generate'
                  )}
                </button>
                {generated && (
                  <>
                    <button
                      className="btn-secondary text-sm flex items-center gap-1"
                      onClick={() => handleExportCsv(generated.id, type)}
                    >
                      <DownloadIcon className="w-3.5 h-3.5" /> CSV
                    </button>
                    <button
                      className="btn-secondary text-sm flex items-center gap-1"
                      onClick={() => handleExportJson(generated.id, type)}
                    >
                      <DownloadIcon className="w-3.5 h-3.5" /> JSON
                    </button>
                  </>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

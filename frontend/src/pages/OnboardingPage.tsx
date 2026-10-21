import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { NetworkIcon, SearchIcon, ZapIcon, ArrowRightIcon, CheckIcon } from 'lucide-react'
import { useCompany } from '@/hooks/useCompany'
import LoadingSpinner from '@/components/LoadingSpinner'

const steps = [
  {
    icon: NetworkIcon,
    title: 'Welcome to NEXUSTRACE AI',
    description:
      'NEXUSTRACE AI maps your entire supply chain — including hidden tier-2, tier-3, and beyond suppliers you may not even know about. Powered by AI inference and evidence-based analysis.',
    bullets: [
      'Automated supply chain graph from your supplier data',
      'AI-powered hidden dependency detection',
      'Real-time risk scoring and criticality assessment',
      'Disruption scenario simulation and impact modeling',
    ],
  },
  {
    icon: SearchIcon,
    title: 'Choose Your Workspace',
    description:
      'Your demo workspace contains synthetic data for 3 companies with 45+ suppliers across 4 tiers. All data is fictional and safe to explore.',
    bullets: [],
  },
  {
    icon: ZapIcon,
    title: 'Ready to Explore',
    description:
      'You\'ll see the NEXUSTRACE AI dashboard with live KPIs, risk findings, and supply chain visualizations. The "Helios Semiconductor Works" demo scenario shows a critical hidden dependency.',
    bullets: [
      'Dashboard: KPIs and risk overview',
      'Network Explorer: interactive supply graph',
      'Hidden Dependencies: AI-detected risks',
      'Disruption Simulator: model supply shocks',
    ],
  },
]

export default function OnboardingPage() {
  const [step, setStep] = useState(0)
  const navigate = useNavigate()
  const { companies, selectedCompany, selectCompany, isLoading } = useCompany()

  const currentStep = steps[step]
  const Icon = currentStep.icon

  return (
    <div className="min-h-screen bg-navy-950 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="flex items-center justify-center gap-2 mb-8">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i === step ? 'w-8 bg-navy-400' : i < step ? 'w-4 bg-navy-600' : 'w-4 bg-navy-800'
              }`}
            />
          ))}
        </div>

        <div className="card">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-navy-800 rounded-xl flex items-center justify-center flex-shrink-0">
              <Icon className="w-6 h-6 text-navy-400" />
            </div>
            <div>
              <p className="text-xs text-navy-400 uppercase tracking-wide font-medium">
                Step {step + 1} of {steps.length}
              </p>
              <h2 className="text-xl font-bold text-slate-100">{currentStep.title}</h2>
            </div>
          </div>

          <p className="text-slate-400 mb-6">{currentStep.description}</p>

          {step === 1 && (
            <div className="space-y-2 mb-6">
              {isLoading ? (
                <div className="flex justify-center py-4">
                  <LoadingSpinner />
                </div>
              ) : companies.length === 0 ? (
                <div className="text-center py-4 text-slate-500 text-sm">
                  No companies found. The backend may not be running yet.
                </div>
              ) : (
                companies.map((company) => (
                  <button
                    key={company.id}
                    type="button"
                    className={`flex items-center gap-3 p-4 rounded-xl border w-full text-left transition-colors ${
                      selectedCompany?.id === company.id
                        ? 'border-navy-500 bg-navy-800/50'
                        : 'border-navy-800 hover:border-navy-700'
                    }`}
                    onClick={() => selectCompany(company.id)}
                  >
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                        selectedCompany?.id === company.id
                          ? 'border-navy-400 bg-navy-400'
                          : 'border-navy-600'
                      }`}
                    >
                      {selectedCompany?.id === company.id && (
                        <CheckIcon className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <div>
                      <p className="text-slate-200 font-medium">{company.name}</p>
                      <p className="text-slate-500 text-sm">
                        {company.industry} {company.is_demo && '• Demo workspace'}
                      </p>
                    </div>
                  </button>
                ))
              )}
            </div>
          )}

          {currentStep.bullets.length > 0 && (
            <ul className="space-y-2 mb-6">
              {currentStep.bullets.map((b, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-slate-400">
                  <CheckIcon className="w-4 h-4 text-navy-400 flex-shrink-0" />
                  {b}
                </li>
              ))}
            </ul>
          )}

          <div className="flex items-center justify-between">
            <button
              type="button"
              className="text-slate-500 hover:text-slate-300 text-sm transition-colors"
              onClick={() => navigate('/dashboard')}
            >
              Skip
            </button>
            <button
              type="button"
              className="btn-primary flex items-center gap-2"
              onClick={() =>
                step < steps.length - 1 ? setStep((s) => s + 1) : navigate('/dashboard')
              }
            >
              {step < steps.length - 1 ? 'Continue' : 'Enter Dashboard'}
              <ArrowRightIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

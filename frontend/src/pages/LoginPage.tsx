import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { login } from '@/api/auth'
import { useAuth } from '@/store/auth'
import { NetworkIcon, EyeIcon, EyeOffIcon, CopyIcon } from 'lucide-react'
import toast from 'react-hot-toast'

const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(1, 'Password required'),
})
type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const { login: storeLogin } = useAuth()
  const navigate = useNavigate()
  const [showPw, setShowPw] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    setIsLoading(true)
    try {
      const res = await login(data.email, data.password)
      await storeLogin(res.access_token)
      const firstVisit = !localStorage.getItem('nexustrace_visited')
      if (firstVisit) {
        localStorage.setItem('nexustrace_visited', 'true')
        navigate('/onboarding')
      } else {
        navigate('/dashboard')
      }
    } catch {
      toast.error('Invalid credentials. Try the demo credentials below.')
    } finally {
      setIsLoading(false)
    }
  }

  const fillDemo = () => {
    setValue('email', 'admin@nexustrace.demo')
    setValue('password', 'demo1234!')
    toast.success('Demo credentials filled!')
  }

  return (
    <div className="min-h-screen bg-navy-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 bg-navy-500 rounded-xl flex items-center justify-center shadow-lg shadow-navy-500/20">
            <NetworkIcon className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">NEXUSTRACE AI</h1>
            <p className="text-navy-400 text-sm">Supply Chain Intelligence</p>
          </div>
        </div>

        <div className="card mb-6">
          <div className="flex items-center justify-between mb-3">
            <p className="text-amber-400 text-sm font-semibold">🎯 Demo Access</p>
            <button
              type="button"
              className="flex items-center gap-1 text-xs text-navy-400 hover:text-slate-200 transition-colors"
              onClick={fillDemo}
            >
              <CopyIcon className="w-3 h-3" />
              Auto-fill
            </button>
          </div>
          <div className="space-y-1 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-500">Email:</span>
              <span className="text-slate-300">admin@nexustrace.demo</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Password:</span>
              <span className="text-slate-300">demo1234!</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-slate-100 mb-6">Sign In</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="label">Email Address</label>
              <input
                {...register('email')}
                type="email"
                className="input"
                placeholder="you@company.com"
                autoComplete="email"
              />
              {errors.email && (
                <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>
              )}
            </div>
            <div>
              <label className="label">Password</label>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPw ? 'text' : 'password'}
                  className="input pr-10"
                  placeholder="••••••••"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                  onClick={() => setShowPw((s) => !s)}
                >
                  {showPw ? <EyeOffIcon className="w-4 h-4" /> : <EyeIcon className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>
              )}
            </div>
            <button type="submit" className="btn-primary w-full" disabled={isLoading}>
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>

        <p className="text-center text-slate-600 text-xs mt-6">
          Enterprise Supply Chain Intelligence Platform • v1.0.0
        </p>
      </div>
    </div>
  )
}

import { apiClient } from './client'
import type {
  AffectedProduct,
  AffectedSupplier,
  DependencyPath,
  Evidence,
  RiskFinding,
} from '@/types'

type FindingResponse = Omit<
  RiskFinding,
  | 'affected_suppliers_json'
  | 'affected_products_json'
  | 'dependency_paths_json'
  | 'evidence_json'
> & {
  affected_suppliers_json?: string | AffectedSupplier[] | null
  affected_products_json?: string | AffectedProduct[] | null
  dependency_paths_json?: string | DependencyPath[] | Record<string, string[][]> | null
  evidence_json?: string | Evidence[] | Record<string, number> | null
}

const parseArray = <T>(value: string | T[] | null | undefined): T[] | undefined => {
  if (!value) return undefined
  if (Array.isArray(value)) return value as T[]

  const parsed: unknown = JSON.parse(value)
  if (!Array.isArray(parsed)) {
    throw new Error('Expected an array in risk finding JSON data')
  }
  return parsed as T[]
}

const parseDependencyPaths = (
  value: FindingResponse['dependency_paths_json']
): DependencyPath[] | undefined => {
  if (!value) return undefined
  const parsed: unknown = typeof value === 'string' ? JSON.parse(value) : value
  if (Array.isArray(parsed)) {
    return parsed.map((item) =>
      Array.isArray(item) ? { path: item } : (item as DependencyPath)
    )
  }
  if (typeof parsed === 'object' && parsed !== null) {
    return Object.values(parsed as Record<string, string[][]>).flatMap((paths) =>
      paths.map((path: string[]) => ({ path }))
    )
  }
  throw new Error('Expected dependency paths to be an array or object')
}

const parseEvidence = (value: FindingResponse['evidence_json']): Evidence[] | undefined => {
  if (!value) return undefined
  const parsed: unknown = typeof value === 'string' ? JSON.parse(value) : value
  if (Array.isArray(parsed)) return parsed as Evidence[]
  if (typeof parsed === 'object' && parsed !== null) {
    return Object.entries(parsed).map(([type, value]) => ({
      type,
      description: `${type}: ${value}`,
    }))
  }
  throw new Error('Expected evidence to be an array or object')
}

const normalizeFinding = (finding: FindingResponse): RiskFinding => ({
  ...finding,
  affected_suppliers_json: parseArray<string | AffectedSupplier>(
    finding.affected_suppliers_json
  )?.map((supplier) =>
    typeof supplier === 'string' ? { id: supplier, name: supplier } : supplier
  ),
  affected_products_json: parseArray<string | AffectedProduct>(
    finding.affected_products_json
  )?.map((product) =>
    typeof product === 'string' ? { id: product, name: product } : product
  ),
  dependency_paths_json: parseDependencyPaths(finding.dependency_paths_json),
  evidence_json: parseEvidence(finding.evidence_json),
})

export const analyzeHiddenDependencies = async (companyId: string) => {
  const res = await apiClient.post<FindingResponse[]>('/dependencies/analyze', null, {
    params: { company_id: companyId },
  })
  return res.data.map(normalizeFinding)
}

export const getFindings = async (companyId: string, params?: Record<string, string>) => {
  const res = await apiClient.get<FindingResponse[]>('/dependencies/findings', {
    params: { company_id: companyId, ...params },
  })
  return res.data.map(normalizeFinding)
}

export const getFinding = async (id: string) => {
  const res = await apiClient.get<FindingResponse>(`/dependencies/findings/${id}`)
  return normalizeFinding(res.data)
}

export const updateFindingStatus = async (
  id: string,
  status: RiskFinding['status'],
  notes?: string
) => {
  const res = await apiClient.put<RiskFinding>(`/dependencies/findings/${id}`, {
    status,
    analyst_notes: notes,
  })
  return res.data
}

import { useState } from 'react'
import { ChevronUpIcon, ChevronDownIcon, SearchIcon } from 'lucide-react'
import LoadingSpinner from './LoadingSpinner'
import EmptyState from './EmptyState'
import type { ColumnDef } from '@/types'
import clsx from 'clsx'

interface Props<T extends Record<string, unknown>> {
  data: T[]
  columns: ColumnDef<T>[]
  isLoading?: boolean
  onRowClick?: (row: T) => void
  searchable?: boolean
  pageSize?: number
  emptyMessage?: string
  keyField?: keyof T
}

export default function DataTable<T extends Record<string, unknown>>({
  data,
  columns,
  isLoading,
  onRowClick,
  searchable = true,
  pageSize = 20,
  emptyMessage,
  keyField,
}: Props<T>) {
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')
  const [page, setPage] = useState(0)

  const filtered = data.filter(
    (row) =>
      !search ||
      Object.values(row).some((v) =>
        String(v).toLowerCase().includes(search.toLowerCase())
      )
  )

  const sorted = sortKey
    ? [...filtered].sort((a, b) => {
        const av = String(a[sortKey] ?? '')
        const bv = String(b[sortKey] ?? '')
        return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av)
      })
    : filtered

  const paged = sorted.slice(page * pageSize, (page + 1) * pageSize)
  const totalPages = Math.ceil(sorted.length / pageSize)

  const handleSort = (key: string) => {
    if (sortKey === key) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  if (isLoading) return <div className="flex justify-center py-12"><LoadingSpinner /></div>

  return (
    <div>
      {searchable && (
        <div className="relative mb-4">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            className="input pl-9"
            placeholder="Search..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(0)
            }}
          />
        </div>
      )}
      <div className="overflow-x-auto rounded-xl border border-navy-800">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-navy-800 bg-navy-900/50">
              {columns.map((col) => (
                <th
                  key={String(col.key)}
                  className={clsx(
                    'px-4 py-3 text-left text-slate-400 font-medium whitespace-nowrap',
                    col.sortable && 'cursor-pointer hover:text-slate-200 select-none',
                    col.className
                  )}
                  onClick={() => col.sortable && handleSort(String(col.key))}
                >
                  <div className="flex items-center gap-1">
                    {col.header}
                    {col.sortable && sortKey === String(col.key) ? (
                      sortDir === 'asc' ? (
                        <ChevronUpIcon className="w-3 h-3" />
                      ) : (
                        <ChevronDownIcon className="w-3 h-3" />
                      )
                    ) : null}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paged.length === 0 ? (
              <tr>
                <td colSpan={columns.length}>
                  <EmptyState title={emptyMessage ?? 'No records found'} />
                </td>
              </tr>
            ) : (
              paged.map((row, i) => (
                <tr
                  key={keyField ? String(row[keyField]) : i}
                  className={clsx(
                    'border-b border-navy-800/50 hover:bg-navy-800/30 transition-colors',
                    onRowClick && 'cursor-pointer'
                  )}
                  onClick={() => onRowClick?.(row)}
                >
                  {columns.map((col) => (
                    <td
                      key={String(col.key)}
                      className={clsx('px-4 py-3 text-slate-300', col.className)}
                    >
                      {col.render
                        ? col.render(row[col.key as keyof T], row)
                        : String(row[col.key as keyof T] ?? '—')}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 text-sm text-slate-400">
          <span>
            Showing {page * pageSize + 1}–{Math.min((page + 1) * pageSize, sorted.length)} of{' '}
            {sorted.length}
          </span>
          <div className="flex gap-2">
            <button
              className="btn-secondary py-1 px-3"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </button>
            <button
              className="btn-secondary py-1 px-3"
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

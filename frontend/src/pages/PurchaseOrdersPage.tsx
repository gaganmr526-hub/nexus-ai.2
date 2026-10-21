import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useCompany } from '@/hooks/useCompany'
import { getPurchaseOrders, updatePurchaseOrder } from '@/api/procurement'
import type { PurchaseOrder, ColumnDef } from '@/types'
import DemoBanner from '@/components/DemoBanner'
import DataTable from '@/components/DataTable'
import StatusBadge from '@/components/StatusBadge'
import Modal from '@/components/Modal'
import { PrinterIcon } from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function PurchaseOrdersPage() {
  const { selectedCompany } = useCompany()
  const qc = useQueryClient()
  const [selectedOrder, setSelectedOrder] = useState<PurchaseOrder | null>(null)

  const { data: orders = [], isLoading } = useQuery({
    queryKey: ['purchase-orders', selectedCompany?.id],
    queryFn: () => getPurchaseOrders(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<PurchaseOrder> }) =>
      updatePurchaseOrder(id, data),
    onSuccess: () => {
      toast.success('Order updated')
      qc.invalidateQueries({ queryKey: ['purchase-orders', selectedCompany?.id] })
    },
    onError: () => toast.error('Could not update purchase order. Please try again.'),
  })

  const columns: ColumnDef<Record<string, unknown>>[] = [
    {
      key: 'order_number',
      header: 'Order #',
      sortable: true,
      render: (v, r) => (
        <span className="font-mono text-slate-200">
          {String(v)} {r.is_demo ? <span className="demo-badge ml-1">DEMO</span> : null}
        </span>
      ),
    },
    { key: 'supplier_id', header: 'Supplier', render: (v) => <span className="text-slate-300">{String(v).slice(0, 12)}…</span> },
    {
      key: 'total_amount',
      header: 'Total',
      sortable: true,
      render: (v, r) => (
        <span className="font-mono">${Number(v).toLocaleString()} {String(r.currency)}</span>
      ),
    },
    { key: 'status', header: 'Status', sortable: true, render: (v) => <StatusBadge status={String(v)} /> },
    {
      key: 'delivery_date',
      header: 'Delivery',
      render: (v) =>
        v ? (
          <span className="text-xs text-slate-400">{format(new Date(String(v)), 'MMM d, yyyy')}</span>
        ) : (
          '—'
        ),
    },
    {
      key: 'created_at',
      header: 'Created',
      sortable: true,
      render: (v) => (
        <span className="text-xs text-slate-500">{format(new Date(String(v)), 'MMM d, yyyy')}</span>
      ),
    },
  ]

  const printOrder = (order: PurchaseOrder) => {
    const win = window.open('', '_blank')
    if (!win) return
    win.document.write(`
      <html><head><title>PO ${order.order_number}</title>
      <style>body{font-family:sans-serif;padding:40px;max-width:800px;margin:auto}h1{color:#1e2166}table{width:100%;border-collapse:collapse}td,th{padding:8px;border:1px solid #ccc;text-align:left}.badge{padding:2px 8px;border-radius:12px;font-size:12px}</style>
      </head><body>
      <h1>NEXUSTRACE AI — Purchase Order</h1>
      <hr/>
      <table>
        <tr><th>Order Number</th><td>${order.order_number}</td></tr>
        <tr><th>Status</th><td>${order.status}</td></tr>
        <tr><th>Total Amount</th><td>$${order.total_amount.toLocaleString()} ${order.currency}</td></tr>
        <tr><th>Delivery Date</th><td>${order.delivery_date ?? 'TBD'}</td></tr>
        <tr><th>Created</th><td>${format(new Date(order.created_at), 'MMMM d, yyyy')}</td></tr>
        ${order.is_demo ? '<tr><td colspan="2" style="background:#fef3c7;color:#92400e;font-weight:bold;text-align:center">⚠ SYNTHETIC DEMO DATA — NOT A REAL PURCHASE ORDER</td></tr>' : ''}
      </table>
      </body></html>
    `)
    win.document.close()
    win.print()
  }

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to view purchase orders.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Purchase Orders</h1>
          <p className="text-slate-500 text-sm">{orders.length} orders</p>
        </div>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      <div className="card">
        <DataTable
          data={orders as unknown as Record<string, unknown>[]}
          columns={columns}
          isLoading={isLoading}
          onRowClick={(row) => setSelectedOrder(row as unknown as PurchaseOrder)}
          keyField="id"
        />
      </div>

      <Modal
        isOpen={!!selectedOrder}
        onClose={() => setSelectedOrder(null)}
        title={`Order ${selectedOrder?.order_number ?? ''}`}
        size="md"
      >
        {selectedOrder && (
          <div className="space-y-4">
            {selectedOrder.is_demo && <DemoBanner />}

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="label">Status</p>
                <StatusBadge status={selectedOrder.status} />
              </div>
              <div>
                <p className="label">Total Amount</p>
                <p className="text-slate-200 font-mono">
                  ${selectedOrder.total_amount.toLocaleString()} {selectedOrder.currency}
                </p>
              </div>
              <div>
                <p className="label">Delivery Date</p>
                <p className="text-slate-200">
                  {selectedOrder.delivery_date
                    ? format(new Date(selectedOrder.delivery_date), 'MMM d, yyyy')
                    : 'TBD'}
                </p>
              </div>
              <div>
                <p className="label">Approval</p>
                <p className="text-slate-200">{selectedOrder.approval_status}</p>
              </div>
            </div>

            <div className="flex gap-3 flex-wrap">
              {selectedOrder.status === 'draft' && (
                <button
                  className="btn-secondary text-sm"
                  onClick={() =>
                    updateMutation.mutate({ id: selectedOrder.id, data: { status: 'pending_approval' } })
                  }
                >
                  Submit for Approval
                </button>
              )}
              {selectedOrder.status === 'pending_approval' && (
                <button
                  className="btn-primary text-sm"
                  onClick={() =>
                    updateMutation.mutate({ id: selectedOrder.id, data: { status: 'approved' } })
                  }
                >
                  Approve
                </button>
              )}
              {selectedOrder.status === 'approved' && (
                <button
                  className="btn-primary text-sm"
                  onClick={() =>
                    updateMutation.mutate({ id: selectedOrder.id, data: { status: 'issued' } })
                  }
                >
                  Issue Order
                </button>
              )}
              <button
                className="btn-secondary text-sm flex items-center gap-1"
                onClick={() => printOrder(selectedOrder)}
              >
                <PrinterIcon className="w-4 h-4" /> Print
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

import { describe, expect, it } from 'vitest'
import { outstandingNextAction, outstandingWorkStatus } from './outstandingWork.js'

describe('outstandingWorkStatus', () => {
  it('needs a schedule when balance remains and no slots exist', () => {
    expect(outstandingWorkStatus({ balance_qty: '2000', delivered_qty: '0', schedule_qty_total: '' })).toBe(
      'need_schedule',
    )
  })

  it('is scheduled when slots cover the order', () => {
    expect(
      outstandingWorkStatus({
        balance_qty: '2000',
        delivered_qty: '0',
        schedule_qty_total: '2000',
        schedule_unallocated_qty: '0',
      }),
    ).toBe('scheduled')
  })

  it('is partial schedule when some qty is still unallocated', () => {
    expect(
      outstandingWorkStatus({
        balance_qty: '2000',
        delivered_qty: '0',
        schedule_qty_total: '800',
        schedule_unallocated_qty: '1200',
      }),
    ).toBe('partial_schedule')
  })

  it('tracks partial and completed shipments', () => {
    expect(
      outstandingWorkStatus({
        balance_qty: '500',
        delivered_qty: '1500',
        schedule_qty_total: '2000',
        schedule_unallocated_qty: '0',
      }),
    ).toBe('partial_ship')
    expect(
      outstandingWorkStatus({
        balance_qty: '0',
        delivered_qty: '2000',
        schedule_qty_total: '2000',
        schedule_unallocated_qty: '0',
      }),
    ).toBe('shipped')
  })
})

describe('outstandingNextAction', () => {
  it('schedules first, then ships', () => {
    expect(outstandingNextAction({ balance_qty: '2000', delivered_qty: '0' })).toBe('schedule')
    expect(
      outstandingNextAction({
        balance_qty: '2000',
        delivered_qty: '0',
        schedule_qty_total: '2000',
        schedule_unallocated_qty: '0',
      }),
    ).toBe('ship')
    expect(outstandingNextAction({ balance_qty: '0', delivered_qty: '2000' })).toBe('done')
  })
})

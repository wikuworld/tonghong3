import { describe, expect, it } from 'vitest'
import {
  extractPlanSlots,
  firstPlannedDeliveryDate,
  mostCommonPlannedDeliveryDate,
  outstandingNextAction,
  outstandingWorkStatus,
} from './outstandingWork.js'

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

describe('firstPlannedDeliveryDate', () => {
  it('uses plan_slots only; ignores Reply ETD and delivery_N actual', () => {
    expect(
      firstPlannedDeliveryDate({
        plan_slots: [{ sequence_no: 1, qty: '100', delivery_date: '2026-09-22' }],
        delivery_1_date: '2026-09-14',
        line_etd: '2026-09-30',
      }),
    ).toBe('2026-09-22')
    expect(
      firstPlannedDeliveryDate({
        delivery_1_date: '2026-09-22',
        line_etd: '2026-09-30',
      }),
    ).toBe(null)
    expect(firstPlannedDeliveryDate({ line_etd: '2026-09-30T00:00:00' })).toBe(null)
    expect(firstPlannedDeliveryDate({})).toBe(null)
  })
})

describe('extractPlanSlots', () => {
  it('reads only the first plan_slot by default', () => {
    expect(
      extractPlanSlots({
        plan_slots: [
          { sequence_no: 1, qty: '100', delivery_date: '2026-09-22' },
          { sequence_no: 2, qty: '50', delivery_date: '2026-09-25' },
        ],
        delivery_1_date: '2026-09-14',
      }),
    ).toEqual([{ sequence_no: 1, qty: '100', delivery_date: '2026-09-22' }])
  })

  it('does not fall back to delivery_N actual columns', () => {
    expect(
      extractPlanSlots({
        delivery_1_qty: '100',
        delivery_1_date: '2026-09-14',
      }),
    ).toEqual([])
  })
})

describe('mostCommonPlannedDeliveryDate', () => {
  it('picks the most frequent planned date from plan_slots', () => {
    expect(
      mostCommonPlannedDeliveryDate([
        { plan_slots: [{ delivery_date: '2026-09-22' }] },
        { plan_slots: [{ delivery_date: '2026-09-22' }] },
        { plan_slots: [{ delivery_date: '2026-09-25' }] },
      ]),
    ).toBe('2026-09-22')
  })
})

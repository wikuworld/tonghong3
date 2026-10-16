import { describe, expect, it } from 'vitest'
import { buildMrpRencanaPrintHtml } from './mrpRencanaPrint.js'

const labels = {
  title: 'Cetak rencana',
  kodeRpi: 'KODE RPI',
  customer: 'CUSTOMER',
  emboss: 'EMBOSS',
  color: 'COLOR',
  thickness: 'THICKNESS',
  qty: 'QTY',
  cs: 'CS',
  backer: 'BACKER',
  schedule: 'SCHEDULE',
  remarks: 'REMARKS',
}

describe('buildMrpRencanaPrintHtml', () => {
  it('prints excel column order with thickness and only typed qty, schedule, remarks', () => {
    const html = buildMrpRencanaPrintHtml(
      {
        rencana: {
          nama_rencana: 'Rencana Rabu',
          kode_rencana: 'RP-1',
          tanggal_rencana: '2026-10-14',
        },
        items: [
          {
            kode_rencana_item: 'RPI-9',
            emboss: 'PLAIN',
            nama_customer: 'long rich',
            color: 'CAMBRIDGE',
            color_swatch: '004-23-16',
            backer: 'A',
            kode_kulit: 'KL-1',
            print_qty: 120,
            print_schedule: 'SHIFT 1',
            print_remarks: 'cek tepi',
            total_qty_so: 999,
            schedule_text: 'SO-999',
            keterangan: 'catatan alokasi',
            thickness: '1.2',
          },
          {
            kode_rencana_item: 'RPI-10',
            emboss: 'SUEDE',
            nama_customer: 'acme',
            color: 'BLACK',
            color_swatch: '001',
            backer: 'B',
            kode_kulit: '',
            print_qty: null,
            print_schedule: '',
            print_remarks: '',
            total_qty_so: 50,
            schedule_text: 'SO-50',
            keterangan: 'jangan cetak',
            thickness: '1.4',
          },
        ],
      },
      labels,
    )

    const header = html.slice(html.indexOf('<thead>'), html.indexOf('</thead>'))
    expect(header).toContain('KODE RPI')
    expect(header.indexOf('KODE RPI')).toBeLessThan(header.indexOf('CUSTOMER'))
    expect(header.indexOf('CUSTOMER')).toBeLessThan(header.indexOf('EMBOSS'))
    expect(header.indexOf('EMBOSS')).toBeLessThan(header.indexOf('COLOR'))
    expect(header.indexOf('COLOR')).toBeLessThan(header.indexOf('THICKNESS'))
    expect(header.indexOf('THICKNESS')).toBeLessThan(header.indexOf('QTY'))
    expect(header.indexOf('QTY')).toBeLessThan(header.indexOf('CS'))
    expect(header.indexOf('CS')).toBeLessThan(header.indexOf('BACKER'))
    expect(header.indexOf('BACKER')).toBeLessThan(header.indexOf('SCHEDULE'))
    expect(header.indexOf('SCHEDULE')).toBeLessThan(header.indexOf('REMARKS'))

    expect(html).toContain('RPI-9')
    expect(html).toContain('LONG RICH')
    expect(html).toContain('>120<')
    expect(html).toContain('SHIFT 1')
    expect(html).toContain('cek tepi')
    expect(html).toContain('1.2')
    expect(html).toContain('1.4')
    expect(html).toContain('RABU')
    expect(html).toContain('14-Oct')
    expect(html).toContain('TTD')
    expect(html).toContain('PKULIT')
    expect(html).toContain('WARNA')
    expect(html).toContain('MPU')

    expect(html).not.toContain('Nama Rencana Produksi')
    expect(html).not.toContain('No. RP')
    expect(html).not.toContain('KL-1')
    expect(html).not.toContain('999')
    expect(html).not.toContain('SO-999')
    expect(html).not.toContain('SO-50')
    expect(html).not.toContain('SUHP')
    expect(html).not.toContain('catatan alokasi')
    expect(html).not.toContain('jangan cetak')
  })
})

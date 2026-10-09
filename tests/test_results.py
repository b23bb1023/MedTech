"""Consistency checks for the public aggregate research record."""
import json
import math
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZipFile

NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
ROOT=Path(__file__).resolve().parents[1]

def xlsx_cells(sheet_name):
    """Read exported numeric values without a spreadsheet-writing dependency."""
    with ZipFile(ROOT/'results/medtech-results.xlsx') as z:
        workbook=ET.fromstring(z.read('xl/workbook.xml'))
        sheets=workbook.find('s:sheets',NS)
        index=next(i for i,s in enumerate(sheets,1) if s.attrib['name']==sheet_name)
        sheet=ET.fromstring(z.read(f'xl/worksheets/sheet{index}.xml'))
        cells={}
        for c in sheet.findall('.//s:c',NS):
            v=c.find('s:v',NS)
            if v is not None and c.attrib.get('t','n')=='n':cells[c.attrib['r']]=float(v.text)
        return cells

class ResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results=json.loads((ROOT/'results/recorded-results.json').read_text())
        cls.matrices=json.loads((ROOT/'results/confusion-matrices.json').read_text())['matrices']

    def test_every_matrix_total_and_diagonal_agree_with_saved_accuracy(self):
        expected={}
        for x in self.results['joint_architecture_runs']:expected[x['run_id']+':joint TNM']=x['metrics']['Acc']
        for x in self.results['tn_multitask_runs']:
            for target in ['T','N']:expected[x['run_id']+':'+target]=x[target]['Acc']
        for x in self.results['holdout_classification']:
            ident=f"classical-21-{x['dataset']}-{x['target']}-{x['model']}:{x['target']}"
            expected[ident]=x['acc']
        for m in self.matrices:
            counts=m['counts'];total=sum(map(sum,counts));diagonal=sum(row[i] for i,row in enumerate(counts))
            self.assertEqual(total,m['sample_count'])
            self.assertTrue(all(isinstance(v,int) and v>=0 for row in counts for v in row))
            self.assertAlmostEqual(diagonal/total,m['accuracy_from_counts'],places=12)
            if m['id'] in expected:self.assertAlmostEqual(diagonal/total,expected[m['id']],delta=0.000051)
        self.assertEqual(len(expected),72)
        self.assertEqual(len(self.matrices),112)
        self.assertEqual(len({m['id'] for m in self.matrices}),112)

    def test_original_workbook_numeric_values_survive_export(self):
        ledger=json.loads((ROOT/'results/workbook-metric-ledger.json').read_text())['numeric_cells']
        values=xlsx_cells('Metric ledger')
        self.assertEqual(len(ledger),1323)
        self.assertEqual(len({x['source_cell'] for x in ledger}),1323)
        for i,x in enumerate(ledger,7):
            self.assertTrue(math.isclose(values[f'B{i}'],x['value'],rel_tol=1e-14,abs_tol=1e-15),x['source_cell'])

    def test_phase2_metrics_are_retained_without_guessing_source_labels(self):
        records=self.results['phase2_unlocated_runs']
        self.assertEqual(len(records),12)
        self.assertTrue(all(x['source_setting']=='VALUE' for x in records))
        self.assertTrue(all(len(x['metrics'])==7 and all(v is not None for v in x['metrics'].values()) for x in records))
        self.assertEqual(len(self.results['workbook_tn_runs']),9)

    def test_confirmed_mse_is_distinct_from_unconfirmed_reported_rmse(self):
        early=self.results['early_joint_runs']
        confirmed=[x for x in early if 'Test pain MSE' in x['metrics']]
        self.assertEqual(len(confirmed),4)
        self.assertTrue(all('Test pain RMSE' not in x['metrics'] for x in confirmed))
        self.assertEqual(sum('Pain RMSE' in x['metrics'] for x in early),2)

    def test_missing_cv_dispersion_is_not_replaced_with_zero(self):
        self.assertTrue(all(x['bal_acc_std'] is None for x in self.results['cv_classification']))
        self.assertFalse(any(k.startswith('H') for k in xlsx_cells('CV classification')))

if __name__=='__main__':unittest.main()

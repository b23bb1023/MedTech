"""Synthetic checks for portable research helpers; no clinical fitting."""
import ast
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.base import clone, is_classifier
from sklearn.linear_model import Ridge
from scripts.check_notebook import check, output_digest

ROOT=Path(__file__).resolve().parents[1]

def helpers(cell_id):
    n=json.loads((ROOT/'notebooks/04_classical_ordinal_pca.ipynb').read_text())
    source=''.join(next(c['source'] for c in n['cells'] if c['id']==cell_id))
    tree=ast.parse(source)
    nodes=[node for node in tree.body if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.ClassDef))]
    module=ast.Module(body=nodes,type_ignores=[])
    namespace={'RANDOM_STATE':42,'TEST_SIZE':.2}
    exec(compile(module,'research-helper','exec'),namespace)
    return namespace

class ResearchNotebookTests(unittest.TestCase):
    def test_all_reviewed_notebooks_pass(self):
        with redirect_stdout(io.StringIO()):
            for path in (ROOT/'notebooks').glob('*.ipynb'):self.assertEqual(check(path),0)

    def test_changed_or_new_output_is_rejected(self):
        n=json.loads((ROOT/'notebooks/03_tn_multitask.ipynb').read_text())
        cell=next(c for c in n['cells'] if c.get('outputs'))
        digest=output_digest(cell['outputs'])
        cell['outputs'][0]['text'].append('Unreviewed record preview\n')
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            path=Path(tmp)/'modified.ipynb';path.write_text(json.dumps(n))
            with patch('scripts.check_notebook.reviewed_outputs',return_value={cell['id']:digest}),redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                self.assertEqual(check(path),1)

    def test_site_encoding_preserves_filtered_index(self):
        n=json.loads((ROOT/'notebooks/03_tn_multitask.ipynb').read_text())
        src=''.join(next(c['source'] for c in n['cells'] if c['id']=='research-016'))
        from sklearn.preprocessing import OneHotEncoder
        df=pd.DataFrame({'Site':['a','b'],'Pain':[.2,.7]},index=[2,8])
        ns={'df':df,'OneHotEncoder':OneHotEncoder}
        with redirect_stdout(io.StringIO()):exec(compile(src,'site-encoding','exec'),ns)
        self.assertEqual(ns['df'].index.tolist(),[2,8])
        self.assertEqual(len(ns['df']),2)
        self.assertFalse(ns['df'].filter(like='Site_').isna().any().any())

    def test_ordinal_wrapper_is_cloneable_classifier(self):
        for cell in ['research-021','research-022']:
            with self.subTest(cell=cell):
                ns=helpers(cell);cls=ns['OrdinalClassifier']
                model=clone(cls());self.assertTrue(is_classifier(model))
                X=np.arange(90).reshape(30,3)/90;y=np.repeat([0,1,2],10)
                model.fit(X,y);probs=model.predict_proba(X)
                self.assertEqual(probs.shape,(30,3))
                np.testing.assert_allclose(probs.sum(axis=1),1)
                self.assertTrue((probs>=0).all())

    def test_future_pca_runs_keep_decoding_modes_distinct(self):
        ns=helpers('research-022');pca=helpers('research-023')
        pca.update(ns)
        pca['get_latent_regressors']=lambda:{'Ridge-round':Ridge(),'Ridge-threshold':Ridge()}
        rng=np.random.default_rng(42);y=np.repeat(np.arange(4),20)
        X=y[:,None]+rng.normal(0,.25,(80,6))
        with redirect_stdout(io.StringIO()):
            result=pca['run_pca_cv'](X,y,'all','N','latent',3,n_splits=2,n_repeats=1)
        self.assertEqual(set(result['setting']),{'pca_latent_3_round','pca_latent_3_threshold'})

if __name__=='__main__':unittest.main()

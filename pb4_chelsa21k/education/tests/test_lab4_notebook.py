import ast
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

NOTEBOOK = Path(__file__).resolve().parents[1] / 'ECO_GEOGRAPHY_LAB4_GLOBAL_120KA_FIXED_20261106.ipynb'


def cells():
    nb = json.loads(NOTEBOOK.read_text())
    return {c.get('metadata', {}).get('id', c.get('id')): ''.join(c['source']) for c in nb['cells']}


def font_namespace():
    tree = ast.parse(cells()['pb4-colab-002'])
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_configure_korean_plotting']
    ns = {}
    exec(compile(ast.Module(body=body, type_ignores=[]), 'font_setup', 'exec'), ns)
    return ns


def basin_namespace():
    ns = font_namespace()
    if '_configure_korean_plotting' in ns:
        ns['_configure_korean_plotting']()
    tree = ast.parse(cells()['pb4-virtual-basin-config'])
    # Execute real controls and geometry without displaying the interactive form.
    body = []
    for n in tree.body:
        if isinstance(n, ast.For):
            break
        body.append(n)
    exec(compile(ast.Module(body=body, type_ignores=[]), 'basin_setup', 'exec'), ns)
    return ns


def test_default_restores_previous_twenty_by_twenty_basin():
    ns = basin_namespace()
    dem, mask, outlet = ns['_build_virtual_basin']()
    assert dem.shape == (20, 20)
    assert mask.sum() == 234
    assert np.isfinite(dem[mask]).all()
    assert mask[outlet] and dem[outlet] == 350.0
    assert mask.sum() * ns['basin_cellsize_widget'].value ** 2 == 93600


def test_largest_allowed_basin_stays_below_four_times_default_cells():
    ns = basin_namespace()
    ns['basin_area_widget'].value = ns['basin_area_widget'].max
    dem, mask, _ = ns['_build_virtual_basin']()
    assert max(dem.shape) <= 40
    assert 234 < mask.sum() <= 1000
    assert mask.sum() * ns['basin_cellsize_widget'].value ** 2 <= 375000


def test_fine_grid_rejects_expensive_area_instead_of_silently_resizing():
    ns = basin_namespace()
    ns['basin_cellsize_widget'].value = 5.0
    with pytest.raises(ValueError):
        ns['_build_virtual_basin']()


def test_coarse_grid_cannot_exceed_physical_area_limit():
    ns = basin_namespace()
    ns['basin_cellsize_widget'].value = ns['basin_cellsize_widget'].max
    with pytest.raises(ValueError):
        ns['_build_virtual_basin']()


def test_korean_labels_render_after_matplotlib_defaults_reset(tmp_path):
    ns = font_namespace()
    configure = ns.get('_configure_korean_plotting')
    assert configure is not None, 'Korean font configuration must be reusable by plotting cells'
    plt.rcdefaults()
    configure()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        fig, ax = plt.subplots()
        ax.plot([0, 1], [1, -1], label='동적 모델 · 혼효림')
        ax.set_title('가상유역 · 유출구 · 생물군계')
        ax.set_xlabel('거리 (m)')
        ax.set_ylabel('토심 (m)')
        ax.legend()
        fig.colorbar(ax.imshow(np.array([[0, 1], [1, 0]])), ax=ax, label='고도 (m)')
        fig.savefig(tmp_path / 'korean_labels.png')
        plt.close(fig)
    assert not [str(w.message) for w in caught if 'Glyph' in str(w.message)]


def test_scenario_starts_with_valid_climate_place_and_updates_zone():
    ns = {
        'climate_places': pd.DataFrame([
            {'koppen_reference_0ka':'Dwa', 'koppen_name':'Cold', 'place_label':'서울', 'representative_id':'KR_SEOUL'},
            {'koppen_reference_0ka':'Af', 'koppen_name':'Tropical', 'place_label':'아마존', 'representative_id':'BR_AMAZON'},
        ]),
        'climate_types':['Dwa','Af'], '_KOPPEN_KO':{}, '_KOPPEN_SUBTYPE':{},
    }
    tree = ast.parse(cells()['pb4-colab-006'])
    # No notebook display is needed to exercise the real dropdown observers.
    tree.body = [n for n in tree.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'display')]
    exec(compile(tree, 'scenario_controls', 'exec'), ns)
    for sc in ns['scenario_controls']:
        assert sc['representative'].value == 'KR_SEOUL'
        sc['koppen'].value = 'Af'
        assert sc['representative'].value == 'BR_AMAZON'

import sys
from pathlib import Path

# ensure workspace root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

print('Workspace root:', ROOT)

# Import controller base and material editor controller
import importlib.util
from importlib.machinery import SourceFileLoader

# Load ControllerBase by path to avoid package-level imports
base_path = ROOT / 'src' / 'core' / 'controller_base.py'
loader = SourceFileLoader('controller_base_mod', str(base_path))
spec = importlib.util.spec_from_loader(loader.name, loader)
module_cb = importlib.util.module_from_spec(spec)
loader.exec_module(module_cb)
ControllerBase = module_cb.ControllerBase
# insert into sys.modules so other modules can import it by package name
sys.modules['src.core.controller_base'] = module_cb

# Load MaterialEditorController by path to avoid importing src.ui.qt package __init__
ctrl_path = ROOT / 'src' / 'ui' / 'qt' / 'material_editor' / 'controller.py'
loader2 = SourceFileLoader('material_editor_ctrl_mod', str(ctrl_path))
spec2 = importlib.util.spec_from_loader(loader2.name, loader2)
module_ctrl = importlib.util.module_from_spec(spec2)
# Before loading controller, load its logic dependencies to avoid package __init__ imports
repo_path = ROOT / 'src' / 'ui' / 'qt' / 'material_editor' / 'logic' / 'material_repository.py'
loader_repo = SourceFileLoader('material_repo_mod', str(repo_path))
spec_repo = importlib.util.spec_from_loader(loader_repo.name, loader_repo)
module_repo = importlib.util.module_from_spec(spec_repo)
loader_repo.exec_module(module_repo)
sys.modules['src.ui.qt.material_editor.logic.material_repository'] = module_repo

export_path = ROOT / 'src' / 'ui' / 'qt' / 'material_editor' / 'logic' / 'material_export_logic.py'
loader_export = SourceFileLoader('material_export_mod', str(export_path))
spec_export = importlib.util.spec_from_loader(loader_export.name, loader_export)
module_export = importlib.util.module_from_spec(spec_export)
loader_export.exec_module(module_export)
sys.modules['src.ui.qt.material_editor.logic.material_export_logic'] = module_export

loader2.exec_module(module_ctrl)
MaterialEditorController = module_ctrl.MaterialEditorController

print('Imported ControllerBase and MaterialEditorController successfully (via SourceFileLoader)')

c = ControllerBase()
mc = MaterialEditorController()
print('Controller instances created:', isinstance(c, ControllerBase), isinstance(mc, MaterialEditorController))

import traceback

def main():
    try:
        import importlib
        m = importlib.import_module('gui.materials_gui')
        print('Imported gui.materials_gui')
        # run the GUI app (blocks)
        m.run_app()
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    main()

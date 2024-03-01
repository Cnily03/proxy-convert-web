def _closure():
    import os
    import importlib.util
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    for fn in os.listdir(cur_dir):
        fp = os.path.join(cur_dir, fn)
        if os.path.isfile(fp) and fn.endswith('.py') and not fn.startswith('_'):
            module_name = fn[:-3]
            spec = importlib.util.spec_from_file_location(module_name, fp)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)


_closure()


globals().update(__import__('pulib.utils', fromlist=['SUB_FUNCS']).SUB_FUNCS)

import os
from json import load as json_load

class Translator:
    def __init__(self):
        self._data = {}
        self.k = None
        self._base_path = os.path.dirname(os.path.abspath(__file__))
        
        try:
            from . import keys
            self.k = keys.K
        except ImportError:
            pass

    def load(self):
        """ Load all JSON files in the lang directory. Each file should be named with the language code (e.g., en.json, es.json) and contain a nested structure of keys and values for translations. """

        for filename in os.listdir(self._base_path):
            if filename.endswith(".json"):
                lang_code = filename[:-5]
                with open(os.path.join(self._base_path, filename), "r", encoding="utf-8") as f:
                    self._data[lang_code] = json_load(f)

    def generate_keys(self):
        """ Generate a keys.py file based on the structure of the loaded JSON files. This is used for IDE autocomplete (IntelliSense). """

        self.load()
        base_lang = "es" if "es" in self._data else list(self._data.keys())[0]
        data = self._data[base_lang]

        lines = [
            "# AUTO-GENERATED FILE - DO NOT EDIT MANUALLY",
            "# This file is used for IDE autocomplete (IntelliSense)",
            "class K:"
        ]

        def walk(d, path, level):
            indent = "    " * level
            
            if isinstance(d, dict):
                for key, value in d.items():
                    clean_name = key.lstrip("_")
                    full_path = f"{path}.{key}" if path else key
                    
                    if isinstance(value, (dict, list)):
                        lines.append(f"{indent}class {clean_name}:")
                        lines.append(f'{indent}    all = "{full_path}"')
                        walk(value, full_path, level + 1)
                    else:
                        lines.append(f'{indent}{clean_name} = "{full_path}"')
            
            elif isinstance(d, list):
                lines.append(f'{indent}all = "{path}"')
                
                for i, value in enumerate(d):
                    index_name = f"_{i}"
                    full_path = f"{path}.{i}"
                    
                    if isinstance(value, (dict, list)):
                        lines.append(f"{indent}class {index_name}:")
                        lines.append(f'{indent}    all = "{full_path}"')
                        walk(value, full_path, level + 1)
                    else:
                        lines.append(f'{indent}{index_name} = "{full_path}"')

        walk(data, "", 1)

        with open(os.path.join(self._base_path, "keys.py"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        return True

    def t(self, lang: str, path: str, key: str = None, **kwargs) -> str:
        """
        Translate a string based on the language and path provided.
        'key' allows accessing a dynamic sub-property (e.g., description['general']).
        """
        
        if not isinstance(path, str):
            path = getattr(path, "all", str(path))
        
        if not self._data:
            self.load()

        keys = path.split('.')
        res = self._data.get(lang, {})

        for k in keys:
            if isinstance(res, dict):
                res = res.get(k)
            elif isinstance(res, list):
                try:
                    res = res[int(k)]
                except (ValueError, IndexError):
                    res = None; break
            else:
                res = None; break

        if key and isinstance(res, dict):
            res = res.get(key, res.get("__n_a", f"[{key} not found]"))

        if res is None:
            return f"[{path}?!]"

        if isinstance(res, list):
            res = "\n".join(str(item) for item in res)

        if kwargs and isinstance(res, str):
            try:
                return res.format(**kwargs)
            except KeyError:
                return res

        return res

translator = Translator()

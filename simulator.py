import re

class VHDLSimulator:
    def __init__(self, code):
        self.code = code
        self.concurrent_assignments = []
        self.processes = []
        self._parse_code()

    def _parse_code(self):
        clean_code = re.sub(r"--[^\n]*", "", self.code)
        
        # 1. Concurrentes
        arch_match = re.search(r"\bbegin\b(.*?)\bend\b", clean_code, re.IGNORECASE | re.DOTALL)
        if arch_match:
            body = arch_match.group(1)
            body_no_process = re.sub(r"\bprocess\b.*?\bend\s+process\b", "", body, flags=re.IGNORECASE | re.DOTALL)
            statements = self._split_top_level(body_no_process, ';')
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and '<=' in stmt:
                    parts = stmt.split('<=', 1)
                    dest = parts[0].strip()
                    expr = parts[1].strip()
                    py_expr = self._translate_expr(expr)
                    self.concurrent_assignments.append((dest, py_expr))

        # 2. Process
        process_matches = re.finditer(r"\bprocess\s*\((.*?)\)(.*?)\bend\s+process\b", clean_code, re.IGNORECASE | re.DOTALL)
        for match in process_matches:
            process_body = match.group(2)
            begin_match = re.search(r"\bbegin\b(.*)", process_body, re.IGNORECASE | re.DOTALL)
            if begin_match:
                body = begin_match.group(1)
                py_code = self._translate_process_body(body)
                self.processes.append(py_code)

    def _translate_expr(self, expr):
        expr = re.sub(r'\band\b', '&', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bor\b', '|', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bxor\b', '^', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bnot\b', '~', expr, flags=re.IGNORECASE)
        expr = expr.replace("'", '"')
        # Traducir conversiones de tipo
        expr = re.sub(r'conv_integer\(([^)]+)\)', r'v_to_int(\1)', expr)
        expr = re.sub(r'conv_std_logic_vector\(([^,]+),\s*(\d+)\)', r'v_to_bin(\1, \2)', expr)
        return expr

    def _translate_process_body(self, body):
        lines = []
        indent_level = 0
        
        for line in body.split('\n'):
            line = line.strip()
            if not line: continue
            
            if re.match(r'^end\s+if', line, re.IGNORECASE):
                indent_level = max(0, indent_level - 1)
                continue
                
            if re.match(r'^else', line, re.IGNORECASE):
                lines.append("    " * max(0, indent_level - 1) + "else:")
                continue
                
            elif_match = re.match(r'^elsif\s+(.*?)\s+then', line, re.IGNORECASE)
            if elif_match:
                cond = elif_match.group(1).strip()
                cond = re.sub(r'\band\b', '&', cond, flags=re.IGNORECASE)
                cond = re.sub(r'\bor\b', '|', cond, flags=re.IGNORECASE)
                cond = re.sub(r'\bxor\b', '^', cond, flags=re.IGNORECASE)
                cond = re.sub(r'\bnot\b', '~', cond, flags=re.IGNORECASE)
                cond = cond.replace('=', '==').replace('====', '==')
                cond = cond.replace("'", '"')
                lines.append("    " * max(0, indent_level - 1) + f"elif {cond}:")
                continue
                
            if_match = re.match(r'^if\s+(.*?)\s+then', line, re.IGNORECASE)
            if if_match:
                cond = if_match.group(1).strip()
                cond = re.sub(r'\band\b', '&', cond, flags=re.IGNORECASE)
                cond = re.sub(r'\bor\b', '|', cond, flags=re.IGNORECASE)
                cond = re.sub(r'\bxor\b', '^', cond, flags=re.IGNORECASE)
                cond = re.sub(r'\bnot\b', '~', cond, flags=re.IGNORECASE)
                cond = cond.replace('=', '==').replace('====', '==')
                cond = cond.replace("'", '"')
                lines.append("    " * indent_level + f"if {cond}:")
                indent_level += 1
                continue

            assign_match = re.match(r'^(\w+)\s*<=\s*([^;]+);', line, re.IGNORECASE)
            if assign_match:
                dest = assign_match.group(1).strip()
                expr = assign_match.group(2).strip()
                expr = re.sub(r'\band\b', '&', expr, flags=re.IGNORECASE)
                expr = re.sub(r'\bor\b', '|', expr, flags=re.IGNORECASE)
                expr = re.sub(r'\bxor\b', '^', expr, flags=re.IGNORECASE)
                expr = re.sub(r'\bnot\b', '~', expr, flags=re.IGNORECASE)
                expr = expr.replace("'", '"')
                
                # Traducir conversiones de tipo (pasando el ancho del bus)
                expr = re.sub(r'conv_integer\(([^)]+)\)', r'v_to_int(\1)', expr)
                expr = re.sub(r'conv_std_logic_vector\(([^,]+),\s*(\d+)\)', r'v_to_bin(\1, \2)', expr)
                
                lines.append("    " * indent_level + f"{dest} = {expr}")
                continue
                
        return "\n".join(lines)

    @staticmethod
    def _split_top_level(text, sep):
        result, buf, depth = [], [], 0
        for ch in text:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            if ch == sep and depth == 0:
                result.append(''.join(buf))
                buf = []
            else:
                buf.append(ch)
        if buf:
            result.append(''.join(buf))
        return result

    def evaluate(self, t, current_inputs, bus_widths):
        context = {}
        for k, v in current_inputs.items():
            if isinstance(v, int) and k in bus_widths:
                context[k] = format(v, f'0{bus_widths[k]}b')
            else:
                context[k] = str(v)
                
        outputs = {}
        
        # Evaluar concurrentes
        for dest, py_expr in self.concurrent_assignments:
            try:
                val = eval(py_expr, {}, context)
                outputs[dest] = val
                context[dest] = val
            except Exception:
                pass

        # Evaluar procesos
        for py_code in self.processes:
            local_vars = dict(context)
            local_vars['outputs'] = outputs
            
            # Funciones de utilidad para VHDL
            def v_to_int(a):
                if isinstance(a, str):
                    if a in ('0', '1'): return int(a)
                    try: return int(a, 2)
                    except: return 0
                return int(a)

            # FIX: Truncar al ancho del bus
            def v_to_bin(val, width):
                try: 
                    return format(int(val) & ((1 << width) - 1), f'0{width}b')
                except: 
                    return "0" * width

            local_vars['v_to_int'] = v_to_int
            local_vars['v_to_bin'] = v_to_bin
            
            try:
                exec(py_code, {}, local_vars)
                for k in ['s', 'cout', 'suma']: 
                    if k in local_vars:
                        outputs[k] = local_vars[k]
                        context[k] = local_vars[k]
            except Exception as e:
                pass
                    
        return outputs
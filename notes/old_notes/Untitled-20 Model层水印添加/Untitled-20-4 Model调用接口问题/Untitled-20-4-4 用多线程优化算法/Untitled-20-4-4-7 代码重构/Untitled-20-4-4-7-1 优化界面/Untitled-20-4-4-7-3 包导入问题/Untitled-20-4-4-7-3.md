python 运行时系统路径是怎么设置的？
--- R1
Python 运行时系统路径（即模块搜索路径）由 `sys.path` 定义，它决定了 Python 解释器在导入模块时查找的位置。以下是其设置机制和常见配置方法：

---

### **1. `sys.path` 的初始化**

Python 启动时按以下顺序初始化 `sys.path`：

1. **当前脚本所在目录**  
   运行脚本时，脚本所在目录会被添加到 `sys.path` 的第一个位置。若在交互式环境（如 REPL），则为当前工作目录。
2. **环境变量 `PYTHONPATH`**  
   系统会读取环境变量 `PYTHONPATH` 中配置的路径，按顺序添加到 `sys.path`。

3. **标准库目录**  
   Python 安装路径下的标准库目录（如 `lib/python3.x`）会被添加。

4. **第三方库目录**  
   `site-packages` 目录（如 `lib/python3.x/site-packages`），存放通过 `pip` 安装的第三方包。

---

### **2. 查看当前路径**

可以通过打印 `sys.path` 查看当前路径列表：

```python
import sys
print(sys.path)
```

---

### **3. 修改系统路径的方法**

#### **(1) 临时添加路径（代码中动态修改）**

在代码中使用 `sys.path.append()` 或 `sys.path.insert()`：

```python
import sys
sys.path.append('/path/to/your/module')  # 添加到末尾
sys.path.insert(0, '/path/to/priority/module')  # 添加到开头（优先搜索）
```

#### **(2) 配置环境变量 `PYTHONPATH`**

在终端中设置环境变量（临时生效）：

```bash
# Linux/Mac
export PYTHONPATH="/your/path:$PYTHONPATH"

# Windows
set PYTHONPATH=C:\your\path;%PYTHONPATH%
```

若要永久生效，需在系统环境变量配置文件中（如 `~/.bashrc` 或系统环境变量设置）添加上述命令。

#### **(3) 使用 `.pth` 文件**

在 Python 的 `site-packages` 目录中创建 `.pth` 文件，每行写入一个路径：

```text
# 示例：my_paths.pth
/path/to/add1
/path/to/add2
```

Python 启动时会自动加载这些路径。

#### **(4) 通过 `site` 模块**

在代码中使用 `site` 模块添加路径：

```python
import site
site.addsitedir('/path/to/your/module')  # 类似.pth文件，支持递归添加
```

---

### **4. 虚拟环境中的路径**

在虚拟环境（如 `venv`）中，`sys.path` 会优先包含虚拟环境的 `site-packages`，而非全局安装的路径。激活虚拟环境后，路径会自动配置。

---

### **5. 路径优先级**

模块搜索按 `sys.path` 列表顺序进行，**靠前的路径优先级更高**。若存在同名模块，解释器会加载第一个匹配的模块。

---

### **总结**

- 默认路径由脚本位置、`PYTHONPATH`、标准库和第三方库组成。
- 动态修改推荐使用 `sys.path.append()` 或 `sys.path.insert()`。
- 持久化配置建议通过 `PYTHONPATH` 或 `.pth` 文件实现。

遇到模块导入问题时，检查 `sys.path` 是否包含目标模块的路径是首要步骤。

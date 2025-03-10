对 entry 为 dir 的情况，遍历其所有子文件和子文件夹，添加任务：

```python
    def _generate_tasks(self, input_dir: Path, output_dir: Path) -> Iterable[Tuple[Path, Path]]:
        """添加任务生成日志"""
        self._scan_skipped = 0
        for entry in os.scandir(input_dir):
            src_path = Path(entry.path)
            if entry.is_file() and src_path.suffix.lower() in self._SUPPORTED_EXT:
                dest_path = output_dir / entry.name
                self._logger.debug(f"添加处理任务: {src_path} → {dest_path}")
                yield (src_path, dest_path)
            else:
                self._scan_skipped += 1
                self._logger.debug(f"跳过非支持文件: {src_path}")
```

--- R1
要递归遍历目录及其子目录并为每个支持的文件生成处理任务，同时保持输出目录的相同结构，以下是优化后的代码实现：

```python
import os
from pathlib import Path
from typing import Iterable, Tuple

class FileProcessor:
    _SUPPORTED_EXT = ('.jpg', '.png', '.txt')  # 支持的文件扩展名示例

    def __init__(self, logger):
        self._logger = logger
        self._scan_skipped = 0

    def _generate_tasks(self, input_dir: Path, output_dir: Path) -> Iterable[Tuple[Path, Path]]:
        """递归生成文件处理任务"""
        for entry in os.scandir(input_dir):
            src_path = Path(entry.path)

            if entry.is_file():
                # 处理单个文件
                if src_path.suffix.lower() in self._SUPPORTED_EXT:
                    dest_path = output_dir / src_path.name
                    self._logger.debug(f"✅ 添加任务: {src_path} → {dest_path}")
                    yield (src_path, dest_path)
                else:
                    self._scan_skipped += 1
                    self._logger.debug(f"⏩ 跳过非支持文件: {src_path}")

            elif entry.is_dir():
                # 处理子目录（递归）
                sub_output = output_dir / entry.name
                self._logger.debug(f"📂 进入子目录: {src_path} → {sub_output}")
                yield from self._generate_tasks(src_path, sub_output)

            else:
                # 处理非常规文件（如符号链接）
                self._scan_skipped += 1
                self._logger.warning(f"🚫 跳过非常规文件: {src_path}")

# 使用示例
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    processor = FileProcessor(logging.getLogger())

    # 生成任务示例
    input_path = Path("/path/to/input")
    output_path = Path("/path/to/output")

    for src, dest in processor._generate_tasks(input_path, output_path):
        print(f"Processing: {src} → {dest}")
```

### 主要改进点说明

1. **递归目录处理**

   - 遇到子目录时自动递归处理
   - 输出目录保持与输入相同的目录结构
   - 示例输入：`/input/folder1/file.jpg`  
     对应输出：`/output/folder1/file.jpg`

2. **增强日志信息**

   - 使用可视化图标提高日志可读性
   - 区分不同日志级别（DEBUG、WARNING）

3. **异常文件处理**

   - 跳过符号链接等非常规文件
   - 统计跳过的文件数量（通过 `_scan_skipped` 属性）

4. **类型提示**
   - 明确输入输出参数类型为 `Path`
   - 返回值的元组类型标注为 `Tuple[Path, Path]`

### 文件处理流程图

```text
开始扫描
├── 遇到文件
│   ├── 支持扩展 → 生成任务
│   └── 不支持扩展 → 跳过并计数
│
└── 遇到目录
    ├── 创建对应输出子目录
    └── 递归扫描子目录内容
```

### 推荐的最佳实践

1. **前置目录创建**  
   在执行实际文件操作前，建议添加目录创建逻辑：

   ```python
   dest_path.parent.mkdir(parents=True, exist_ok=True)
   ```

2. **性能优化**

   - 对于超大型目录，可改用 `os.walk` 优化遍历性能
   - 添加并行处理支持（如使用 `concurrent.futures`）

3. **扩展过滤条件**  
   可添加更多过滤规则，例如：

   ```python
   # 按文件名过滤
   if src_path.name.startswith('.'):
       self._logger.debug(f"跳过隐藏文件: {src_path}")
       continue

   # 按文件大小过滤
   if entry.stat().st_size > 100_000_000:  # 100MB
       self._logger.warning(f"文件过大: {src_path}")
       continue
   ```

4. **结果验证**  
   建议添加后处理校验逻辑：
   ```python
   if not dest_path.exists():
       self._logger.error(f"文件生成失败: {dest_path}")
   ```

主函数实现 NormalWatermarkProcessor 时， 父类 BaseWatermarkProcessor 使用 process_batch 函数时调用子类的方法 process_single，此时传递参数
如果使用的是 FoggyWatermarkProcessor，可能传递给 process_single 的方法就不一样了。所以这个实现要怎么替代？

```python
# 创建参数对象
params = NormalWatermarkParams(opacity=0.8)

# 初始化处理器
processor = NormalProcessor()

# 处理文件
processor.process_single(
    input_path=Path("input.jpg"),
    output_path=Path("output.jpg"),
    params=params
)
```

--- R1
python
T = TypeVar('T', bound=ProcessParams)
class BaseWatermarkProcessor(Generic[T]):
def process_single(self, input_path: Path, output_path: Path, params: T) -> None:
raise NotImplementedError

````
这样，子类可以指定具体的参数类型：
```python
class NormalWatermarkProcessor(BaseWatermarkProcessor[NormalWatermarkParams]):
    def process_single(self, input_path: Path, output_path: Path, params: NormalWatermarkParams) -> None:
        # 具体实现
````

3. **确保参数对象与处理器匹配**：在创建处理器实例时，需要传递对应的参数对象。例如，`Normal`处理器使用`NormalWatermarkParams`，`Foggy`处理器使用`FoggyWatermarkParams`。

4. **处理`process_batch`方法**：父类的`process_batch`方法需要生成对应的参数对象，并传递给`process_single`。这可能需要一个工厂方法或配置来根据处理器类型生成正确的参数。

可能遇到的问题包括如何动态地创建正确的参数对象，以及如何确保类型安全，避免传递错误的参数类型给子类。

另外，需要考虑如何在运行时确保参数对象符合子类的要求。例如，使用`isinstance`检查参数类型，或者在父类中定义抽象方法，强制子类实现参数生成逻辑。

总结一下，解决方案应该包括：

- 使用泛型类来绑定处理器和参数类型。
- 在父类中定义通用的`process_batch`方法，但具体参数生成由子类处理。
- 确保参数对象符合子类的要求，可能通过工厂模式或配置类。

接下来，我需要将这些思考转化为具体的代码实现，并验证其正确性。

<end>已深度思考（用时 31 秒）</end>

### 解决方案

为了确保不同子类处理器（如 `Normal` 和 `Foggy`）能正确处理各自的参数，同时保持类型安全和代码复用，可以采用以下分步实现：

---

#### 1. **定义参数协议和泛型基类**

```python
from typing import Protocol, Generic, TypeVar, runtime_checkable
from pathlib import Path
from abc import ABC, abstractmethod

# 定义参数协议
@runtime_checkable
class ProcessParams(Protocol):
    opacity: float
    blend_mode: str

# 泛型类型变量，绑定到参数协议
T = TypeVar("T", bound=ProcessParams)

class BaseWatermarkProcessor(Generic[T], ABC):
    """水印处理器基类（泛型）"""

    @abstractmethod
    def process_single(
        self,
        input_path: Path,
        output_path: Path,
        params: T  # 由子类指定具体参数类型
    ) -> None:
        """处理单个文件（子类必须实现）"""
        raise NotImplementedError

    def process_batch(
        self,
        input_dir: Path,
        output_dir: Path
    ) -> list[Path]:
        """批量处理文件（通用逻辑）"""
        success_files = []
        for input_path in input_dir.glob("*"):
            output_path = output_dir / input_path.name
            params = self._create_params()  # 由子类生成参数
            try:
                self.process_single(input_path, output_path, params)
                success_files.append(output_path)
            except Exception as e:
                self._log_error(input_path, e)
        return success_files

    @abstractmethod
    def _create_params(self) -> T:
        """创建参数对象（子类必须实现）"""
        raise NotImplementedError

    def _log_error(self, input_path: Path, error: Exception):
        print(f"处理失败: {input_path} - {error}")
```

---

#### 2. **实现具体处理器和参数类**

```python
# Normal 水印处理器及参数
class NormalWatermarkParams:
    def __init__(self, opacity: float, blend_mode: str = "multiply"):
        self.opacity = opacity
        self.blend_mode = blend_mode

class NormalWatermarkProcessor(BaseWatermarkProcessor[NormalWatermarkParams]):
    def process_single(
        self,
        input_path: Path,
        output_path: Path,
        params: NormalWatermarkParams  # 明确参数类型
    ) -> None:
        print(f"处理普通水印 | 模式: {params.blend_mode}, 透明度: {params.opacity}")
        # 实际处理逻辑...

    def _create_params(self) -> NormalWatermarkParams:
        return NormalWatermarkParams(opacity=0.8)

# Foggy 水印处理器及参数
class FoggyWatermarkParams:
    def __init__(self, opacity: float, dispersion: float):
        self.opacity = opacity
        self.blend_mode = "foggy"  # 必须符合协议
        self.dispersion = dispersion  # 扩展参数

class FoggyWatermarkProcessor(BaseWatermarkProcessor[FoggyWatermarkParams]):
    def process_single(
        self,
        input_path: Path,
        output_path: Path,
        params: FoggyWatermarkParams  # 明确参数类型
    ) -> None:
        print(f"处理雾化水印 | 雾化强度: {params.dispersion}")
        # 实际处理逻辑...

    def _create_params(self) -> FoggyWatermarkParams:
        return FoggyWatermarkParams(opacity=0.7, dispersion=0.2)
```

---

#### 3. **主函数调用示例**

```python
def main():
    # 初始化处理器
    normal_processor = NormalWatermarkProcessor()
    foggy_processor = FoggyWatermarkProcessor()

    # 处理文件
    input_dir = Path("input_images")
    output_dir = Path("output_images")

    # 普通水印处理
    normal_results = normal_processor.process_batch(input_dir, output_dir)
    print(f"普通水印成功处理: {len(normal_results)} 文件")

    # 雾化水印处理
    foggy_results = foggy_processor.process_batch(input_dir, output_dir)
    print(f"雾化水印成功处理: {len(foggy_results)} 文件")

if __name__ == "__main__":
    main()
```

---

### 关键设计说明

1. **泛型参数绑定**

   - 基类 `BaseWatermarkProcessor` 使用泛型 `T` 绑定到具体参数类型。
   - 子类通过 `BaseWatermarkProcessor[SpecificParams]` 明确参数类型，如 `NormalWatermarkProcessor` 绑定 `NormalWatermarkParams`。

2. **参数生成隔离**

   - 子类必须实现 `_create_params()` 方法，负责生成符合自身需求的参数对象。
   - 父类 `process_batch()` 统一调用此方法获取参数，确保参数类型与处理器匹配。

3. **类型安全验证**

   - 通过 `@runtime_checkable` 协议确保参数对象实现必要属性（如 `opacity`）。
   - 静态类型检查（如 mypy）会验证子类方法的参数类型是否匹配泛型约束。

4. **扩展性**
   - 新增水印类型只需继承基类并实现 `process_single` 和 `_create_params`，无需修改现有代码。

---

### 输出示例

```plaintext
处理普通水印 | 模式: multiply, 透明度: 0.8
处理普通水印 | 模式: multiply, 透明度: 0.8
普通水印成功处理: 2 文件

处理雾化水印 | 雾化强度: 0.2
处理失败: input_images/image2.jpg - 文件格式不支持
雾化水印成功处理: 1 文件
```

通过这种设计，不同处理器能安全地处理各自的参数类型，同时保持批量处理逻辑的复用性。

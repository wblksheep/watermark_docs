我应该从基类中引入 T 和 ProcessParams 还是？

```python
    def _validate_params(self, params: T):
        # 运行时校验协议实现
        if not isinstance(params, ProcessParams):  # 依赖 @runtime_checkable
            missing = []
            if not hasattr(params, 'opacity'):
                missing.append('opacity')
            if not hasattr(params, 'blend_mode'):
                missing.append('blend_mode')
            raise TypeError(f"参数缺少必要属性: {missing}")
```

--- R1
以下是关于类型参数 `T` 和协议 `ProcessParams` 的归属及使用建议：

---

### 代码组织最佳实践

#### 1. **将协议与泛型定义放在基类模块**

```python
# base_processor.py
from typing import Protocol, TypeVar, runtime_checkable

@runtime_checkable
class ProcessParams(Protocol):
    """参数协议（定义公共接口）"""
    opacity: float
    blend_mode: str

# 泛型参数类型（绑定到协议）
T = TypeVar("T", bound=ProcessParams)

class BaseWatermarkProcessor(Generic[T]):
    """泛型基类处理器"""
    def process_single(self, input_path: Path, output_path: Path, params: T) -> None:
        self._validate_params(params)
        # ... 其他逻辑

    def _validate_params(self, params: T):
        """参数校验（同时验证协议和业务规则）"""
        # 协议层校验（强制接口实现）
        if not isinstance(params, ProcessParams):  # 必须显式检查协议
            missing = []
            if not hasattr(params, 'opacity'):
                missing.append('opacity')
            if not hasattr(params, 'blend_mode'):
                missing.append('blend_mode')
            raise TypeError(f"参数违反协议，缺少属性: {missing}")

        # 业务规则校验（值有效性）
        if not (0 <= params.opacity <= 1):
            raise ValueError("透明度需在0-1之间")
```

#### 2. **子类直接继承泛型参数**

```python
# normal_processor.py
from .base_processor import BaseWatermarkProcessor, ProcessParams

class NormalParams:
    """普通水印参数（隐式实现协议）"""
    def __init__(self, opacity: float, blend_mode: str = "multiply"):
        self.opacity = opacity
        self.blend_mode = blend_mode

class NormalProcessor(BaseWatermarkProcessor[NormalParams]):
    """普通水印处理器"""
    def process_single(self, input_path: Path, output_path: Path, params: NormalParams) -> None:
        # 此处 params 类型自动受 NormalParams 约束
        print(f"使用模式 {params.blend_mode} 处理")
```

---

### 关键设计决策说明

#### 1. \*\*为什么需要同时使用 `T` 和 `ProcessParams`？

- **类型安全（静态检查）**  
  `T = TypeVar("T", bound=ProcessParams)` 通过泛型确保子类参数类型必须符合协议，在 IDE 和静态类型检查器（如 mypy）中直接报错。
- **运行时校验（防御性编程）**  
  使用 `isinstance(params, ProcessParams)` 动态检查协议实现，防止以下情况：

  ```python
  class WrongParams:  # 未实现协议
      def __init__(self, opacity: int):  # 错误类型
          self.opacity = opacity
          self.blend_mode = 123  # 错误类型

  processor = NormalProcessor()
  processor.process_single(..., params=WrongParams(opacity=100))  # 静态类型检查会报错，但动态语言可能绕过
  ```

#### 2. **协议与泛型的分工**

- **协议 (`ProcessParams`)**  
  定义参数的最小公共接口，不关心具体实现类。

- **泛型 (`T`)**  
  约束子类处理器的参数类型范围，实现类型级联。

#### 3. **代码复用优化**

- **校验逻辑复用**  
  基类的 `_validate_params` 方法统一处理协议校验和公共业务规则（如透明度范围），子类只需关注自身逻辑：
  ```python
  class FoggyProcessor(BaseWatermarkProcessor[FoggyParams]):
      def process_single(self, input_path: Path, output_path: Path, params: FoggyParams) -> None:
          # 无需重复校验 opacity
          print(f"雾化强度: {params.dispersion}")
  ```

---

### 最终结论

**必须同时在基类中引入 `T` 和 `ProcessParams`**，二者协同工作以实现：

1. **静态类型安全** → 通过泛型约束
2. **动态类型防御** → 通过协议运行时校验
3. **代码最大复用** → 公共校验逻辑集中在基类

这种设计能在 Python 的动态类型特性下提供最大程度的类型安全保障。

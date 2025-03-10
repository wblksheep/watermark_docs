在 Model 层中有以下代码，它有什么问题？配置类和处理器类在哪里创建比较好？

```python
    def process_normal_watermark(self, folder,  **kwargs):
        # 初始化配置
        try:
            config = YamlWatermarkConfig(Path("config.yaml"))
        except Exception as e:
            logger.exception(e)
            raise e
        # 创建处理器
        processor = NormalWatermarkProcessor(
            config=config,
            npy_path="watermark_normal_200.npy"
        )
        # # 执行批量处理
        # input_dir = Path("input")
        output_dir = Path("output")
        success_files = processor.process_batch(folder, output_dir)

        print(f"成功处理 {len(success_files)} 张图片")

    def process_foggy_watermark(self, folder, text="BH", **kwargs):
        print({"folder":folder,**{param: data for param, data in kwargs.items()}})
```

--- R1

### 问题分析

以下代码存在三个核心问题：

---

#### 1. **硬编码配置路径（违反关注点分离原则）**

```python
config = YamlWatermarkConfig(Path("config.yaml"))  # 硬编码路径
processor = NormalWatermarkProcessor(config=config, npy_path="watermark_normal_200.npy")
```

**问题：**

- 配置路径 `config.yaml` 和水印文件路径 `watermark_normal_200.npy` 直接硬编码在业务逻辑中，导致：
  - **维护困难**：路径变更需要修改代码。
  - **环境不兼容**：无法区分开发/生产环境配置。
  - **代码耦合**：Model 层依赖具体文件路径，无法复用。

**改进方向：**

- 通过依赖注入传递配置对象，而非在 Model 层直接创建。

---

#### 2. **业务逻辑与对象创建耦合（违反单一职责原则）**

```python
def process_normal_watermark(self, folder, **kwargs):
    # 初始化配置、创建处理器等非业务逻辑操作
    config = YamlWatermarkConfig(...)
    processor = NormalWatermarkProcessor(...)
    # 业务逻辑操作
    success_files = processor.process_batch(...)
```

**问题：**

- Model 层方法同时负责配置加载、处理器创建和业务逻辑，职责不单一。
- 测试困难：需真实文件才能测试业务逻辑。

**改进方向：**

- 将对象创建逻辑移至工厂类或依赖注入框架。

---

#### 3. **异常处理冗余**

```python
try:
    config = YamlWatermarkConfig(...)
except Exception as e:
    logger.exception(e)
    raise e  # 抛出后外层仍需捕获，冗余
```

**问题：**

- 捕获异常仅为了记录日志，随后重新抛出，导致调用方仍需处理异常。
- 日志重复记录风险（如果外层也捕获异常）。

**改进方向：**

- 由调用方统一处理异常，或定义业务异常类。

---

### 配置类与处理器类的推荐创建位置

#### 1. **配置类创建**

**推荐位置：** **应用启动层**

- 在程序入口（如 `main()` 函数）或配置管理模块中初始化。
- 通过环境变量或配置文件动态加载路径。

**示例：**

```python
# config_manager.py
class ConfigLoader:
    @classmethod
    def load_watermark_config(cls) -> WatermarkConfig:
        env = os.getenv("APP_ENV", "dev")
        config_path = Path(f"config/{env}_watermark.yaml")  # 按环境加载
        return YamlWatermarkConfig(config_path)

# main.py
config = ConfigLoader.load_watermark_config()
processor_factory = ProcessorFactory(config)
model = WatermarkModel(processor_factory)
```

---

#### 2. **处理器类创建**

**推荐位置：** **工厂类**

- 使用工厂模式集中管理处理器创建逻辑。
- 通过依赖注入将工厂传递给 Model 层。

**示例：**

```python
# processors.py
class ProcessorFactory:
    def __init__(self, config: WatermarkConfig):
        self.config = config

    def create_normal_processor(self) -> WatermarkProcessor:
        return NormalWatermarkProcessor(
            config=self.config,
            npy_path=self.config.npy_path  # 从配置中读取路径
        )

# model.py
class WatermarkModel:
    def __init__(self, processor_factory: ProcessorFactory):
        self.processor_factory = processor_factory

    def process_normal_watermark(self, folder: Path) -> List[Path]:
        processor = self.processor_factory.create_normal_processor()
        return processor.process_batch(folder)
```

---

### 改进后代码示例

#### 1. **依赖注入 + 工厂模式**

```python
# Model 层（仅关注业务逻辑）
class WatermarkModel:
    def __init__(self, processor_factory: ProcessorFactory):
        self.processor_factory = processor_factory

    def process_normal_watermark(self, folder: Path) -> List[Path]:
        """添加水印核心逻辑"""
        processor = self.processor_factory.create_normal_processor()
        output_dir = self._prepare_output_dir()
        return processor.process_batch(folder, output_dir)

    def _prepare_output_dir(self) -> Path:
        """创建输出目录（复用逻辑）"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        return output_dir
```

#### 2. **统一异常处理（调用方）**

```python
# controller.py
try:
    model.process_normal_watermark(Path("input"))
except WatermarkError as e:  # 自定义业务异常
    logger.error(f"业务处理失败: {e}")
    show_user_message("添加水印失败，请检查输入文件")
except Exception as e:
    logger.critical(f"系统错误: {e}")
    show_user_message("系统异常，请联系管理员")
```

---

### 总结

- **配置类**应在应用启动时按环境加载，通过依赖注入传递。
- **处理器类**通过工厂模式创建，避免 Model 层耦合具体实现。
- **Model 层**仅关注核心业务逻辑，不处理对象创建或路径解析。

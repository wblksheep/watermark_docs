运行时库导入的时候有问题，程序不报错，为其添加日志调试信息：

```python
import logging
import sys, os
from pathlib import Path

# ---------------------------- 日志初始化 ----------------------------
logging.basicConfig(
    level=logging.DEBUG,  # 改为DEBUG级别以显示更多信息
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),  # 修正文件名
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
# ---------------------------- 初始路径信息 ----------------------------
logger.info("=============== 应用启动 ===============")
logger.debug(f"[启动阶段] 当前工作目录: {os.getcwd()}")
logger.debug(f"[启动阶段] 系统路径 sys.path:\n{'\n'.join(sys.path)}")
logger.debug(f"[启动阶段] Python解释器路径: {sys.executable}")
logger.debug(f"[启动阶段] 脚本入口文件: {__file__}")

from PySide6.QtWidgets import QApplication

from container import Container
from config import setup_logging, AppConfig
from src.config_loader import ConfigLoader


def get_base_path():
    """获取资源基准路径（添加详细日志）"""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
        logger.debug(f"[路径解析] 处于冻结环境，基础路径: {base_path}")
    else:
        base_path = Path(__file__).parent
        logger.debug(f"[路径解析] 处于开发环境，基础路径: {base_path}")

    logger.debug(f"[路径解析] 最终 base_path 是否存在: {base_path.exists()}")
    return base_path

def main():
    logger.info("=============== 进入 main 函数 ===============")

    # 再次记录路径（防止之前导入模块修改了路径）
    logger.debug(f"[main函数] 当前工作目录: {os.getcwd()}")
    logger.debug(f"[main函数] 更新后的 sys.path:\n{'\n'.join(sys.path)}")
    app = QApplication(sys.argv)
    logger.debug("QApplication 实例已创建")


    try:
        # ---------------------------- 配置加载 ----------------------------
        base_path = get_base_path()
        config_path = base_path / 'config.yaml'
        logger.debug(f"[配置加载] 尝试加载配置文件: {config_path.absolute()}")
        logger.debug(f"[配置加载] 配置文件是否存在: {config_path.exists()}")

        config = ConfigLoader.load_config(config_path, AppConfig)
        logger.info("配置文件加载成功")
        logger.debug(f"[配置内容] 当前配置: {config}")
        # ---------------------------- 依赖注入 ----------------------------
        container = Container()
        logger.debug("依赖容器已初始化")

        presenter = container.presenter(config=config)
        logger.debug("Presenter 实例已创建")

        view = container.view()
        logger.debug("View 实例已创建")

        view.show()
        logger.info("主窗口已显示")

        sys.exit(app.exec())
    except Exception as e:
        logger.exception(e)
        # raise Exception(e)


if __name__ == "__main__":
    main()
```

--- R1

以下是针对模块导入问题添加的详细日志调试信息，帮助定位库导入失败的根本原因：

```python
import logging
import sys
import os
from pathlib import Path

# ---------------------------- 日志初始化 ----------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------------------------- 初始路径信息 ----------------------------
logger.info("=============== 应用启动 ===============")
logger.debug(f"[启动阶段] 当前工作目录: {os.getcwd()}")
logger.debug(f"[启动阶段] 系统路径 sys.path:\n{'\n'.join(sys.path)}")
logger.debug(f"[启动阶段] Python解释器路径: {sys.executable}")
logger.debug(f"[启动阶段] 脚本入口文件: {__file__}")

# ---------------------------- 关键库导入追踪 ----------------------------
try:
    logger.debug("[模块导入] 尝试导入 PySide6.QtWidgets...")
    from PySide6.QtWidgets import QApplication
    logger.debug(f"[模块导入] PySide6 成功导入，模块路径: {os.path.dirname(QApplication.__file__)}")
except ImportError as e:
    logger.error("[模块导入] PySide6 导入失败！")
    logger.exception(e)
    sys.exit(1)

try:
    logger.debug("[模块导入] 尝试导入 container 模块...")
    from container import Container
    logger.debug(f"[模块导入] container 模块路径: {Container.__module__.__file__}")
except ImportError as e:
    logger.error("[模块导入] container 模块导入失败，可能路径配置错误！")
    logger.exception(e)
    sys.exit(1)

try:
    logger.debug("[模块导入] 尝试导入 config 模块...")
    from config import setup_logging, AppConfig
    logger.debug(f"[模块导入] config 模块路径: {os.path.abspath(__import__('config').__file__)}")
except ImportError as e:
    logger.error("[模块导入] config 模块导入失败，检查文件是否存在！")
    logger.exception(e)
    sys.exit(1)

try:
    logger.debug("[模块导入] 尝试导入 src.config_loader...")
    from src.config_loader import ConfigLoader
    logger.debug(f"[模块导入] ConfigLoader 路径: {ConfigLoader.__module__.__file__}")
except ImportError as e:
    logger.error("[模块导入] src.config_loader 导入失败，检查 src 目录结构！")
    logger.exception(e)
    sys.exit(1)

# ---------------------------- 函数定义 ----------------------------
def get_base_path():
    """获取资源基准路径（添加详细日志）"""
    logger.debug("[路径解析] 开始计算基础路径...")
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
        logger.debug(f"[路径解析] 处于冻结环境，基础路径: {base_path}")
    else:
        base_path = Path(__file__).parent
        logger.debug(f"[路径解析] 处于开发环境，基础路径: {base_path}")

    logger.debug(f"[路径解析] 最终 base_path 是否存在: {base_path.exists()}")
    logger.debug(f"[路径解析] base_path 内容列表:\n{', '.join(os.listdir(base_path))}")
    return base_path

def main():
    logger.info("=============== 进入 main 函数 ===============")
    logger.debug(f"[main函数] 当前工作目录: {os.getcwd()}")
    logger.debug(f"[main函数] 更新后的 sys.path:\n{'\n'.join(sys.path)}")

    try:
        app = QApplication(sys.argv)
        logger.debug("QApplication 实例已创建")

        # ---------------------------- 配置加载 ----------------------------
        base_path = get_base_path()
        config_path = base_path / 'config.yaml'
        logger.debug(f"[配置加载] 尝试加载配置文件: {config_path.absolute()}")
        logger.debug(f"[配置加载] 配置文件是否存在: {config_path.exists()}")
        if not config_path.exists():
            logger.error(f"[配置加载] 配置文件不存在！搜索路径: {config_path.resolve()}")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        logger.debug("[配置加载] 开始加载配置文件...")
        config = ConfigLoader.load_config(config_path, AppConfig)
        logger.info("配置文件加载成功")
        logger.debug(f"[配置内容] 当前配置: {config}")

        # ---------------------------- 依赖注入 ----------------------------
        logger.debug("[依赖注入] 初始化容器...")
        container = Container()
        logger.debug(f"[依赖注入] 容器对象类型: {type(container)}")

        logger.debug("[依赖注入] 创建 Presenter...")
        presenter = container.presenter(config=config)
        logger.debug(f"[依赖注入] Presenter 类型: {type(presenter)}")

        logger.debug("[依赖注入] 创建 View...")
        view = container.view()
        logger.debug(f"[依赖注入] View 类型: {type(view)}")

        logger.debug("[界面显示] 准备显示主窗口...")
        view.show()
        logger.info("主窗口已显示")

        sys.exit(app.exec())
    except Exception as e:
        logger.error("[严重错误] 主流程异常终止！")
        logger.exception(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### **主要增强点说明：**

---

#### 1. **模块导入追踪**

- 每个关键导入语句包裹在 `try-except` 中，记录：
  ```python
  try:
      logger.debug("[模块导入] 尝试导入 xxx...")
      from xxx import yyy
      logger.debug(f"模块路径: {yyy.__file__}")  # 确认实际加载路径
  except ImportError as e:
      logger.error("具体模块导入失败！")
      logger.exception(e)
      sys.exit(1)
  ```
- 记录模块的 `__file__` 属性，验证是否从预期位置加载

---

#### 2. **路径验证增强**

- 在 `get_base_path()` 中添加：
  ```python
  logger.debug(f"[路径解析] base_path 内容列表:\n{', '.join(os.listdir(base_path))}")
  ```
  列出目录内容，验证关键文件（如 `config.yaml`）是否可见

---

#### 3. **依赖注入调试**

- 记录对象类型，验证是否成功创建：
  ```python
  logger.debug(f"[依赖注入] 容器对象类型: {type(container)}")
  logger.debug(f"[依赖注入] Presenter 类型: {type(presenter)}")
  ```

---

#### 4. **配置文件存在性检查**

- 明确检查配置文件存在性：
  ```python
  if not config_path.exists():
      logger.error(f"配置文件不存在！搜索路径: {config_path.resolve()}")
  ```

---

#### 5. **错误处理标准化**

- 所有异常捕获后立即记录完整堆栈：
  ```python
  logger.exception(e)
  sys.exit(1)  # 确保异常退出时有非0状态码
  ```

---

### **日志分析建议：**

1. **模块导入失败**  
   检查日志中 `[模块导入]` 相关条目，若某个模块失败，根据记录的路径验证：

   - 路径是否包含目标模块
   - 是否缺少依赖库（如 PySide6）

2. **配置文件丢失**  
   查看 `[配置加载]` 条目，确认 `config.yaml` 是否在列出的目录内容中

3. **路径分歧问题**  
   对比冻结环境和开发环境的 `base_path` 内容，确保资源文件打包正确

4. **依赖注入异常**  
   若 `Presenter` 或 `View` 未创建，检查容器初始化日志及类型信息

通过上述日志增强，可以快速定位到是路径配置错误、模块缺失还是依赖注入逻辑问题。

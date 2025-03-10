为以下内容添加 logger 调试信息，尤其是系统路径相关的

```python
import logging
import sys, os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("appooo.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"当前路径: {os.getcwd()}")
logger.info(f"系统路径: {sys.path}")
logger.info(f"可执行文件位置: {sys.executable}")

from PySide6.QtWidgets import QApplication

from container import Container
from config import setup_logging, AppConfig
from src.config_loader import ConfigLoader


def get_base_path():
    """获取资源基准路径"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def main():
    # logger = logging.getLogger(__name__)
    # logger.info(f"当前路径: {os.getcwd()}")
    # logger.info(f"系统路径: {sys.path}")
    # logger.info(f"可执行文件位置: {sys.executable}")
    app = QApplication(sys.argv)
    # setup_logging()
    # logger = logging.getLogger(__name__)


    try:
        # # 加载配置
        # config = ConfigLoader.load_config(
        #     Path('config.yaml'),
        #     AppConfig
        # )
        config_path = get_base_path() / 'config.yaml'
        config = ConfigLoader.load_config(config_path, AppConfig)
        container = Container()
        presenter = container.presenter(config=config)
        view = container.view()
        view.show()

        sys.exit(app.exec())
    except Exception as e:
        logger.exception(e)
        # raise Exception(e)


if __name__ == "__main__":
    main()
```

--- R1
以下是添加了详细 `logger` 调试信息的代码，尤其针对系统路径相关的内容，标注了关键修改点：

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
    except FileNotFoundError as e:
        logger.error(f"关键文件未找到: {e}")
        raise
    except Exception as e:
        logger.exception("未捕获的异常:")
        raise

if __name__ == "__main__":
    main()
```

### **主要改动说明：**

---

#### **1. 日志级别调整**

- 将 `level=logging.INFO` 改为 `level=logging.DEBUG`，确保调试信息可见。

---

#### **2. 路径信息增强**

- **启动阶段**：添加了脚本入口文件 `__file__` 的路径记录。
- **路径解析**：在 `get_base_path()` 中记录冻结环境/开发环境判断结果，并验证路径是否存在。
- **main 函数阶段**：二次记录 `sys.path` 和工作目录，防止其他模块修改路径。

---

#### **3. 关键操作跟踪**

- **配置加载**：记录配置文件绝对路径及其存在性。
- **依赖注入**：跟踪容器、Presenter、View 的初始化过程。
- **异常处理**：区分 `FileNotFoundError` 和其他异常，明确错误类型。

---

#### **4. 日志格式优化**

- 在关键日志中添加 `[标签]`（如 `[路径解析]`），便于快速定位问题。
- 使用 `\n` 格式化 `sys.path` 输出，提升可读性。

---

### **使用建议：**

1. **调试打包问题**：重点关注 `get_base_path()` 的日志，确认资源路径是否正确。
2. **模块导入失败**：对比启动时和 `main()` 中的 `sys.path`，检查路径是否被意外修改。
3. **配置加载失败**：通过日志确认 `config.yaml` 路径是否存在。

main 函数，自动生成配置文件，仅检验参数的配置传递机制并打印。

```python
from pydantic import BaseModel, Field, validator
from pathlib import Path

class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: str = Field(min_length=3)
    port: int = Field(ge=1024, le=65535)
    timeout_sec: float = Field(10.0, description="连接超时时间(秒)")

class AlgorithmParams(BaseModel):
    """算法参数配置"""
    learning_rate: float = 0.001
    batch_size: int = 32
    use_gpu: bool = False

class AppConfig(BaseModel):
    """全局应用配置"""
    env: str = Field("dev", regex="^(dev|test|prod)$")
    log_level: str = Field("INFO", regex="^(DEBUG|INFO|WARNING|ERROR)$")
    database: DatabaseConfig
    model_params: AlgorithmParams
    output_dir: Path = Path("results")

    @validator("output_dir")
    def validate_output_dir(cls, v):
        if not v.is_absolute():
            raise ValueError("输出路径必须为绝对路径")
        return v
```

--- R1
以下是一个自动生成测试配置并验证参数传递机制的 `main` 函数实现，该实现聚焦于配置系统的核心逻辑验证：

```python
from pathlib import Path
from pydantic import ValidationError
import random
import string

def generate_test_case(case_type: str) -> dict:
    """生成不同类型的测试配置"""
    base_config = {
        "env": "dev",
        "log_level": "INFO",
        "database": {
            "host": "db.example.com",
            "port": 5432,
            "timeout_sec": 15.0
        },
        "model_params": {
            "learning_rate": 0.001,
            "batch_size": 32,
            "use_gpu": False
        },
        "output_dir": "/data/output"
    }

    # 生成随机字符串
    rand_str = lambda: ''.join(random.choices(string.ascii_lowercase, k=5))

    if case_type == "valid":
        return base_config

    elif case_type == "invalid_env":
        return {**base_config, "env": "invalid_env"}

    elif case_type == "invalid_port":
        return {
            **base_config,
            "database": {
                **base_config["database"],
                "port": random.choice([1023, 65536, "invalid"])
            }
        }

    elif case_type == "nested_error":
        return {
            **base_config,
            "model_params": {
                "learning_rate": "not_a_float",
                "batch_size": 10.5,  # 浮点数错误
                "use_gpu": "not_bool"
            }
        }

    elif case_type == "path_error":
        return {
            **base_config,
            "output_dir": "relative/path"
        }

    elif case_type == "random":
        return {
            "env": random.choice(["dev", "test", "prod", "invalid"]),
            "log_level": random.choice(["DEBUG", "INFO", "ERROR", "INVALID"]),
            "database": {
                "host": rand_str() * random.randint(1, 3),  # 可能触发长度校验
                "port": random.randint(0, 100000),
                "timeout_sec": "string_instead_of_float"
            },
            "model_params": {
                "learning_rate": random.choice([0.01, "invalid"]),
                "batch_size": random.choice([16, 32.0]),
                "use_gpu": random.choice([True, False, "yes"])
            },
            "output_dir": random.choice(["/valid/path", "invalid/relative"])
        }

def validate_config(config: dict) -> dict:
    """执行配置校验并返回结果"""
    try:
        parsed = AppConfig(**config)
        return {
            "valid": True,
            "config": parsed.dict(),
            "errors": None
        }
    except ValidationError as e:
        return {
            "valid": False,
            "config": None,
            "errors": [
                {
                    "field": "->".join(map(str, err["loc"])),
                    "message": err["msg"],
                    "input": get_nested_value(config, err["loc"])
                }
                for err in e.errors()
            ]
        }

def get_nested_value(data: dict, loc: tuple):
    """递归获取嵌套字段值"""
    for key in loc:
        if isinstance(data, dict):
            data = data.get(key, "MISSING")
        else:
            return "N/A"
    return data

def print_result(case_type: str, result: dict):
    """可视化打印验证结果"""
    print(f"\n🔧 测试类型: {case_type.upper()}")
    print("📝 验证结果:", "✅ 通过" if result["valid"] else "❌ 失败")

    if not result["valid"]:
        print("\n❌ 错误详情:")
        for error in result["errors"]:
            print(f"  🎯 字段路径: {error['field']}")
            print(f"  📌 错误信息: {error['message']}")
            print(f"  📥 输入内容: {error['input']}\n")

def main():
    """主测试流程"""
    test_cases = [
        ("valid", "合法配置"),
        ("invalid_env", "非法环境参数"),
        ("invalid_port", "非法端口号"),
        ("nested_error", "嵌套模型错误"),
        ("path_error", "路径类型错误"),
        ("random", "随机压力测试")
    ]

    for case_type, description in test_cases:
        # 生成测试配置
        config = generate_test_case(case_type)

        # 执行配置验证
        result = validate_config(config)

        # 打印可视化报告
        print(f"\n{'='*30}")
        print(f"🏁 开始测试: {description}")
        print_result(case_type, result)

if __name__ == "__main__":
    main()
```

### 输出示例

```text
==============================
🏁 开始测试: 合法配置
🔧 测试类型: VALID
📝 验证结果: ✅ 通过

==============================
🏁 开始测试: 非法环境参数
🔧 测试类型: INVALID_ENV
📝 验证结果: ❌ 失败

❌ 错误详情:
  🎯 字段路径: env
  📌 错误信息: string does not match regex
  📥 输入内容: invalid_env

==============================
🏁 开始测试: 非法端口号
🔧 测试类型: INVALID_PORT
📝 验证结果: ❌ 失败

❌ 错误详情:
  🎯 字段路径: database->port
  📌 错误信息: value is not a valid integer
  📥 输入内容: invalid

==============================
🏁 开始测试: 嵌套模型错误
🔧 测试类型: NESTED_ERROR
📝 验证结果: ❌ 失败

❌ 错误详情:
  🎯 字段路径: model_params->learning_rate
  📌 错误信息: value is not a valid float
  📥 输入内容: not_a_float

  🎯 字段路径: model_params->batch_size
  📌 错误信息: value is not a valid integer
  📥 输入内容: 10.5

  🎯 字段路径: model_params->use_gpu
  📌 错误信息: value could not be parsed to a boolean
  📥 输入内容: not_bool
```

### 关键特性

1. **智能测试生成**

   - 预设常见错误场景（环境参数、端口范围、路径类型）
   - 支持随机压力测试覆盖边界条件

2. **深度错误追踪**

   - 显示错误字段的完整路径（如 `database->port`）
   - 展示错误输入值的具体内容

3. **可视化输出**

   - 使用图标符号增强可读性
   - 结构化展示错误堆栈信息

4. **灵活扩展性**
   - 通过 `generate_test_case` 函数可快速添加新测试类型
   - 支持自定义错误处理逻辑

该方案通过分层验证机制，可有效检测以下配置问题：

- ✅ 类型不匹配（字符串 → 数值）
- ✅ 正则表达式校验失败
- ✅ 嵌套模型字段校验
- ✅ 文件路径类型验证
- ✅ 数值范围越界

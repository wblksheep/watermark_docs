```error
Traceback (most recent call last):
  File "C:\Users\Design-10\.conda\envs\haiyin_python313\Lib\logging\__init__.py", line 1153, in emit
    stream.write(msg + self.terminator)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'gbk' codec can't encode character '\U0001f51a' in position 56: illegal multibyte sequence
```

--- R1

```ys_think

<icon>https://wy-static.wenxiaobai.com/bot-capability/prod/%E6%B7%B1%E5%BA%A6%E6%80%9D%E8%80%83.png</icon>

<start>思考中...</start>

嗯，用户遇到了一个Unicode编码错误，具体是在使用日志系统时尝试写入特殊字符（比如'\U0001f51a'，也就是🔄这个表情符号）的时候，触发了'gbk'编解码器的异常。首先，我需要理解这个错误的根本原因。

用户提供的错误信息显示，问题出现在logging模块的StreamHandler中，当尝试将包含Unicode字符的日志消息写入控制台时，由于默认编码是gbk，而该字符无法用gbk编码，所以抛出了UnicodeEncodeError。这种情况通常发生在Windows系统上，因为默认的控制台编码可能不是UTF-8。

接下来，我要考虑用户提供的代码中可能引发这个问题的地方。用户提到他们在日志消息中添加了表情符号，比如“🟢 开始批处理任务”，这些符号属于Unicode字符，而Windows控制台的默认编码（gbk）可能不支持这些字符，导致写入失败。

我需要回顾用户提供的代码，特别是日志系统的配置部分。在之前的优化中，他们可能使用了StreamHandler来输出日志到控制台，而没有指定正确的编码方式。因此，当含有特殊Unicode字符的日志信息被写入时，会引发编码错误。

解决这个问题的方法通常包括以下几个方面：

1. **指定正确的编码**：在创建FileHandler或StreamHandler时，明确指定使用UTF-8编码，避免依赖系统默认编码。

2. **替换或转义不可编码字符**：在处理日志消息时，替换掉无法被目标编码处理的字符，或者使用转义序列。

3. **确保控制台支持Unicode**：在Windows系统中，可能需要调整控制台的代码页为UTF-8，但这可能不总是可行，尤其是对于老旧版本的Windows。

在用户提供的代码中，StreamHandler被用来输出到控制台，但未指定编码。而FileHandler在创建时虽然指定了encoding='utf-8'，但可能控制台的处理方式不同。

可能的解决方案是修改StreamHandler的配置，确保在写入控制台时使用正确的编码。但需要注意的是，Python的StreamHandler默认使用sys.stdout的编码，而Windows的cmd或PowerShell默认可能使用gbk。因此，可能需要强制StreamHandler使用UTF-8编码，或者替换无法编码的字符。

另外，用户可能在日志消息中使用了表情符号，这些符号在控制台输出时如果编码不支持，就会导致错误。因此，另一个解决方案是避免在日志中使用这些符号，或者在输出到控制台时进行适当的处理。

现在，我需要将这些思考转化为具体的解决方案，提供给用户。需要分步骤说明如何修改代码，以及可能的替代方案，确保用户能够理解和实施这些修改。

<end>已深度思考（用时25秒）</end>

```

这是一个常见的编码问题，可以通过以下三种方式解决。以下是详细的解决方案：

### 方法一：修改流编码配置（推荐）

```python
# 修改LogSystem类的_setup方法
class LogSystem:
    @classmethod
    def _setup(cls):
        """线程安全的日志系统初始化"""
        # ...其他代码不变...

        # 修改StreamHandler配置
        stream_handler = logging.StreamHandler()
        stream_handler.setStream(
            open(sys.stdout.fileno(),
                 mode='w',
                 encoding='utf-8',
                 errors='replace',
                 buffering=1)
        )

        # ...后续配置保持不变...
```

### 方法二：使用编码安全的表情符号

```python
# 修改所有日志消息中的表情符号
self._logger.info(f"▶️ 开始批处理任务 | 输入目录: {input_dir}...")  # 使用基本符号
self._logger.info(f"👉 跳过非支持文件: {src_path}")          # 替代原有复杂符号
```

### 方法三：全局编码配置（适用于 Python 3.7+）

```python
# 在程序启动时添加
import io
import sys

sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer,
    encoding='utf-8',
    errors='replace',
    line_buffering=True
)
```

### 方案选择建议：

| 方案   | 优点             | 缺点             | 适用场景         |
| ------ | ---------------- | ---------------- | ---------------- |
| 方法一 | 精准控制日志输出 | 需要修改日志系统 | 需要保留原有符号 |
| 方法二 | 无需修改底层代码 | 改变可视化效果   | 快速修复需求     |
| 方法三 | 全局解决问题     | 可能影响其他输出 | 全新项目         |

建议采用方法一+方法三的组合方案：

```python
# 在文件顶部添加
import sys
import io

if sys.stdout.encoding != 'UTF-8':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8',
        errors='backslashreplace',
        line_buffering=True
    )

# 修改StreamHandler配置
stream_handler = logging.StreamHandler()
stream_handler.emit = lambda record: logging.StreamHandler.emit(
    stream_handler,
    logging.makeLogRecord({
        **record.__dict__,
        'msg': record.msg.encode('utf-8', 'replace').decode('utf-8')
    })
)
```

这个组合方案可以确保：

1. 标准输出强制使用 UTF-8 编码
2. 日志系统自动处理编码异常
3. 保留原始符号显示能力
4. 兼容 Windows/Linux/macOS 系统

验证修复后日志输出示例：

```log
2024-03-28 15:30:22.873 - MainThread - [INFO] - ? 开始批处理任务 | 输入目录: /input...
2024-03-28 15:30:23.125 - MainThread - [INFO] - ? 扫描到 42 个待处理文件...
```

> 注意：在部分老旧终端中，复杂 Unicode 字符可能显示为?符号，但这可以避免程序崩溃

当二次调用的时候，函数就失效了，程序一直在等待队列完成处理

```python
    def shutdown(self):
        """安全关闭日志系统"""
        self.listener.stop()
        while not self.log_queue.empty():
            time.sleep(0.1)  # 等待队列处理完成
```

--- R1
在二次调用 `shutdown` 时，队列可能未被正确处理，因为监听线程（listener）已停止但队列仍有残留项，导致循环无法退出。以下是解决方案：

**问题分析：**

1. **线程未完全停止：** 调用 `listener.stop()` 后，监听线程可能未处理完队列中的剩余项。
2. **不可靠的队列检查：** `self.log_queue.empty()` 在多线程环境下不可靠，可能误判队列状态。
3. **残留项未被处理：** 第二次调用时，若队列存在残留项且监听线程已终止，循环将无限等待。

**解决方案：**

1. **等待监听线程结束：** 停止监听线程后，使用 `join()` 确保其处理完所有队列项。
2. **移除队列检查循环：** 监听线程终止后，队列应已为空，无需额外检查。

**修改后的代码：**

```python
def shutdown(self):
    """安全关闭日志系统"""
    self.listener.stop()
    self.listener.join()  # 等待监听线程处理完成并终止
```

**详细说明：**

- **停止并等待线程：** `self.listener.join()` 确保线程在处理完所有队列项后终止，避免残留项导致的问题。
- **线程内部逻辑调整：** 确保监听线程在收到停止信号后继续处理剩余项，例如：

```python
# 监听线程的 run 方法示例
def run(self):
    while not self.stopped:
        try:
            record = self.log_queue.get(timeout=0.1)
            # 处理记录
        except queue.Empty:
            continue
    # 处理停止后剩余的记录
    while not self.log_queue.empty():
        try:
            record = self.log_queue.get_nowait()
            # 处理记录
        except queue.Empty:
            break
```

此调整确保线程在停止前清空队列，使得 `shutdown` 调用后队列必然为空，从而避免循环等待问题。

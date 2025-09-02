# 快速开始指南

## 1. 基本使用

### 导入库
```python
from security_detector import SecurityDetector
```

### 初始化检测器
```python
# 使用默认敏感词表
detector = SecurityDetector()

# 或使用自定义敏感词表
detector = SecurityDetector("/path/to/your/sensitive_words.txt")
```

### 检测文本
```python
text = "这是一个需要检测的文本"
result = detector.detect(text)

if result.is_safe:
    print("✅ 文本安全")
else:
    print("❌ 文本不安全")
    print(f"发现的敏感词: {result.sensitive_words}")
```

## 2. LLM安全检查

```python
user_input = "请帮我写一篇关于人工智能的文章"
is_safe = detector.is_safe_for_llm(user_input)

if is_safe:
    print("✅ 可以作为LLM输入")
else:
    print("❌ 不建议作为LLM输入")
```

## 3. 批量检测

```python
texts = ["文本1", "文本2", "文本3"]
results = detector.batch_detect(texts)

for i, result in enumerate(results):
    status = "安全" if result.is_safe else "不安全"
    print(f"文本{i+1}: {status}")
```

## 4. 命令行使用

### 检测单个文本
```bash
python cli.py -t "要检测的文本"
```

### 检测文件
```bash
python cli.py -f input.txt
```

### 批量检测
```bash
python cli.py -b batch_input.txt
```

### JSON格式输出
```bash
python cli.py -t "文本" --format json
```

## 5. 敏感词管理

```python
# 添加敏感词
detector.add_sensitive_word("新敏感词")

# 移除敏感词
detector.remove_sensitive_word("要移除的词")

# 获取所有敏感词
all_words = detector.get_sensitive_words()
```

## 6. 完整示例

```python
from security_detector import SecurityDetector

def check_user_input(user_text):
    """检查用户输入是否安全"""
    detector = SecurityDetector()
    
    # 检测文本
    result = detector.detect(user_text)
    
    # 返回结果
    return {
        "is_safe": result.is_safe,
        "risk_level": result.risk_level,
        "confidence": result.confidence,
        "sensitive_words": result.sensitive_words
    }

# 使用示例
user_input = "我想了解一些政治话题"
result = check_user_input(user_input)

if result["is_safe"]:
    print("✅ 输入安全，可以处理")
else:
    print("❌ 输入不安全，拒绝处理")
    print(f"风险等级: {result['risk_level']}")
    print(f"敏感词: {result['sensitive_words']}")
```

## 7. 性能优化建议

1. **重用检测器实例**: 避免重复创建检测器对象
2. **批量处理**: 使用 `batch_detect()` 处理大量文本
3. **缓存结果**: 对于重复检测的文本，可以缓存结果

```python
# 好的做法
detector = SecurityDetector()  # 创建一次

# 批量处理
texts = ["文本1", "文本2", "文本3", ...]
results = detector.batch_detect(texts)

# 避免的做法
for text in texts:
    detector = SecurityDetector()  # 每次都创建新实例
    result = detector.detect(text)
```

## 8. 错误处理

```python
try:
    detector = SecurityDetector()
    result = detector.detect(text)
except FileNotFoundError:
    print("敏感词表文件不存在")
except Exception as e:
    print(f"检测过程中出现错误: {e}")
```

## 9. 配置自定义

可以通过修改 `config.py` 文件来自定义检测行为：

```python
# 修改风险等级阈值
DETECTION_CONFIG = {
    "risk_thresholds": {
        "high": {"word_count": 3, "density": 0.05},  # 更严格
        "medium": {"word_count": 1, "density": 0.02},
        "low": {"word_count": 1, "density": 0.01}
    }
}
```

## 10. 测试

运行测试确保一切正常：

```bash
python test_security_detector.py
```

运行示例查看功能：

```bash
python example.py
```

---

现在您已经了解了基本用法，可以开始使用敏感词检测库了！如有问题，请查看完整的 [README.md](README.md) 文档。 
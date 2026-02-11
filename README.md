# ComfyUI Workflow Migration Tool

## 项目简介 (Project Overview)

This repository provides tools and documentation for migrating ComfyUI workflows from unstable GroundingDino nodes to more reliable alternatives like Florence-2.

本项目提供工具和文档，用于将 ComfyUI 工作流从不稳定的 GroundingDino 节点迁移到更可靠的替代方案（如 Florence-2）。

## 问题背景 (Background)

GroundingDino in ComfyUI workflows suffers from:
- 🔴 Instability and frequent errors (不稳定性和频繁错误)
- 🔴 Low-quality code requiring constant troubleshooting (低质量代码需要持续排查)
- 🔴 Poor performance (性能问题)
- 🔴 Lack of maintenance (缺乏维护)

## 解决方案 (Solution)

Replace GroundingDino with **Florence-2** or **YOLO** for:
- ✅ Better stability (更好的稳定性)
- ✅ Improved performance (提升性能)
- ✅ Higher quality code (更高质量代码)
- ✅ Active maintenance (积极维护)

## 快速开始 (Quick Start)

### Automatic Migration (自动迁移)

```bash
# Migrate your workflow automatically
python migrate_workflow.py your_workflow.json migrated_workflow.json --pretty
```

### Manual Migration (手动迁移)

See [GROUNDINGDINO_REPLACEMENT_GUIDE.md](GROUNDINGDINO_REPLACEMENT_GUIDE.md) for detailed instructions.

## 文件说明 (Files)

- **GROUNDINGDINO_REPLACEMENT_GUIDE.md** - Comprehensive migration guide (完整迁移指南)
- **migrate_workflow.py** - Automatic migration script (自动迁移脚本)
- **example_workflow_before.json** - Example workflow with GroundingDino (使用 GroundingDino 的示例工作流)
- **example_workflow_after.json** - Example workflow with Florence-2 (使用 Florence-2 的示例工作流)

## Installation (安装)

### 1. Install Florence-2 in ComfyUI

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/kijai/ComfyUI-Florence2
pip install -r ComfyUI-Florence2/requirements.txt
```

### 2. Use the Migration Script

```bash
python migrate_workflow.py input.json output.json
```

## Migration Benefits (迁移优势)

| Feature | GroundingDino | Florence-2 |
|---------|---------------|------------|
| Stability | ❌ Poor | ✅ Excellent |
| Performance | ❌ Slow | ✅ Fast |
| Code Quality | ❌ Low | ✅ High |
| Maintenance | ❌ Inactive | ✅ Active |
| Memory Usage | ❌ High | ✅ Optimized |
| Accuracy | ⚠️ Moderate | ✅ High |

## Usage Example (使用示例)

```bash
# Before migration test
# Load example_workflow_before.json in ComfyUI
# May experience: crashes, errors, slow inference

# After migration
python migrate_workflow.py example_workflow_before.json my_migrated_workflow.json --pretty

# Load my_migrated_workflow.json in ComfyUI
# Experience: stable, fast, reliable
```

## Support (支持)

For issues or questions:
1. Check [GROUNDINGDINO_REPLACEMENT_GUIDE.md](GROUNDINGDINO_REPLACEMENT_GUIDE.md)
2. Review example workflows
3. Open an issue on GitHub

## License

MIT License - Feel free to use and modify

---

**推荐使用 Florence-2 替代 GroundingDino！**
(Recommended: Use Florence-2 instead of GroundingDino!)

# 设计系统 — AI 知识库

> Liquid Glass 液态玻璃风格 · 半透明 · 毛玻璃 · 流体动效

## 产品上下文

- **产品名称**：AI 知识库问答系统
- **产品类型**：Web应用 / Dashboard（Streamlit-based）
- **核心功能**：文档上传（PDF/MD/TXT）、智能问答、来源引用、文档管理
- **目标用户**：
  - 学习RAG技术的开发者
  - 需要个人文档知识库的用户
  - 对AI应用感兴趣的探索者
- **行业/领域**：AI/ML开发工具 + 知识管理 + 教育技术
- **使用场景**：长时间学习、知识查询、文档检索
- **部署环境**：本地开发 + 云端服务器（http://43.128.97.2:8501）

---

## 审美方向

**风格核心**：液态玻璃主义（Liquid Glassmorphism）

- **装饰水平**：表现型（Expressive）— 渐变、模糊、流体动画
- **设计哲学**：界面的层次像液态玻璃一样流动、融合
- **情感目标**：未来感、轻盈、沉浸式、梦幻
- **参考产品**：iOS 26、macOS 26、visionOS、Windows 11

**为什么选择这个方向？**
1. **极致现代感** — 代表2025-2026年的设计趋势
2. **视觉冲击力强** — 毛玻璃+渐变产生惊艳效果
3. **沉浸式体验** — 流体动效让界面"活"起来
4. **差异化明显** — 区别于所有传统AI工具的极简风

---

## 色彩系统

### 色彩策略：渐变半透明（Gradient Translucency）

**主色渐变**（液态蓝紫）
```css
/* 蓝紫粉渐变 */
--gradient-blue-purple: linear-gradient(135deg, #0071E3 0%, #5856D6 50%, #AF52DE 100%);

/* 青蓝渐变 */
--gradient-cyan-blue: linear-gradient(135deg, #5AC8FA 0%, #0071E3 100%);

/* 橙粉渐变 */
--gradient-orange-pink: linear-gradient(135deg, #FF9500 0%, #FF2D55 100%);
```

**背景渐变**（微妙彩色）
- 浅色模式：`linear-gradient(135deg, #F5F5F7 0%, #E8E8ED 100%)`
- 深色模式：`linear-gradient(135deg, #1C1C1E 0%, #000000 100%)`
- **背景流动**：15秒循环动画，渐变缓慢移动

**玻璃表面色**（半透明白/黑）
- 标准玻璃白：`rgba(255, 255, 255, 0.7)` + `backdrop-filter: blur(30px)`
- 轻玻璃白：`rgba(255, 255, 255, 0.5)` + `backdrop-filter: blur(20px)`
- 标准玻璃黑：`rgba(28, 28, 30, 0.7)` + `backdrop-filter: blur(30px)`

**语义色**（带透明度）
- 成功：`rgba(52, 199, 89, 0.8)`
- 警告：`rgba(255, 149, 0, 0.8)`
- 错误：`rgba(255, 59, 48, 0.8)`
- 信息：`rgba(90, 200, 250, 0.8)`

### 色彩使用原则

1. **渐变优先** — 按钮、标题、装饰使用渐变
2. **流动动画** — 渐变色背景流动（6-15秒循环）
3. **半透明表面** — 所有卡片和容器必须透明
4. **无纯色背景** — 背景必须是渐变
5. **色彩丰富** — 蓝紫粉橙四色系统

---

## 字体系统

### 字体策略：系统字体 + 更大字号

**显示/标题/正文**：系统字体栈
```css
font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
             "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
```

**代码/等宽**：`JetBrains Mono` 或 `SF Mono`

### 字号比例（Liquid Glass标准）

| 级别 | 字号 | 字重 | 使用场景 |
|------|------|------|----------|
| Large Title | 40px | 800 | 页面主标题 |
| Title 1 | 32px | 800 | 主要区块标题 |
| Title 2 | 26px | 700 | 次级区块标题 |
| Headline | 19px | 600 | 强调文本 |
| **Body** | **19px** | **500** | **正文（标准）** |
| Footnote | 15px | 500 | 注释、元数据 |
| Caption | 12px | 500 | 说明文字 |

**关键决策**：
- **19px作为标准正文** — 比极简Apple风格的17px更大
- **字重500-700** — 使用Medium/Semibold/Bold，不用Regular
- **标题加粗到800** — ExtraBold，增强视觉冲击力

---

## 间距系统

### 间距策略：极度宽松（Ultra-Generous）

**基础单位**：8px

**间距比例**
- 8px：微小间隙
- 16px：紧凑间距
- 24px：标准间距
- 32px：舒适间距
- 48px：宽松间距
- 64px：区块间距
- 96px：超大间距（新增）

**密度**：极度宽松 — 液态玻璃需要空间"流动"

---

## Glassmorphism 核心

### 毛玻璃效果配方

```css
/* 标准毛玻璃卡片 */
.glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(30px) saturate(180%);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-shadow:
        0 8px 32px rgba(0, 113, 227, 0.12),
        0 0 0 1px rgba(255, 255, 255, 0.5) inset;
}

/* 轻毛玻璃 */
.glass-light {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 超强毛玻璃（对话框） */
.glass-ultra {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(40px) saturate(180%);
    border-radius: 32px;
    border: 1px solid rgba(255, 255, 255, 0.6);
    box-shadow:
        0 16px 64px rgba(0, 113, 227, 0.15),
        inset 0 1px 1px rgba(255, 255, 255, 0.9);
}
```

### 玻璃层次系统（3层叠加）

1. **基础层**（Background）：渐变背景 + 漂浮装饰球
2. **中层**（Mid-layer）：模糊30px，透明度50%
3. **顶层**（Foreground）：模糊20px，透明度70%

---

## 圆角系统（更圆润）

- 小（按钮/标签）：14px
- 中（卡片/输入框）：18px
- 大（容器）：24px
- 超大（对话框）：32px
- 全（圆按钮）：9999px

**Liquid Glass需要更圆润** — 液体没有尖角，比极简Apple风格增大40%

---

## 阴影与光泽

### 液态阴影（多层叠加）

```css
/* 液态阴影 - 蓝紫光晕 */
.shadow-liquid {
    box-shadow:
        0 4px 16px rgba(0, 113, 227, 0.15),
        0 8px 32px rgba(88, 86, 214, 0.1),
        0 0 0 1px rgba(255, 255, 255, 0.5) inset;
}

/* 悬停增强 */
.shadow-liquid-hover {
    box-shadow:
        0 8px 24px rgba(0, 113, 227, 0.2),
        0 16px 48px rgba(88, 86, 214, 0.15),
        0 0 0 1px rgba(255, 255, 255, 0.7) inset;
}
```

### 内发光（内部光泽）

```css
.glow-inner {
    box-shadow:
        inset 0 1px 1px rgba(255, 255, 255, 0.8),
        inset 0 -1px 1px rgba(0, 0, 0, 0.05);
}
```

### 顶部高光线

```css
.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0.8) 50%,
        transparent 100%
    );
}
```

---

## 动效系统

### 动效策略：流体动画（Fluid Motion）

**缓动函数**：`cubic-bezier(0.25, 0.1, 0.25, 1)` — 更流畅的弹性曲线

**时长**：
- 微交互：400-500ms
- 状态转换：600-800ms
- 复杂动画：1000-1200ms
- 背景流动：15000ms（15秒）

### 流体动效类型

1. **Spring弹性**：轻微弹性回弹（scale: 1.02-1.05）
2. **渐变流动**：渐变色背景流动（6-15秒循环）
3. **模糊过渡**：模糊值从20px平滑过渡到40px
4. **漂浮动画**：装饰球缓慢漂浮（20-25秒循环）
5. **边界流动**：边框渐变流动（8秒循环）

### 关键动画示例

```css
/* 背景渐变流动 */
@keyframes gradientFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 按钮渐变流动 */
@keyframes btnGradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 漂浮球 */
@keyframes float {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(50px, 30px) scale(1.1); }
}
```

---

## 组件规范

### 按钮（液态玻璃）

**主按钮**
- 背景：蓝紫渐变 `linear-gradient(135deg, #0071E3 0%, #5856D6 100%)`
- 渐变流动：6秒循环
- 圆角：9999px（完全圆形）
- 内阴影：`inset 0 1px 1px rgba(255, 255, 255, 0.3)`
- 阴影：蓝紫光晕
- 悬停：`scale(1.05) translateY(-2px)` + 增强光晕

**次要按钮**
- 背景：`rgba(255, 255, 255, 0.7)` + `backdrop-filter: blur(20px)`
- 边框：`1px solid rgba(255, 255, 255, 0.4)`
- 内发光：微妙
- 悬停：透明度变60% + 增强模糊 + `scale(1.03)`

### 输入框（毛玻璃输入）

- 背景：`rgba(255, 255, 255, 0.5)` + `backdrop-filter: blur(20px)`
- 边框：`1px solid rgba(0, 113, 227, 0.3)`
- 圆角：18px
- 焦点：边框渐变 + 蓝色光晕（6px）+ 增强模糊30px
- 内发光：`inset 0 1px 1px rgba(255, 255, 255, 0.5)`

### 卡片（多层玻璃）

```css
.glass-card {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(30px) saturate(180%);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.4);
    padding: 32px;
    box-shadow:
        0 8px 32px rgba(0, 113, 227, 0.12),
        0 0 0 1px rgba(255, 255, 255, 0.5) inset;
    transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.glass-card:hover {
    transform: translateY(-4px) scale(1.01);
    backdrop-filter: blur(40px) saturate(200%);
    box-shadow:
        0 16px 48px rgba(0, 113, 227, 0.18),
        0 0 0 1px rgba(255, 255, 255, 0.6) inset;
}
```

### 对话框（超级玻璃）

```css
.glass-dialog {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(40px) saturate(180%);
    border-radius: 32px;
    border: 1px solid rgba(255, 255, 255, 0.6);
    box-shadow:
        0 16px 64px rgba(0, 113, 227, 0.15),
        inset 0 1px 1px rgba(255, 255, 255, 0.9);
    padding: 24px;
}
```

### 标签

- 背景：10-20%透明度的语义色
- 模糊：`backdrop-filter: blur(10px)`
- 圆角：14px
- 边框：`1px solid rgba(255, 255, 255, 0.3)`

---

## 装饰元素

### 液态装饰球（Liquid Orbs）

```css
.orb {
    position: fixed;
    border-radius: 50%;
    background: linear-gradient(135deg, #0071E3, #5856D6, #AF52DE);
    filter: blur(80px);
    opacity: 0.25;
    pointer-events: none;
    animation: float 20s ease-in-out infinite;
}

/* 3个装饰球 */
.orb-1 { width: 600px; height: 600px; top: -200px; right: -200px; }
.orb-2 { width: 500px; height: 500px; bottom: -150px; left: -150px; }
.orb-3 { width: 400px; height: 400px; top: 50%; left: 50%; }
```

### 渐变流动边框

```css
.border-gradient-flow {
    position: relative;
}

.border-gradient-flow::before {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 26px;
    background: linear-gradient(135deg, #0071E3, #5856D6, #AF52DE);
    background-size: 300% 300%;
    animation: borderFlow 8s linear infinite;
    z-index: -1;
}
```

---

## 页面布局

### 主背景

```css
body {
    background: linear-gradient(135deg, #F5F5F7 0%, #E8E8ED 100%);
    background-size: 400% 400%;
    animation: gradientFlow 15s ease infinite;
}
```

### 侧边栏（毛玻璃侧边栏）

- 背景：`rgba(255, 255, 255, 0.5)` + `backdrop-filter: blur(30px)`
- 右边框：`1px solid rgba(255, 255, 255, 0.3)`
- 内阴影：左侧微妙阴影（深度感）

### 主内容区（浮动玻璃层）

- 3层卡片叠加
- 每层透明度递减（70% → 60% → 50%）
- 模糊强度递增（20px → 30px → 40px）

---

## 设计原则总结

### ✅ DO（应该做的）

1. **大量使用毛玻璃** — backdrop-filter: blur(20-40px) + 饱和度增强
2. **半透明背景** — rgba(255, 255, 255, 0.5-0.7)
3. **渐变色彩** — 蓝紫粉橙的流动渐变
4. **流体动效** — 500-1200ms的流畅动画
5. **超大圆角** — 14-32px，液体无尖角
6. **多层叠加** — 3-5层玻璃产生深度
7. **微妙光泽** — 内发光、高光、反射
8. **装饰球** — 3个大型模糊球体在背景漂浮
9. **渐变动画** — 所有渐变色缓慢流动
10. **弹性交互** — 悬停时轻微放大（scale: 1.02-1.05）

### ❌ DON'T（不应该做的）

1. **不使用纯色背景** — 必须渐变
2. **不使用不透明表面** — 必须半透明
3. **不使用小圆角** — 最小14px
4. **不使用快速动画** — 最小400ms
5. **不使用实边框** — 用光泽边框或半透明边框
6. **不过度模糊** — 20-40px即可，不是100px
7. **不使用纯黑/纯白** — 必须有透明度
8. **不使用静态背景** — 必须流动动画
9. **不使用单调色彩** — 必须渐变
10. **不过度装饰** — 液态球3个即可，不是满屏

---

## 决策日志

| 日期 | 决策 | 理由 |
|------|------|------|
| 2026-03-25 | 创建Liquid Glass设计系统 | 用户要求苹果软件主流的Liquid Glass液态玻璃风格 |
| 2026-03-25 | 选择渐变色彩系统 | 液态玻璃的核心特征，产生流动感 |
| 2026-03-25 | 使用19px标准正文字号 | 比极简Apple风格更大，配合毛玻璃效果更易读 |
| 2026-03-25 | 圆角14-32px | 液体无尖角，比极简风格增大40% |
| 2026-03-25 | 动效500-1200ms | 流体动画需要更慢的速度，营造液态感 |
| 2026-03-25 | 添加3个装饰球 | 产生深度和动感，不过度装饰 |
| 2026-03-25 | 背景渐变流动15秒循环 | 缓慢流动，营造梦幻氛围 |
| 2026-03-25 | 毛玻璃blur(20-40px) | 产生液态玻璃效果，不过度模糊 |

---

## 参考资料

- [Apple Design Resources - Liquid Glass](https://developer.apple.com/design/resources/)
- [Glassmorphism in UI Design](https://ui.glass/glossary)
- [iOS 26 Design Trends](https://developer.apple.com/ios/whats-new/)
- [visionOS Design Guidelines](https://developer.apple.com/visionos/design/)

---

**版本**：v2.0 (Liquid Glass)
**最后更新**：2026-03-25
**创建者**：Claude Code /design-consultation skill
**状态**：✅ 已批准，准备实施

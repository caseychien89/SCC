# 職能發展學院 - 卡片網格組件技術需求

## 1. 組件概述

### 1.1 組件名稱
- **中文名稱**: 課程卡片網格
- **英文名稱**: Course Card Grid
- **組件類型**: 響應式網頁元素

### 1.2 功能描述
展示職能發展學院課程或服務項目的卡片式網格佈局，支援響應式設計，適配不同裝置螢幕尺寸。

## 2. 設計規格

### 2.1 桌面版 (Desktop) - 1200px+
- **容器寬度**: 1226px (最大寬度)
- **內邊距**: 64px
- **卡片排列**: 3列2行 (共6張卡片)
- **卡片間距**: 64px (水平與垂直)
- **卡片尺寸**: 301.33px 寬度，高度自適應

### 2.2 平板版 (Tablet) - 768px ~ 1199px
- **容器寬度**: 100% (最大 768px)
- **內邊距**: 32px
- **卡片排列**: 2列3行
- **卡片間距**: 32px
- **卡片尺寸**: 填滿可用空間

### 2.3 行動版 (Mobile) - 767px 以下
- **容器寬度**: 100%
- **內邊距**: 16px
- **卡片排列**: 1列6行 (垂直堆疊)
- **卡片間距**: 24px
- **卡片尺寸**: 填滿可用空間

## 3. 卡片組件規格

### 3.1 卡片結構
```
Card
├── Icon Container (32x32px)
│   └── SVG Icon (26.67x26.67px)
└── Content Container
    ├── Title (標題)
    └── Description (描述文字)
```

### 3.2 卡片內部佈局
- **佈局方向**: 水平排列 (icon + content)
- **圖示與內容間距**: 24px
- **標題與描述間距**: 8px
- **內容區間距**: 16px

### 3.3 響應式卡片調整
- **桌面版**: 水平佈局 (圖示在左，文字在右)
- **平板版**: 保持水平佈局，縮小間距
- **行動版**: 可選垂直佈局 (圖示在上，文字在下)

## 4. 視覺樣式

### 4.1 字體規格
```css
/* 標題樣式 */
.card-title {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 24px;
  line-height: 1.2;
  letter-spacing: -2%;
  color: #1E1E1E;
}

/* 描述文字樣式 */
.card-description {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 16px;
  line-height: 1.4;
  color: #757575;
}
```

### 4.2 顏色規範
- **背景色**: #FFFFFF (白色)
- **主要文字**: #1E1E1E (深灰)
- **次要文字**: #757575 (中灰)
- **圖示顏色**: #1E1E1E (深灰)
- **圖示描邊**: 3px

### 4.3 響應式字體調整
```css
/* 平板版字體調整 */
@media (max-width: 1199px) {
  .card-title { font-size: 20px; }
  .card-description { font-size: 14px; }
}

/* 行動版字體調整 */
@media (max-width: 767px) {
  .card-title { font-size: 18px; }
  .card-description { font-size: 14px; }
}
```

## 5. 技術實作需求

### 5.1 HTML 結構
```html
<section class="course-card-grid">
  <div class="container">
    <div class="card-grid">
      <article class="course-card">
        <div class="card-icon">
          <svg><!-- 課程圖示 --></svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">課程標題</h3>
          <p class="card-description">課程描述內容...</p>
        </div>
      </article>
      <!-- 重複5次 -->
    </div>
  </div>
</section>
```

### 5.2 CSS Grid 佈局
```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 64px;
  padding: 64px;
}

/* 平板版佈局 */
@media (max-width: 1199px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 32px;
    padding: 32px;
  }
}

/* 行動版佈局 */
@media (max-width: 767px) {
  .card-grid {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 16px;
  }
}
```

### 5.3 Flexbox 卡片佈局
```css
.course-card {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

/* 行動版垂直佈局選項 */
@media (max-width: 767px) {
  .course-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}
```

## 6. 無障礙設計 (Accessibility)

### 6.1 語意化標籤
- 使用 `<section>` 包裝整個組件
- 使用 `<article>` 標記每張卡片
- 使用 `<h3>` 標記卡片標題
- 使用 `<p>` 標記描述內容

### 6.2 ARIA 屬性
```html
<section class="course-card-grid" aria-label="課程介紹">
  <article class="course-card" role="article">
    <div class="card-icon" aria-hidden="true">
      <svg role="img" aria-label="課程圖示">...</svg>
    </div>
    <div class="card-content">
      <h3 class="card-title">課程標題</h3>
      <p class="card-description">課程描述</p>
    </div>
  </article>
</section>
```

### 6.3 鍵盤導航
- 確保所有互動元素可透過 Tab 鍵存取
- 提供適當的 focus 狀態樣式

## 7. 效能最佳化

### 7.1 圖片最佳化
- SVG 圖示使用內嵌方式減少 HTTP 請求
- 提供多種圖示尺寸適應不同螢幕密度
- 使用 `loading="lazy"` 延遲載入非關鍵圖片

### 7.2 CSS 最佳化
- 使用 CSS Grid 和 Flexbox 避免複雜的 float 佈局
- 採用 mobile-first 的媒體查詢策略
- 最小化重排和重繪

## 8. 瀏覽器支援

### 8.1 現代瀏覽器支援
- Chrome 57+
- Firefox 52+
- Safari 10.1+
- Edge 16+

### 8.2 向下相容
- 提供 CSS Grid 的 Flexbox fallback
- 使用 PostCSS 自動添加 vendor prefixes

## 9. 測試需求

### 9.1 響應式測試
- 測試斷點: 320px, 768px, 1024px, 1200px, 1920px
- 確保在各種螢幕尺寸下正常顯示

### 9.2 無障礙測試
- 使用螢幕閱讀器測試
- 鍵盤導航測試
- 色彩對比度檢測

### 9.3 效能測試
- Core Web Vitals 指標檢測
- 行動裝置載入速度測試

## 10. 維護與擴展

### 10.1 內容管理
- 卡片內容應可透過 CMS 動態管理
- 支援卡片數量的彈性調整 (4-12張)

### 10.2 樣式客製化
- 提供 CSS 變數支援主題切換
- 模組化 SCSS 結構便於維護

### 10.3 功能擴展
- 預留卡片點擊事件處理
- 支援未來可能的篩選和排序功能
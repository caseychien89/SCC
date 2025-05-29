--- /dev/null
+++ b/accordion技術需求.md
@@ -0,0 +1,240 @@
+# Accordion 元件技術需求規格
+
+## 1. 目的 (Objective)
+本文件旨在定義一個可重複使用的 Accordion (手風琴) UI 元件的技術需求。此元件將用於顯示可折疊的內容區塊，每個區塊包含標題和日期。
+
+## 2. 功能需求 (Functional Requirements)
+1.  **Accordion 功能**:
+    *   使用者可以點擊每個項目的標題區域來展開或收合其對應的內容區域。
+    *   一次只應有一個項目內容是展開的。點擊一個項目展開其內容時，其他已展開的項目應自動收合。
+2.  **標題與日期顯示**:
+    *   每個 Accordion 項目都必須同時顯示標題 (title) 和日期 (date)。
+    *   標題內容可能會很長，需要能夠自動換行顯示。
+3.  **預設顯示**:
+    *   頁面載入時，預設顯示第一個 Accordion 項目的內容。
+4.  **內容區域**:
+    *   每個項目的內容區域具有固定的高度。
+    *   如果內容超出固定高度，應提供垂直捲動軸 (scrollbar) 或將多餘內容截斷 (本規格建議使用捲動軸)。
+5.  **資料來源**:
+    *   所有 Accordion 項目的資料 (標題、日期、內容) 將從資料庫獲取，並透過後端模板引擎 (如 Jinja) 動態載入。
+6.  **可測試性**:
+    *   元件應能獨立運作於一個基本的 HTML 頁面中，以便於測試。
+7.  **Jinja 整合**:
+    *   HTML 結構需設計成易於透過 Jinja 模板語言進行迭代和資料綁定。
+
+## 3. 技術規格 (Technical Specifications)
+
+### 3.1 HTML 結構 (HTML Structure)
+建議採用以下 HTML 結構。此結構易於使用 CSS 設定樣式，並透過 JavaScript 控制行為。
+
+```html
+<div class="accordion-container">
+    <!-- Accordion Item 1 (預設展開) -->
+    <div class="accordion-item is-active">
+        <div class="accordion-header">
+            <span class="accordion-title">這是第一個項目的標題，這個標題可能會非常長，以至於需要換行顯示才能完整呈現所有文字。</span>
+            <span class="accordion-date">2023-10-26</span>
+        </div>
+        <div class="accordion-content">
+            <p>這是第一個項目的內容。此處的文字是用來填充空間，模擬實際內容。內容區域將具有固定的高度，如果文字過多，將會出現捲動軸。</p>
+            <p>更多內容以測試捲動功能。</p>
+        </div>
+    </div>
+
+    <!-- Accordion Item 2 -->
+    <div class="accordion-item">
+        <div class="accordion-header">
+            <span class="accordion-title">這是第二個項目的標題</span>
+            <span class="accordion-date">2023-10-27</span>
+        </div>
+        <div class="accordion-content">
+            <p>這是第二個項目的內容。此內容較短。</p>
+        </div>
+    </div>
+
+    <!-- Accordion Item 3 -->
+    <div class="accordion-item">
+        <div class="accordion-header">
+            <span class="accordion-title">這是第三個項目的標題，同樣可能包含較多文字。</span>
+            <span class="accordion-date">2023-10-28</span>
+        </div>
+        <div class="accordion-content">
+            <p>這是第三個項目的內容。固定高度的設計有助於保持頁面佈局的一致性。</p>
+        </div>
+    </div>
+    <!-- 更多項目可依此結構添加 -->
+</div>
+```
+*   `.accordion-container`: Accordion 的主要容器。
+*   `.accordion-item`: 代表每一個可折疊的項目。
+    *   `is-active`: 此 class 用於標識當前展開的項目。
+*   `.accordion-header`: 項目的標題區域，使用者將點擊此區域來觸發展開/收合。
+*   `.accordion-title`: 用於顯示項目標題。
+*   `.accordion-date`: 用於顯示項目日期。
+*   `.accordion-content`: 項目的內容區域，預設為隱藏，展開時顯示。
+
+### 3.2 CSS 樣式 (CSS Styling)
+
+```css
+/* 基本樣式 (可根據實際設計調整) */
+.accordion-container {
+    width: 100%;
+    max-width: 600px; /* 範例最大寬度 */
+    margin: 20px auto;
+    border: 1px solid #ccc;
+    border-radius: 4px;
+}
+
+.accordion-item {
+    border-bottom: 1px solid #ccc;
+}
+
+.accordion-item:last-child {
+    border-bottom: none;
+}
+
+.accordion-header {
+    display: flex;
+    justify-content: space-between;
+    align-items: flex-start; /* 確保長標題與日期頂部對齊 */
+    padding: 15px;
+    background-color: #f7f7f7;
+    cursor: pointer;
+    user-select: none; /* 防止文字選取 */
+}
+
+.accordion-header:hover {
+    background-color: #e9e9e9;
+}
+
+.accordion-title {
+    flex-grow: 1; /* 標題佔據主要空間 */
+    margin-right: 15px; /* 與日期之間的間距 */
+    line-height: 1.4; /* 改善多行標題的可讀性 */
+}
+
+.accordion-date {
+    flex-shrink: 0; /* 防止日期被壓縮 */
+    font-size: 0.9em;
+    color: #555;
+    white-space: nowrap; /* 確保日期不換行 */
+}
+
+.accordion-content {
+    max-height: 0;
+    overflow: hidden;
+    padding: 0 15px; /* 左右內邊距，上下由 is-active 控制 */
+    background-color: #fff;
+    box-sizing: border-box;
+    transition: max-height 0.3s ease-out, padding-top 0.3s ease-out, padding-bottom 0.3s ease-out;
+}
+
+.accordion-item.is-active .accordion-content {
+    max-height: 150px; /* 固定的內容高度 */
+    overflow-y: auto;  /* 內容超出時顯示捲動軸 */
+    padding-top: 15px;
+    padding-bottom: 15px;
+}
+
+/* 可選：加入展開/收合指示圖標 */
+.accordion-header::after {
+    content: '+'; /* 預設為收合狀態 */
+    font-size: 1.2em;
+    font-weight: bold;
+    margin-left: 10px;
+    transition: transform 0.3s ease-out;
+}
+
+.accordion-item.is-active .accordion-header::after {
+    content: '−'; /* 展開狀態 */
+    transform: rotate(180deg); /* 如果使用箭頭圖標，可以旋轉 */
+}
+```
+
+### 3.3 JavaScript 行為 (JavaScript Behavior)
+
+```javascript
+document.addEventListener('DOMContentLoaded', function () {
+    const accordionItems = document.querySelectorAll('.accordion-item');
+    const fixedContentHeight = 150; // 與 CSS 中的 max-height 一致
+
+    // 預設展開第一個項目
+    if (accordionItems.length > 0) {
+        const firstItem = accordionItems[0];
+        firstItem.classList.add('is-active');
+        // 不需要手動設定 max-height，CSS 的 .is-active .accordion-content 已處理
+    }
+
+    accordionItems.forEach(item => {
+        const header = item.querySelector('.accordion-header');
+        const content = item.querySelector('.accordion-content');
+
+        header.addEventListener('click', () => {
+            const isActive = item.classList.contains('is-active');
+
+            // 先關閉所有項目
+            accordionItems.forEach(otherItem => {
+                otherItem.classList.remove('is-active');
+                // otherItem.querySelector('.accordion-content').style.maxHeight = '0px'; // CSS transition 會處理
+            });
+
+            // 如果當前點擊的項目不是已展開的，則展開它
+            if (!isActive) {
+                item.classList.add('is-active');
+                // content.style.maxHeight = fixedContentHeight + 'px'; // CSS transition 會處理
+            }
+            // 如果點擊的是已展開的項目，它會在上面的循環中被關閉，實現 toggle 效果
+        });
+    });
+});
+```
+
+## 4. 資料結構範例 (Data Structure Example - for Jinja)
+後端傳遞給 Jinja 模板的資料可能如下列 Python 列表結構所示：
+
+```python
+accordion_data = [
+    {
+        "title": "這是第一個項目的標題，這個標題可能會非常長，以至於需要換行顯示才能完整呈現所有文字。",
+        "date": "2023-10-26",
+        "content": "<p>這是第一個項目的內容。此處的文字是用來填充空間，模擬實際內容。</p><p>內容區域將具有固定的高度，如果文字過多，將會出現捲動軸。</p>"
+    },
+    {
+        "title": "這是第二個項目的標題",
+        "date": "2023-10-27",
+        "content": "<p>這是第二個項目的內容。此內容較短。</p>"
+    },
+    {
+        "title": "這是第三個項目的標題，同樣可能包含較多文字。",
+        "date": "2023-10-28",
+        "content": "<p>這是第三個項目的內容。固定高度的設計有助於保持頁面佈局的一致性。</p>"
+    }
+]
+```
+
+## 5. Jinja 整合建議 (Jinja Integration Suggestions)
+在 Jinja 模板中，可以使用 `for` 迴圈來迭代資料並生成 HTML。
+
+```html+jinja
+<div class="accordion-container">
+    {% for item in accordion_data %}
+    <div class="accordion-item {% if loop.first %}is-active{% endif %}">
+        <div class="accordion-header">
+            <span class="accordion-title">{{ item.title }}</span>
+            <span class="accordion-date">{{ item.date }}</span>
+        </div>
+        <div class="accordion-content">
+            {{ item.content | safe }} {# 假設 content 是 HTML，使用 safe filter #}
+        </div>
+    </div>
+    {% endfor %}
+</div>
+```
+
+## 6. 基本測試頁面範例 (Basic Test Page Example)
+以下是一個完整的 HTML 頁面，包含了上述的 HTML 結構、CSS 樣式和 JavaScript 邏輯，可用於基本測試。
+
+```html
+<!DOCTYPE html>
+<html lang="zh-TW">
+<head>
+    <meta charset="UTF-8">
+    <meta name="viewport" content="width=device-width, initial-scale=1.0">
+    <title>Accordion 測試頁面</title>
+    <style>
+        body {
+            font-family: sans-serif;
+            margin: 0;
+            padding: 20px;
+            background-color: #f0f0f0;
+        }
+        .accordion-container {
+            width: 100%;
+            max-width: 600px;
+            margin: 20px auto;
+            border: 1px solid #ccc;
+            border-radius: 4px;
+            background-color: #fff;
+            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
+        }
+        .accordion-item {
+            border-bottom: 1px solid #eee;
+        }
+        .accordion-item:last-child {
+            border-bottom: none;
+        }
+        .accordion-header {
+            display: flex;
+            justify-content: space-between;
+            align-items: flex-start;
+            padding: 15px;
+            background-color: #f7f7f7;
+            cursor: pointer;
+            user-select: none;
+            transition: background-color 0.2s ease;
+        }
+        .accordion-header:hover {
+            background-color: #e9e9e9;
+        }
+        .accordion-title {
+            flex-grow: 1;
+            margin-right: 15px;
+            line-height: 1.4;
+            font-weight: bold;
+        }
+        .accordion-date {
+            flex-shrink: 0;
+            font-size: 0.9em;
+            color: #555;
+            white-space: nowrap;
+            padding-top: 2px; /* 微調對齊 */
+        }
+        .accordion-content {
+            max-height: 0;
+            overflow: hidden;
+            padding: 0 15px;
+            background-color: #fff;
+            box-sizing: border-box;
+            transition: max-height 0.35s ease-in-out, padding-top 0.35s ease-in-out, padding-bottom 0.35s ease-in-out;
+            color: #333;
+            line-height: 1.6;
+        }
+        .accordion-item.is-active .accordion-content {
+            max-height: 150px; /* 固定內容高度 */
+            overflow-y: auto;
+            padding-top: 15px;
+            padding-bottom: 15px;
+        }
+        .accordion-header::after { /* 指示圖標 */
+            content: '+';
+            font-size: 1.5em; /* 放大圖標 */
+            line-height: 1; /* 確保圖標垂直居中 */
+            font-weight: bold;
+            margin-left: 10px;
+            color: #337ab7;
+            transition: transform 0.35s ease-in-out;
+        }
+        .accordion-item.is-active .accordion-header::after {
+            content: '−';
+            /* transform: rotate(45deg); 如果是 + 號變 x 號 */
+        }
+    </style>
+</head>
+<body>
+
+    <h1>Accordion 元件測試</h1>
+
+    <div class="accordion-container">
+        <!-- Item 1 -->
+        <div class="accordion-item">
+            <div class="accordion-header">
+                <span class="accordion-title">這是第一個項目的標題，這個標題可能會非常長，以至於需要換行顯示才能完整呈現所有文字。</span>
+                <span class="accordion-date">2023-10-26</span>
+            </div>
+            <div class="accordion-content">
+                <p>這是第一個項目的內容。此處的文字是用來填充空間，模擬實際內容。內容區域將具有固定的高度，如果文字過多，將會出現捲動軸。</p>
+                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
+                <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
+            </div>
+        </div>
+
+        <!-- Item 2 -->
+        <div class="accordion-item">
+            <div class="accordion-header">
+                <span class="accordion-title">這是第二個項目的標題</span>
+                <span class="accordion-date">2023-10-27</span>
+            </div>
+            <div class="accordion-content">
+                <p>這是第二個項目的內容。此內容較短。</p>
+            </div>
+        </div>
+
+        <!-- Item 3 -->
+        <div class="accordion-item">
+            <div class="accordion-header">
+                <span class="accordion-title">這是第三個項目的標題，同樣可能包含較多文字。</span>
+                <span class="accordion-date">2023-10-28</span>
+            </div>
+            <div class="accordion-content">
+                <p>這是第三個項目的內容。固定高度的設計有助於保持頁面佈局的一致性。</p>
+                <p>為了測試捲動，這裡也加入一些額外文字。如果內容不多，捲動軸不會出現。</p>
+            </div>
+        </div>
+    </div>
+
+    <script>
+        document.addEventListener('DOMContentLoaded', function () {
+            const accordionItems = document.querySelectorAll('.accordion-container .accordion-item');
+            // const fixedContentHeight = 150; // CSS 已經定義了
+
+            // 預設展開第一個項目
+            if (accordionItems.length > 0) {
+                const firstItem = accordionItems[0];
+                // 檢查是否已經由 Jinja (或其他方式) 預設添加 is-active
+                if (!firstItem.classList.contains('is-active')) {
+                    firstItem.classList.add('is-active');
+                }
+            }
+
+            accordionItems.forEach(item => {
+                const header = item.querySelector('.accordion-header');
+                // const content = item.querySelector('.accordion-content'); // 不直接操作 style.maxHeight
+
+                if (header) { // 確保 header 存在
+                    header.addEventListener('click', () => {
+                        const currentlyActive = item.classList.contains('is-active');
+
+                        // 先關閉所有項目
+                        accordionItems.forEach(otherItem => {
+                            if (otherItem !== item || currentlyActive) { // 如果是當前項目且已展開，則關閉它
+                                otherItem.classList.remove('is-active');
+                            }
+                        });
+
+                        // 如果當前點擊的項目原先不是展開的，則展開它
+                        if (!currentlyActive) {
+                            item.classList.add('is-active');
+                        }
+                    });
+                }
+            });
+        });
+    </script>
+
+</body>
+</html>
+```
+
+---
+**文件結束**
+
+

Gemini Code Assist supports plain-text files. Other file types, like PDFs and images, are not directly supported at this time. If a version of the file is available in a plain text format, please use that instead, or copy the relevant contents from the file into your prompt.

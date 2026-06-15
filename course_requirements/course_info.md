# IT5425 Data Management and Visualization

_Quản trị dữ liệu và trực quan hoá_

## Course Information

| Field | Details |
| --- | --- |
| Credits | 2(2-1-0-4) |
| Prerequisite | None |
| Pre-courses | None |
| Corequisite | None |

## Objectives

This course provides basic foundations on data management and visualization. Students are trained to design and propose solutions to store, manage, and integrate data, and to visually present a story from the data and insights. Real-life applications and datasets are used for practice with Python and its libraries. By the end of the course, students can choose appropriate solutions and tools for storing and visualizing data in real-world problems.

## Mục tiêu

Môn học cung cấp nền tảng về quản trị và trực quan hoá dữ liệu, từ tổ chức và làm sạch dữ liệu đến phân tích thăm dò và kể chuyện bằng dữ liệu. Sinh viên thực hành trên Python và tập dữ liệu thực tế.

## Course Content

_Nội dung giảng dạy_

### Chapter 1: Overview of Data Visualization

_Chương 1: Tổng quan về trực quan hoá dữ liệu_

1. Introduction
2. Why data visualization
3. Role of data visualization
4. Types of data visualization

### Chapter 2: Visual Models and Encoding

_Chương 2: Mô hình và mã hoá trực quan_

1. Properties of data and measurement levels
2. Visual marks
3. Visual channels
4. Visual encoding

### Chapter 3: Graphical Perception

_Chương 3: Nhận thức trực quan bằng đồ hoạ_

1. Signal detection
2. Magnitude estimation
3. Pre-attentive processing
4. Using multiple visual encodings
5. Gestalt grouping principles

### Chapter 4: Visualization for Multi-dimensional Data

_Chương 4: Trực quan hoá dữ liệu đa chiều_

1. Coordinate systems and axes
2. Visualizing amounts
3. Visualizing distributions
4. Visualizing proportions
5. Visualizing relationships
6. Visualizing trends
7. Visualizing uncertainty

### Chapter 5: Visualization for Graphs

_Chương 5: Trực quan hoá dữ liệu đồ thị_

1. Graph data properties
2. Mechanisms for graph visualization

### Chapter 6: Principles of Figure Design

_Chương 6: Nguyên tắc thiết kế hình vẽ_

1. The principle of proportional ink
2. Handling overlapping points
3. Issues in the use of color
4. Multi-panel figures
5. Titles, captions, and tables
6. Balancing data and context
7. Problems with 3D charts

### Chapter 7: Map Visualization

_Chương 7: Trực quan hoá bản đồ_

1. Theoretical foundations
2. Types of map data visualization

### Chapter 8: Interactive Visualization

_Chương 8: Trực quan hoá tương tác_

1. Introduction
2. Design principles
3. Interaction techniques: filtering, zooming, selection, view transformation
4. Animated visualization
5. Tools and libraries
6. Practical applications

### Chapter 9: Storytelling with Data

_Chương 9: Kể chuyện bằng dữ liệu_

1. Introduction
2. Fundamental principles of data storytelling
3. Visualization techniques for storytelling
4. Narrative styles in data storytelling
5. Interaction and exploration in storytelling

## Capstone Project Guidelines

_Hướng dẫn bài tập lớn_

### Project Requirements

_Yêu cầu dự án_

Build a dashboard for a specific dataset.

- **Tools:** Power BI, Apache Superset, Tableau, Python (Plotly, Dash, Streamlit), or equivalent.
- **Preferred tool:** Streamlit.
- **Data source:** The dataset must be findable on Google Dataset Search.

### Deliverables

| Item | Description |
| --- | --- |
| Source code | Dashboard source code, or project file if using Power BI or Tableau |
| Presentation slides | Slides for dashboard demo |
| Report | Report that clearly analyzes the visualization techniques and guidelines from the course and how they were applied in the dashboard |

## Report Guideline: "Technique Application" Section

_Hướng dẫn viết phần "Áp dụng kỹ thuật" trong báo cáo_

The report must include a clear analysis of the visualization techniques and principles covered in the course, and how they were applied to each chart or page in the dashboard. Use the structure below and include a subsection for each relevant chapter.

### Suggested Structure Per Chapter

```markdown
### Chapter X: [Chapter title]

#### Techniques / Principles Applied

- List the relevant items (X.1, X.2, ...) from the chapter that relate to your dashboard.

#### How Applied in the Dashboard

- Describe specifically: which chart/page, which technique, and why that choice was made.
- You may include screenshots.

#### Notes / Adjustments

- If you deviated from the theory, explain why.
```

### What to Cover by Chapter

| Chapter | What to address in the report |
| --- | --- |
| Ch. 1 | Why you chose the dataset; role of visualization in the problem; types of visualization used, such as exploratory or explanatory visualization. |
| Ch. 2 | Data types (nominal, ordinal, quantitative); visual marks (points, lines, areas) and visual channels (position, size, color) used; rationale for encoding each variable. |
| Ch. 3 | Use of pre-attentive processing; Gestalt principles, such as proximity and similarity, in layout; magnitude estimation, such as length vs. area vs. angle, and whether each chart choice is appropriate. |
| Ch. 4 | Chart types for amounts, distributions, proportions, relationships, and trends; coordinate systems; whether uncertainty was visualized. |
| Ch. 5 | If using graph data: graph data properties; layout mechanism, such as force-directed or hierarchical; node/edge representation. |
| Ch. 6 | Proportional ink; handling overlap; use of color, including palette and accessibility; multi-panel figures; titles and captions; data-context balance; avoiding unnecessary 3D charts. |
| Ch. 7 | If using maps: type of map visualization; foundations, such as projection and geocoding; how data is encoded on the map. |
| Ch. 8 | Interaction techniques: filter, zoom, select, and change view; use of animation; tools/libraries used. |
| Ch. 9 | Story structure; storytelling principles; narrative style; interaction and exploration in the story. |

> **Note:** You do not need to cover every chapter. Only include chapters relevant to your dashboard; you may skip others or briefly state why they do not apply.

Teacher uploaded resources: https://drive.google.com/drive/folders/1SJCffHKzHtQ7pzny9BETTNn-vQ1CND32
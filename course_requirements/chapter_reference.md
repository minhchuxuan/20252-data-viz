# IT5425 Chapter Reference

This file is the local course-content reference used to design the dashboard story, report, and slide deck. `course_info.md` remains the source of truth for teacher requirements; this file expands those chapters into practical design checkpoints for the Paris 2024 Olympic dashboard.

## Chapter 1: Overview of Data Visualization

Course topics:

1. Introduction
2. Why data visualization
3. Role of data visualization
4. Types of data visualization

Dashboard implications:

- Explain why Paris 2024 is a suitable real-life dataset.
- State the problem that visualization solves: medal tables alone hide geography, specialization, athlete distributions, and venue patterns.
- Combine explanatory visualization with exploratory interaction.
- Use multiple visualization types: map, table, bar, scatter, heatmap, treemap, flow graph, histogram, boxplot, timeline.

Storytelling use:

- Begin with global context.
- Move from country competition to sport specialization.
- Humanize the story through athlete demographics.
- Close with venue geography and records.

## Chapter 2: Visual Models and Encoding

Course topics:

1. Properties of data and measurement levels
2. Visual marks
3. Visual channels
4. Visual encoding

Dashboard implications:

- Nominal data: NOC, country, discipline, event, venue, gender, medal type.
- Ordinal data: medal table rank, medal hierarchy.
- Quantitative data: medal totals, athlete count, age, event count, competition days, record count.
- Temporal data: first competition date and last competition date.
- Geographic data: venue latitude/longitude and country geometry.

Encoding decisions:

- Position: scatter plots, maps, timelines.
- Length: medal bars, delta bars, record bars.
- Color hue: medal type, gender, gain/loss.
- Color intensity: choropleth, heatmap, record scale.
- Size/area: venue bubbles, treemap, scatter bubble size.

## Chapter 3: Graphical Perception

Course topics:

1. Signal detection
2. Magnitude estimation
3. Pre-attentive processing
4. Using multiple visual encodings
5. Gestalt grouping principles

Dashboard implications:

- Use bars for precise magnitude comparison because length is easier to compare than area or angle.
- Use color intensity for pre-attentive detection of high medal density on maps and heatmaps.
- Use similarity and proximity in heatmaps and multi-panel sections.
- Avoid relying on pie-angle comparison for key claims.
- Use labels and hover details where color or area is not precise enough.

## Chapter 4: Visualization for Multi-dimensional Data

Course topics:

1. Coordinate systems and axes
2. Visualizing amounts
3. Visualizing distributions
4. Visualizing proportions
5. Visualizing relationships
6. Visualizing trends
7. Visualizing uncertainty

Dashboard implications:

- Amounts: medal table, medal bars, discipline medal records, record bars.
- Distributions: athlete age histogram, age boxplots by discipline.
- Proportions: gender balance by discipline, treemap.
- Relationships: delegation size vs medals, event count vs competition days.
- Trends/change: Paris-vs-Tokyo medal delta, competition start timeline.
- Uncertainty: not central because the data are completed event records, not sampled estimates.

## Chapter 5: Visualization for Graphs

Course topics:

1. Graph data properties
2. Mechanisms for graph visualization

Dashboard implications:

- Use a derived flow graph because the raw data are relational rather than a natural social network.
- Nodes: NOC, discipline, medal color.
- Links: athlete-medal record counts.
- Mechanism: Sankey layout for flow magnitude.
- Be explicit that this is a categorical flow graph, not athlete-to-athlete connectivity.

## Chapter 6: Principles of Figure Design

Course topics:

1. The principle of proportional ink
2. Handling overlapping points
3. Issues in the use of color
4. Multi-panel figures
5. Titles, captions, and tables
6. Balancing data and context
7. Problems with 3D charts

Dashboard implications:

- Bars start at zero and use proportional length.
- Scatter plots cap bubble sizes and use tooltips for detail.
- Medal colors are consistent across pages.
- Avoid 3D charts.
- Use charts and tables together when both pattern and exact value matter.
- Use story cards and captions to add context without cluttering charts.

## Chapter 7: Map Visualization

Course topics:

1. Theoretical foundations
2. Types of map data visualization

Dashboard implications:

- World choropleth: total medals by country/NOC.
- Venue bubble map: venues by latitude/longitude with athlete volume and medal activity.
- Handle NOC-to-ISO code differences for country maps.
- Exclude records without coordinates from map layers, but retain them for non-map analysis.

## Chapter 8: Interactive Visualization

Course topics:

1. Introduction
2. Design principles
3. Interaction techniques: filtering, zooming, selection, view transformation
4. Animated visualization
5. Tools and libraries
6. Practical applications

Dashboard implications:

- Sidebar filters: NOC, discipline, medal color, gender, age, medal status.
- View transformation: top-N slider and medal sort selector.
- Details-on-demand: Plotly hover tooltips.
- Zoom/pan: Plotly chart controls and map controls.
- Animation is not used because the dataset is a completed event snapshot and filters are more analytically useful.

## Chapter 9: Storytelling with Data

Course topics:

1. Introduction
2. Fundamental principles of data storytelling
3. Visualization techniques for storytelling
4. Narrative styles in data storytelling
5. Interaction and exploration in storytelling

Dashboard story arc:

1. **Opening Lens:** global scale and medal geography.
2. **Medal Race:** who led and who changed from Tokyo to Paris.
3. **Sport Specialization:** country-discipline strengths.
4. **Athlete Lens:** age, gender, workload, and medals.
5. **Paris Geography:** venue spread, competition rhythm, and records.

Storytelling principles:

- Start broad, then narrow.
- Pair every page with one guiding question.
- Use interaction for exploration after the narrative path is clear.
- Avoid generic chart galleries; every chart should answer a course-relevant question.

# SPED Services Analytics Dashboard - User Guide

## Overview

The Analytics Dashboard provides powerful data visualization and pivot table capabilities for analyzing SPED service data. It reads from the same database as the Services Aggregator but presents the data in interactive charts, tables, and reports.

## Getting Started

### Prerequisites
1. Run `install_requirements.bat` to install Streamlit and dependencies
2. Use Services Aggregator to import data from email first
3. Ensure `aggregated_services.db` exists with data

### Launching the Dashboard
```batch
run_dashboard.bat
```
This opens the dashboard in your web browser at http://localhost:8501

## Dashboard Features

### 1. Overview Mode
Quick metrics and insights:
- **Total Students** - Number of unique students served
- **Total Sessions** - All recorded service sessions
- **Total Hours** - Sum of all service durations
- **Average Score** - Mean score across all sessions with scores
- **Top Students** - Bar chart of most frequently served students
- **Service Distribution** - Sessions by service type

### 2. Pivot Tables
Interactive Excel-like pivot tables:

#### How to Use:
1. **Select Rows** - Choose dimensions to group by (student, service, goal, etc.)
2. **Select Columns** - Optional column dimensions for cross-tabulation
3. **Select Values** - What to aggregate (duration, score, count)
4. **Select Aggregation** - How to combine (sum, average, count, min, max)

#### Example Pivot Tables:

**Student Service Hours by Week:**
- Rows: Student
- Columns: Week
- Values: Duration
- Aggregation: Sum

**Average Scores by Goal:**
- Rows: Goal ID
- Columns: (none)
- Values: Score
- Aggregation: Average

**Service Frequency by Day:**
- Rows: Weekday
- Columns: Service
- Values: Count
- Aggregation: Count

#### Features:
- Color-coded cells (heatmaps)
- Totals row/column
- Export to CSV
- Real-time updates

### 3. Visualizations

#### Service Trends Tab
- **Line Chart** - Service frequency over time
- **Pie Chart** - Total duration by service type

#### Student Progress Tab
- Select individual student or "All Students"
- **Score Trend** - Score progression with trend line
- **Duration Distribution** - Histogram of session lengths

#### Goal Tracking Tab
- **Bar Chart** - Average score by goal with target line
- **Details Table** - Goal statistics (sessions, duration, scores)

#### Time Analysis Tab
- **Activity Heatmap** - Sessions by hour and day of week
- **Weekly Summary** - Students served and average scores by week

### 4. Detailed Data View

Advanced filtering and data exploration:

#### Filters:
- **Student** - Select one or multiple students
- **Service** - Filter by service types
- **Date Range** - Specify start and end dates
- **Minimum Score** - Show only sessions above threshold

#### Features:
- View filtered records count
- Sortable columns
- Export filtered data to CSV
- Formatted display (duration in minutes, scores as percentages)

## Practical Use Cases

### For Administrators

**Monthly Compliance Report:**
1. Go to Pivot Tables
2. Set Rows: Student, Columns: Service
3. Values: Duration, Aggregation: Sum
4. Export for compliance documentation

**Goal Achievement Analysis:**
1. Go to Visualizations → Goal Tracking
2. Review average scores vs targets
3. Identify goals needing intervention

### For Teachers

**Student Progress Review:**
1. Go to Visualizations → Student Progress
2. Select specific student
3. Review score trends and session consistency

**Service Delivery Patterns:**
1. Go to Visualizations → Time Analysis
2. Check heatmap for service gaps
3. Identify optimal service times

### For Special Ed Coordinators

**Program Effectiveness:**
1. Go to Overview for quick metrics
2. Check Pivot Tables for service distribution
3. Use Detailed View for specific student drill-downs

**IEP Meeting Preparation:**
1. Filter Detailed Data by student
2. Export student's service history
3. Generate charts from Visualizations tab

## Tips & Tricks

### Pivot Table Best Practices
- Start simple with one row dimension
- Add columns for comparison
- Use color gradients to spot patterns
- Export complex pivots for Excel analysis

### Performance Optimization
- Use date filters to limit data range
- Refresh data after new imports
- Close unused browser tabs

### Data Quality Checks
- Look for missing scores in Overview
- Check for duplicate entries (should be prevented)
- Verify duration values are reasonable

## Keyboard Shortcuts
- **F5** - Refresh dashboard
- **Ctrl+F** - Search within page
- **Ctrl+P** - Print current view

## Troubleshooting

### No Data Showing
1. Verify Services Aggregator has imported data
2. Check `aggregated_services.db` exists
3. Click "Refresh Data" button

### Slow Performance
1. Reduce date range in filters
2. Close other browser tabs
3. Restart dashboard with `run_dashboard.bat`

### Export Issues
1. Check browser download settings
2. Ensure sufficient disk space
3. Try different browser if issues persist

## Advanced Features

### Custom Date Ranges
- Use Detailed View date picker
- Filter by academic terms
- Compare year-over-year data

### Multi-Student Analysis
- Select multiple students in filters
- Compare progress across cohorts
- Identify service patterns

### Goal-Based Reporting
- Filter by goal_id in pivot tables
- Track goal-specific metrics
- Generate goal achievement reports

## Dashboard Workflow

### Daily Use
1. Launch dashboard
2. Check Overview for new data
3. Review any alerts or anomalies

### Weekly Reporting
1. Generate pivot table for week
2. Export service summary
3. Share with team

### Monthly Analysis
1. Full data review in Visualizations
2. Generate compliance reports
3. Export detailed records for filing

## Integration with Other Apps

### With Services Tracker
- Tracker sends data via email
- Aggregator imports to database
- Dashboard visualizes the data

### With QR Code Maker
- QR codes define service types
- Goal IDs link to QR batches
- Track QR usage patterns

### With Services Aggregator
- Aggregator manages data import
- Dashboard reads same database
- Run aggregator before dashboard

## Security & Privacy

- Data stays local on your computer
- No cloud uploads
- Browser-based but localhost only
- Close dashboard when not in use

## Updates & Maintenance

### Adding New Visualizations
- Edit Services_Dashboard.py
- Add new chart types in create_visualizations()
- Restart dashboard to see changes

### Database Changes
- Schema updates in Aggregator
- Dashboard auto-adapts to new fields
- Backward compatible with old data

---

*For technical support, refer to IMPLEMENTATION_BRIEF.md*
*Last Updated: [Current Date]*
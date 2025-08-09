# -*- coding: utf-8 -*-
"""
SPED Services Analytics Dashboard
Created for comprehensive data analysis and reporting
Uses Streamlit for interactive visualizations and pivot tables
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="SPED Services Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
@st.cache_resource
def get_connection():
    """Create a cached database connection"""
    return sqlite3.connect("aggregated_services.db", check_same_thread=False)

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_data():
    """Load services data from database"""
    conn = get_connection()
    query = """
    SELECT 
        id,
        timestamp,
        student,
        service,
        duration,
        event,
        score,
        goal_id,
        device_id,
        source_email,
        schema_version,
        imported_at
    FROM services
    ORDER BY timestamp DESC
    """
    df = pd.read_sql_query(query, conn)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['week'] = df['timestamp'].dt.isocalendar().week
    df['month'] = df['timestamp'].dt.strftime('%Y-%m')
    df['weekday'] = df['timestamp'].dt.day_name()
    
    return df

def create_overview_metrics(df):
    """Create overview metric cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_students = df['student'].nunique()
        st.metric(
            "Total Students",
            total_students,
            delta=f"Active this week: {df[df['timestamp'] > datetime.now() - timedelta(days=7)]['student'].nunique()}"
        )
    
    with col2:
        total_sessions = len(df)
        sessions_this_week = len(df[df['timestamp'] > datetime.now() - timedelta(days=7)])
        st.metric(
            "Total Sessions",
            total_sessions,
            delta=f"+{sessions_this_week} this week"
        )
    
    with col3:
        total_hours = df['duration'].sum() / 60 if not df.empty else 0
        st.metric(
            "Total Hours",
            f"{total_hours:.1f}",
            delta=f"Avg: {df['duration'].mean():.0f} min" if not df.empty else "0 min"
        )
    
    with col4:
        avg_score = df['score'].mean() if not df.empty else 0
        score_trend = "📈" if avg_score > 75 else "📊" if avg_score > 50 else "📉"
        st.metric(
            f"Average Score {score_trend}",
            f"{avg_score:.1f}%" if avg_score > 0 else "N/A",
            delta=f"Goals tracked: {df['goal_id'].notna().sum()}"
        )

def create_pivot_table(df):
    """Create interactive pivot table"""
    st.subheader("📊 Interactive Pivot Table")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rows = st.multiselect(
            "Rows (Group by):",
            ["student", "service", "goal_id", "device_id", "weekday", "week", "month"],
            default=["student"]
        )
    
    with col2:
        cols = st.multiselect(
            "Columns:",
            ["service", "event", "week", "month", "weekday", "device_id"],
            default=["service"] if "service" not in rows else []
        )
    
    with col3:
        values = st.selectbox(
            "Values:",
            ["duration", "score", "count"],
            format_func=lambda x: {
                "duration": "Duration (min)",
                "score": "Score (%)",
                "count": "Session Count"
            }.get(x, x)
        )
    
    with col4:
        agg_func = st.selectbox(
            "Aggregation:",
            ["mean", "sum", "count", "min", "max"],
            format_func=lambda x: {
                "mean": "Average",
                "sum": "Total",
                "count": "Count",
                "min": "Minimum",
                "max": "Maximum"
            }.get(x, x)
        )
    
    if rows:
        try:
            # Handle the special "count" value
            if values == "count":
                pivot_values = "id"  # Use any column for counting
                pivot_agg = "count"
            else:
                pivot_values = values
                pivot_agg = agg_func
            
            # Create pivot table
            if cols:
                pivot = pd.pivot_table(
                    df,
                    values=pivot_values,
                    index=rows,
                    columns=cols,
                    aggfunc=pivot_agg,
                    fill_value=0,
                    margins=True,
                    margins_name="Total"
                )
            else:
                pivot = pd.pivot_table(
                    df,
                    values=pivot_values,
                    index=rows,
                    aggfunc=pivot_agg,
                    fill_value=0,
                    margins=True,
                    margins_name="Total"
                )
            
            # Format the pivot table
            if values in ["duration", "score"]:
                pivot = pivot.round(1)
            
            # Display with conditional formatting
            if values == "score":
                styled_pivot = pivot.style.background_gradient(cmap="RdYlGn", vmin=0, vmax=100)
            elif values == "duration":
                styled_pivot = pivot.style.background_gradient(cmap="Blues")
            else:
                styled_pivot = pivot.style.background_gradient(cmap="YlOrRd")
            
            st.dataframe(styled_pivot, use_container_width=True)
            
            # Download button
            csv = pivot.to_csv()
            st.download_button(
                label="📥 Download Pivot Table as CSV",
                data=csv,
                file_name=f"pivot_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"Error creating pivot table: {str(e)}")
    else:
        st.info("Please select at least one row dimension to create a pivot table")

def create_visualizations(df):
    """Create data visualizations"""
    st.subheader("📈 Data Visualizations")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Service Trends", "Student Progress", "Goal Tracking", "Time Analysis"])
    
    with tab1:
        # Service frequency over time
        col1, col2 = st.columns(2)
        
        with col1:
            services_by_day = df.groupby(['date', 'service']).size().reset_index(name='count')
            fig = px.line(
                services_by_day,
                x='date',
                y='count',
                color='service',
                title="Service Frequency Over Time",
                labels={'count': 'Number of Sessions', 'date': 'Date'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            service_duration = df.groupby('service')['duration'].sum().reset_index()
            fig = px.pie(
                service_duration,
                values='duration',
                names='service',
                title="Total Duration by Service Type"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Student progress analysis
        selected_student = st.selectbox(
            "Select Student:",
            ["All Students"] + sorted(df['student'].unique().tolist())
        )
        
        if selected_student != "All Students":
            student_df = df[df['student'] == selected_student]
        else:
            student_df = df
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Score trend over time
            if not student_df[student_df['score'].notna()].empty:
                score_trend = student_df[student_df['score'].notna()].groupby('date')['score'].mean().reset_index()
                fig = px.scatter(
                    score_trend,
                    x='date',
                    y='score',
                    title=f"Score Trend - {selected_student}",
                    trendline="lowess"
                )
                fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Target")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No score data available for this selection")
        
        with col2:
            # Session duration distribution
            fig = px.histogram(
                student_df,
                x='duration',
                nbins=20,
                title=f"Session Duration Distribution - {selected_student}",
                labels={'duration': 'Duration (minutes)', 'count': 'Frequency'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Goal achievement tracking
        if not df[df['goal_id'].notna()].empty:
            goal_data = df[df['goal_id'].notna()].groupby('goal_id').agg({
                'score': 'mean',
                'duration': 'sum',
                'id': 'count'
            }).reset_index()
            goal_data.columns = ['Goal ID', 'Avg Score', 'Total Duration', 'Sessions']
            
            fig = px.bar(
                goal_data,
                x='Goal ID',
                y='Avg Score',
                title="Average Score by Goal",
                color='Avg Score',
                color_continuous_scale="RdYlGn",
                labels={'Avg Score': 'Average Score (%)'}
            )
            fig.add_hline(y=80, line_dash="dash", line_color="black", annotation_text="Target")
            st.plotly_chart(fig, use_container_width=True)
            
            # Goal details table
            st.dataframe(
                goal_data.style.format({
                    'Avg Score': '{:.1f}%',
                    'Total Duration': '{:.0f} min'
                }),
                use_container_width=True
            )
        else:
            st.info("No goal data available")
    
    with tab4:
        # Time-based analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Heatmap of services by day and hour
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            
            heatmap_data = df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
            heatmap_pivot = heatmap_data.pivot(index='hour', columns='day_of_week', values='count').fillna(0)
            
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            heatmap_pivot.columns = [days[i] if i < len(days) else str(i) for i in heatmap_pivot.columns]
            
            fig = px.imshow(
                heatmap_pivot,
                title="Service Activity Heatmap",
                labels=dict(x="Day of Week", y="Hour of Day", color="Sessions"),
                aspect="auto",
                color_continuous_scale="YlOrRd"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Weekly summary
            weekly_summary = df.groupby('week').agg({
                'student': 'nunique',
                'duration': 'sum',
                'score': 'mean'
            }).reset_index()
            weekly_summary.columns = ['Week', 'Students', 'Total Duration', 'Avg Score']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Students', x=weekly_summary['Week'], y=weekly_summary['Students'], yaxis='y'))
            fig.add_trace(go.Scatter(name='Avg Score', x=weekly_summary['Week'], y=weekly_summary['Avg Score'], yaxis='y2', mode='lines+markers'))
            
            fig.update_layout(
                title="Weekly Summary",
                xaxis_title="Week Number",
                yaxis=dict(title="Number of Students", side="left"),
                yaxis2=dict(title="Average Score (%)", overlaying="y", side="right"),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

def create_detailed_view(df):
    """Create detailed data view with filters"""
    st.subheader("🔍 Detailed Data View")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        students = st.multiselect(
            "Filter by Student:",
            df['student'].unique(),
            default=None
        )
    
    with col2:
        services = st.multiselect(
            "Filter by Service:",
            df['service'].unique(),
            default=None
        )
    
    with col3:
        date_range = st.date_input(
            "Date Range:",
            value=(df['date'].min(), df['date'].max()),
            min_value=df['date'].min(),
            max_value=df['date'].max()
        )
    
    with col4:
        min_score = st.slider(
            "Minimum Score:",
            min_value=0,
            max_value=100,
            value=0
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if students:
        filtered_df = filtered_df[filtered_df['student'].isin(students)]
    
    if services:
        filtered_df = filtered_df[filtered_df['service'].isin(services)]
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['date'] >= date_range[0]) &
            (filtered_df['date'] <= date_range[1])
        ]
    
    if min_score > 0:
        filtered_df = filtered_df[filtered_df['score'] >= min_score]
    
    # Display filtered data
    st.write(f"Showing {len(filtered_df)} of {len(df)} records")
    
    # Format display
    display_df = filtered_df[['timestamp', 'student', 'service', 'duration', 'event', 'score', 'goal_id', 'device_id']].copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    
    st.dataframe(
        display_df.style.format({
            'duration': '{:.0f} min',
            'score': '{:.1f}%'
        }, na_rep='-'),
        use_container_width=True
    )
    
    # Export filtered data
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def main():
    """Main dashboard application"""
    st.title("📊 SPED Services Analytics Dashboard")
    st.markdown("---")
    
    # Load data
    try:
        df = load_data()
        
        if df.empty:
            st.warning("No data found in database. Please run the Services Aggregator to import data first.")
            st.info("Steps to get data:\n1. Run Services Aggregator\n2. Fetch emails with service logs\n3. Return to this dashboard")
            return
        
        # Sidebar
        with st.sidebar:
            st.header("Dashboard Controls")
            
            # Refresh button
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.rerun()
            
            st.markdown("---")
            
            # Data summary
            st.subheader("Data Summary")
            st.metric("Total Records", len(df))
            st.metric("Date Range", f"{df['date'].min()} to {df['date'].max()}")
            st.metric("Data Sources", df['device_id'].nunique())
            
            st.markdown("---")
            
            # View selection
            view_mode = st.radio(
                "Select View:",
                ["Overview", "Pivot Tables", "Visualizations", "Detailed Data"]
            )
        
        # Main content based on view selection
        if view_mode == "Overview":
            create_overview_metrics(df)
            st.markdown("---")
            
            # Quick insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📌 Top Students by Sessions")
                top_students = df['student'].value_counts().head(10)
                st.bar_chart(top_students)
            
            with col2:
                st.subheader("📌 Service Distribution")
                service_counts = df['service'].value_counts()
                st.bar_chart(service_counts)
        
        elif view_mode == "Pivot Tables":
            create_pivot_table(df)
        
        elif view_mode == "Visualizations":
            create_visualizations(df)
        
        elif view_mode == "Detailed Data":
            create_detailed_view(df)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure the database file 'aggregated_services.db' exists in the same directory.")

if __name__ == "__main__":
    main()
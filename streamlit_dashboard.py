"""
Streamlit dashboard for Smart Traffic Light Control System.

Run with:
    streamlit run streamlit_dashboard.py
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from fuzzy_controller import FuzzyTrafficController
from main_control_system import SmartTrafficLightSystem
from traffic_simulator import TrafficSimulator


PROJECT_DIR = Path(__file__).resolve().parent
RESULTS_JSON = PROJECT_DIR / "test_results.json"
FIGURES_DIR = PROJECT_DIR / "figures"
GENERATED_IMAGES = [
    "performance_comparison.png",
    "improvement_chart.png",
    "adaptive_response.png",
    "traffic_patterns.png",
    "membership_functions.png",
]

SCENARIO_PRESETS = {
    "Weekday Morning Peak": {"duration": 120, "start_hour": 8, "is_weekday": True},
    "Weekday Evening Peak": {"duration": 120, "start_hour": 17, "is_weekday": True},
    "Weekday Normal Hours": {"duration": 120, "start_hour": 11, "is_weekday": True},
    "Weekend Midday": {"duration": 120, "start_hour": 12, "is_weekday": False},
    "Night Time": {"duration": 120, "start_hour": 2, "is_weekday": True},
}

TIME_LABELS = ["Night", "Normal", "Morning Peak", "Evening Peak"]


def inject_styles() -> None:
    """Inject custom CSS to make the UI visually distinct and presentation-ready."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Manrope:wght@400;600;700&display=swap');

            .stApp {
                background: radial-gradient(circle at 0% 0%, #fff3d9 0%, #f4f8ff 46%, #eef6f2 100%);
            }
            html, body, [class*="css"] {
                font-family: 'Manrope', sans-serif;
            }
            h1, h2, h3, h4 {
                font-family: 'Sora', sans-serif;
                letter-spacing: 0.1px;
            }
            .hero {
                background: linear-gradient(110deg, #103d5c 0%, #1f5d78 42%, #3f7f6e 100%);
                color: #f8fbff;
                padding: 1.2rem 1.4rem;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.25);
                box-shadow: 0 10px 28px rgba(16, 61, 92, 0.24);
                margin-bottom: 1rem;
            }
            .hero p {
                margin-bottom: 0;
                color: rgba(245, 251, 255, 0.92);
            }
            .metric-card {
                border-radius: 14px;
                padding: 0.8rem 1rem;
                background: #ffffff;
                border: 1px solid #d6e4ef;
                box-shadow: 0 4px 16px rgba(16, 61, 92, 0.08);
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 10px;
                margin-bottom: 0.6rem;
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 10px;
                background: #ebf2f7;
                border: 1px solid #d3e1eb;
                color: #123a56;
                font-weight: 700;
                padding: 0.35rem 0.9rem;
            }
            .stTabs [aria-selected="true"] {
                background: #123a56 !important;
                color: #ffffff !important;
                border-color: #123a56 !important;
            }
            .insight {
                background: #f8fff9;
                border-left: 5px solid #2f7a4a;
                padding: 0.65rem 0.85rem;
                border-radius: 8px;
                margin-top: 0.4rem;
                margin-bottom: 0.4rem;
            }
            .warning {
                background: #fff8ef;
                border-left: 5px solid #c7702d;
                padding: 0.65rem 0.85rem;
                border-radius: 8px;
                margin-top: 0.4rem;
                margin-bottom: 0.4rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_saved_results() -> list[dict]:
    if not RESULTS_JSON.exists():
        return []
    with RESULTS_JSON.open("r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(show_spinner=False)
def run_single_comparison(duration: int, start_hour: int, is_weekday: bool, stochastic: bool) -> dict:
    system = SmartTrafficLightSystem(intersection_id="DASH-001")
    if stochastic:
        system.traffic_simulator = TrafficSimulator(seed=None)
    return system.compare_systems(duration_minutes=duration, start_hour=start_hour, is_weekday=is_weekday)


@st.cache_data(show_spinner=False)
def run_benchmark_suite(stochastic: bool) -> pd.DataFrame:
    rows = []
    for scenario_name, params in SCENARIO_PRESETS.items():
        comparison = run_single_comparison(
            duration=params["duration"],
            start_hour=params["start_hour"],
            is_weekday=params["is_weekday"],
            stochastic=stochastic,
        )
        rows.append(
            {
                "Scenario": scenario_name,
                "Fixed Delay (s)": comparison["fixed_time"]["average_delay"],
                "Smart Delay (s)": comparison["smart_control"]["average_delay"],
                "Delay Reduction (%)": comparison["improvement"]["delay_reduction_percent"],
                "Vehicles Processed": comparison["smart_control"]["total_vehicles"],
                "Delay Saved (s)": comparison["improvement"]["total_delay_saved"],
            }
        )
    return pd.DataFrame(rows)


def build_kpi_strip(saved_results: list[dict]) -> None:
    if not saved_results:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Saved Scenarios", 0)
        c2.metric("Average Improvement", "N/A")
        c3.metric("Best Scenario", "N/A")
        c4.metric("Total Vehicles", "N/A")
        return

    avg_improvement = mean(x["improvement_percent"] for x in saved_results)
    total_vehicles = sum(x["total_vehicles"] for x in saved_results)
    best = max(saved_results, key=lambda x: x["improvement_percent"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saved Scenarios", len(saved_results))
    c2.metric("Average Improvement", f"{avg_improvement:.2f}%")
    c3.metric("Best Scenario", best["scenario"])
    c4.metric("Total Vehicles", f"{total_vehicles:,}")


def render_overview(saved_results: list[dict]) -> None:
    st.subheader("Project Command Center")
    st.markdown(
        """
        <div class="hero">
            <h3 style="margin-bottom: 0.3rem;">Smart Traffic Light Intelligence Dashboard</h3>
            <p>
                This dashboard combines fuzzy logic, traffic simulation, fairness controls,
                pedestrian safety, and benchmark analytics into one presentation-ready system.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    build_kpi_strip(saved_results)

    left, right = st.columns([1.25, 1])

    with left:
        st.markdown("### Why This Scores Higher")
        st.markdown(
            """
            <div class="insight">1. End-to-end observability: from fuzzy decisions to pedestrian safety and queue-level fairness.</div>
            <div class="insight">2. Scenario-based evaluation: fixed-time baseline vs adaptive control across peak, normal, and night traffic.</div>
            <div class="insight">3. Export-ready evidence: saved JSON, generated figures, and reproducible benchmark controls.</div>
            <div class="insight">4. Practical extension path: SUMO-ready scenario integration for stronger real-world credibility.</div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("### Quick Actions")
        if st.button("Run Full Benchmark (Preset Scenarios)", use_container_width=True):
            df = run_benchmark_suite(stochastic=False)
            st.session_state["latest_benchmark"] = df.to_dict(orient="records")
            st.success("Benchmark complete. Check the Benchmark tab for full breakdown.")

        if st.button("Run Stochastic Stress Benchmark", use_container_width=True):
            df = run_benchmark_suite(stochastic=True)
            st.session_state["latest_benchmark"] = df.to_dict(orient="records")
            st.success("Stress benchmark complete with random simulation dynamics.")

        st.caption("Use tabs for deeper analysis and presentation visuals.")


def render_live_simulator() -> None:
    st.subheader("Live Scenario Simulator")
    c1, c2, c3, c4 = st.columns(4)

    duration = c1.slider("Duration (minutes)", 30, 240, 120, 10)
    start_hour = c2.slider("Start Hour", 0, 23, 8, 1)
    day_type = c3.selectbox("Day Type", ["Weekday", "Weekend"])
    stochastic = c4.toggle("Stochastic Mode", value=False, help="Adds non-deterministic traffic patterns.")

    if st.button("Run Scenario Comparison", type="primary", use_container_width=True):
        with st.spinner("Running simulation and comparison..."):
            comparison = run_single_comparison(
                duration=duration,
                start_hour=start_hour,
                is_weekday=day_type == "Weekday",
                stochastic=stochastic,
            )

        fixed = comparison["fixed_time"]
        smart = comparison["smart_control"]
        imp = comparison["improvement"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fixed Avg Delay", f"{fixed['average_delay']:.2f}s")
        m2.metric("Smart Avg Delay", f"{smart['average_delay']:.2f}s")
        m3.metric("Delay Reduction", f"{imp['delay_reduction_percent']:.2f}%")
        m4.metric("Delay Saved", f"{imp['total_delay_saved']:.0f}s")

        cycle_df = pd.DataFrame(smart.get("cycle_details", []))
        if not cycle_df.empty:
            queue_cols = ["ns_queue_after", "ew_queue_after"]
            green_cols = ["minute", "green_time", "active_direction"]

            line = px.line(
                cycle_df,
                x="minute",
                y=queue_cols,
                title="Queue Evolution by Direction",
                labels={"value": "Vehicles in Queue", "minute": "Simulation Minute", "variable": "Direction"},
                color_discrete_sequence=["#2a9d8f", "#e76f51"],
            )
            st.plotly_chart(line, use_container_width=True)

            scatter = px.scatter(
                cycle_df,
                x="minute",
                y="green_time",
                color="active_direction",
                title="Adaptive Green Time Decisions",
                labels={"green_time": "Green Time (s)", "minute": "Simulation Minute"},
                color_discrete_map={"NS": "#264653", "EW": "#f4a261"},
            )
            st.plotly_chart(scatter, use_container_width=True)

            st.dataframe(cycle_df[green_cols + queue_cols].head(20), use_container_width=True)

        st.download_button(
            "Download This Scenario Result (JSON)",
            data=json.dumps(comparison, indent=2),
            file_name="scenario_comparison.json",
            mime="application/json",
            use_container_width=True,
        )


def render_benchmark_tab(saved_results: list[dict]) -> None:
    st.subheader("Benchmark and Performance Lab")

    use_saved = st.toggle("Use saved test_results.json", value=True)

    if use_saved and saved_results:
        df = pd.DataFrame(
            {
                "Scenario": [x["scenario"] for x in saved_results],
                "Fixed Delay (s)": [x["fixed_avg_delay"] for x in saved_results],
                "Smart Delay (s)": [x["smart_avg_delay"] for x in saved_results],
                "Delay Reduction (%)": [x["improvement_percent"] for x in saved_results],
                "Vehicles Processed": [x["total_vehicles"] for x in saved_results],
            }
        )
    elif "latest_benchmark" in st.session_state:
        df = pd.DataFrame(st.session_state["latest_benchmark"])
    else:
        st.info("No benchmark dataset loaded yet. Run benchmark from Overview or disable saved data.")
        return

    st.dataframe(df, use_container_width=True)

    bar = go.Figure()
    bar.add_trace(
        go.Bar(
            x=df["Scenario"],
            y=df["Fixed Delay (s)"],
            name="Fixed-Time",
            marker_color="#d1495b",
        )
    )
    bar.add_trace(
        go.Bar(
            x=df["Scenario"],
            y=df["Smart Delay (s)"],
            name="Smart Fuzzy",
            marker_color="#2a9d8f",
        )
    )
    bar.update_layout(
        barmode="group",
        title="Fixed-Time vs Smart Delay by Scenario",
        yaxis_title="Average Delay (s)",
        xaxis_title="Scenario",
    )
    st.plotly_chart(bar, use_container_width=True)

    improvement_chart = px.bar(
        df,
        x="Scenario",
        y="Delay Reduction (%)",
        color="Delay Reduction (%)",
        color_continuous_scale="RdYlGn",
        title="Improvement Percentage by Scenario",
    )
    st.plotly_chart(improvement_chart, use_container_width=True)

    if "Delay Saved (s)" in df.columns:
        total_saved = df["Delay Saved (s)"].sum()
    else:
        total_saved = ((df["Fixed Delay (s)"] - df["Smart Delay (s)"]) * df["Vehicles Processed"]).sum()

    st.markdown(
        f"""
        <div class="metric-card">
            <strong>Aggregate Delay Savings Estimate:</strong> {total_saved:,.0f} seconds across benchmark scenarios.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_fuzzy_lab() -> None:
    st.subheader("Fuzzy Logic Lab")

    controller = FuzzyTrafficController()
    c1, c2, c3 = st.columns(3)
    density = c1.slider("Traffic Density (%)", 0, 100, 65)
    day = c2.selectbox("Day", ["Weekday", "Weekend"])
    slot_label = c3.selectbox("Time Slot", TIME_LABELS, index=2)
    slot = TIME_LABELS.index(slot_label)

    green_time = controller.compute_green_time(density=density, is_weekday=(day == "Weekday"), time_period=slot)
    st.metric("Recommended Green Time", f"{green_time} seconds")

    curve_rows = []
    for d in range(0, 101, 5):
        curve_rows.append(
            {
                "Density": d,
                "Night": controller.compute_green_time(d, day == "Weekday", 0),
                "Normal": controller.compute_green_time(d, day == "Weekday", 1),
                "Morning Peak": controller.compute_green_time(d, day == "Weekday", 2),
                "Evening Peak": controller.compute_green_time(d, day == "Weekday", 3),
            }
        )

    curve_df = pd.DataFrame(curve_rows)
    melted = curve_df.melt(id_vars=["Density"], var_name="Time Slot", value_name="Green Time")
    line = px.line(
        melted,
        x="Density",
        y="Green Time",
        color="Time Slot",
        title="How Fuzzy Logic Adapts Green Time",
        labels={"Density": "Traffic Density (%)", "Green Time": "Green Time (s)"},
        color_discrete_sequence=["#6c757d", "#118ab2", "#06d6a0", "#ef476f"],
    )
    st.plotly_chart(line, use_container_width=True)

    st.markdown(
        """
        <div class="insight">
            Presentation tip: explain that overlap between fuzzy membership sets avoids abrupt timing jumps,
            which makes decisions smoother than rigid threshold rules.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_safety_fairness_tab() -> None:
    st.subheader("Pedestrian Safety and Fairness Analytics")

    scenario = st.selectbox("Scenario Preset", list(SCENARIO_PRESETS.keys()), index=0)
    stochastic = st.toggle("Stochastic Replay", value=False)

    if st.button("Analyze Safety and Fairness", use_container_width=True):
        params = SCENARIO_PRESETS[scenario]
        with st.spinner("Running detailed scenario analysis..."):
            comparison = run_single_comparison(
                duration=params["duration"],
                start_hour=params["start_hour"],
                is_weekday=params["is_weekday"],
                stochastic=stochastic,
            )

        smart = comparison["smart_control"]
        cycle_df = pd.DataFrame(smart.get("cycle_details", []))
        ped_stats = smart.get("pedestrian_stats", {})

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pedestrians Crossed", ped_stats.get("total_pedestrians_crossed", 0))
        c2.metric("Crossing Requests", ped_stats.get("crossing_requests", 0))
        c3.metric("Safety Overrides", ped_stats.get("forced_crossings", 0))
        c4.metric("Current Waiting", ped_stats.get("current_waiting", 0))

        if not cycle_df.empty:
            direction_count = cycle_df["active_direction"].value_counts().reset_index()
            direction_count.columns = ["Direction", "Cycles"]
            pie = px.pie(direction_count, names="Direction", values="Cycles", title="Directional Service Share")
            st.plotly_chart(pie, use_container_width=True)

            fairness_gap = abs(
                direction_count.loc[direction_count["Direction"] == "NS", "Cycles"].sum()
                - direction_count.loc[direction_count["Direction"] == "EW", "Cycles"].sum()
            )

            st.markdown(
                f"""
                <div class="metric-card">
                    <strong>Fairness Gap (Cycle Difference):</strong> {fairness_gap} cycles.
                    Lower is generally better when both directions have comparable demand.
                </div>
                """,
                unsafe_allow_html=True,
            )

            forced_ratio = 0.0
            if ped_stats.get("crossing_requests", 0) > 0:
                forced_ratio = (ped_stats.get("forced_crossings", 0) / ped_stats["crossing_requests"]) * 100

            if forced_ratio > 25:
                st.markdown(
                    """
                    <div class="warning">
                        High safety override ratio detected. Consider tuning pedestrian crossing policy
                        for stronger comfort while preserving vehicle throughput.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="insight">
                        Safety override ratio is healthy. The controller is balancing throughput and pedestrian safety well.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_assets_and_sumo_tab() -> None:
    st.subheader("Reports, Visual Assets, and SUMO Integration")

    st.markdown("### Generated Analysis Assets")
    existing_images = [name for name in GENERATED_IMAGES if (FIGURES_DIR / name).exists()]

    if not existing_images:
        st.info("No generated images found yet. Run performance_testing.py to create charts.")
    else:
        for image_name in existing_images:
            st.image(str(FIGURES_DIR / image_name), caption=image_name, use_container_width=True)

    st.markdown("### SUMO Scenario Status")
    sumo_files = [
        PROJECT_DIR / "sumo_scenario" / "intersection.net.xml",
        PROJECT_DIR / "sumo_scenario" / "intersection.sumocfg",
        PROJECT_DIR / "sumo_scenario" / "routes.rou.xml",
        PROJECT_DIR / "sumo_scenario" / "trips.trips.xml",
    ]

    sumo_status = pd.DataFrame(
        {
            "File": [f.name for f in sumo_files],
            "Exists": [f.exists() for f in sumo_files],
            "Size (KB)": [round((f.stat().st_size / 1024), 2) if f.exists() else 0 for f in sumo_files],
        }
    )
    st.dataframe(sumo_status, use_container_width=True)

    st.markdown(
        """
        <div class="insight">
            For advanced evaluation, run SUMO with fuzzy control using:
            <code>python sumo_fuzzy_simulation.py --gui --duration 900 --start-hour 8</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if RESULTS_JSON.exists():
        st.download_button(
            "Download Saved Benchmark JSON",
            data=RESULTS_JSON.read_text(encoding="utf-8"),
            file_name="test_results.json",
            mime="application/json",
            use_container_width=True,
        )


def render_presentation_tab() -> None:
    st.subheader("Presentation Booster")

    st.markdown("### High-Impact Talking Sequence")
    st.markdown(
        """
        1. Show baseline weakness: fixed-time signals ignore real-time conditions.
        2. Explain fuzzy logic inputs: density, day type, and time slot.
        3. Show adaptive output: green time changes smoothly with traffic pressure.
        4. Prove impact: benchmark comparison with delay reduction percentages.
        5. Highlight responsibility: pedestrian max-wait safeguards and fairness controls.
        6. Mention scalability: SUMO integration path and multi-intersection extensions.
        """
    )

    st.markdown("### Extra-Credit Add-ons Included")
    st.markdown(
        """
        1. Deterministic and stochastic benchmark modes.
        2. Queue-level directional fairness diagnostics.
        3. Safety override ratio analysis for pedestrian comfort.
        4. JSON export pipeline for auditability.
        5. Built-in scenario presets for rapid live demos.
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="Smart Traffic Control Dashboard",
        page_icon="Traffic",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_styles()

    st.sidebar.title("Dashboard Controls")
    st.sidebar.markdown("Smart Traffic Light Control\nSoft Computing Project")
    st.sidebar.markdown("---")
    st.sidebar.caption("Tip: Use full-width mode and switch tabs during presentation.")

    saved_results = load_saved_results()

    tabs = st.tabs(
        [
            "Overview",
            "Live Simulator",
            "Benchmark",
            "Fuzzy Lab",
            "Safety and Fairness",
            "Assets and SUMO",
            "Presentation",
        ]
    )

    with tabs[0]:
        render_overview(saved_results)
    with tabs[1]:
        render_live_simulator()
    with tabs[2]:
        render_benchmark_tab(saved_results)
    with tabs[3]:
        render_fuzzy_lab()
    with tabs[4]:
        render_safety_fairness_tab()
    with tabs[5]:
        render_assets_and_sumo_tab()
    with tabs[6]:
        render_presentation_tab()


if __name__ == "__main__":
    main()

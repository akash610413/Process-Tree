import streamlit as st
import pandas as pd
from graphviz import Digraph


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Process Tree Visualizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

.main-title {
    font-size: 46px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 5px;
}

.main-subtitle {
    font-size: 18px;
    opacity: 0.7;
    margin-bottom: 25px;
}

.section-heading {
    font-size: 28px;
    font-weight: 750;
    margin-top: 10px;
    margin-bottom: 15px;
}

.info-box {
    padding: 20px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-bottom: 12px;
}

.info-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
}

.info-text {
    opacity: 0.8;
    line-height: 1.6;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE / SIMULATOR CORE
# =========================================================

def reset_state():
    """
    Reset the entire process simulation.
    """

    st.session_state.processes = {
        0: {
            "ppid": None,
            "step": 0
        }
    }

    st.session_state.log = []

    # Number of processes after every step.
    # Initially only P0 exists.
    st.session_state.growth = [1]

    # Next PID to assign.
    st.session_state.next_pid = 1

    # Number of fork rounds/operations.
    st.session_state.step_counter = 0

    # Currently selected process in Custom mode.
    st.session_state.selected_pid = 0


# Initialize simulation
if "processes" not in st.session_state:
    reset_state()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_children(pid):
    """
    Return all direct children of a process.
    """

    return [
        process_pid
        for process_pid, data
        in st.session_state.processes.items()
        if data["ppid"] == pid
    ]


def fork_process(parent_pid):
    """
    Create exactly one child process for the selected parent.
    Used by Custom fork() mode.
    """

    st.session_state.step_counter += 1

    new_pid = st.session_state.next_pid

    st.session_state.processes[new_pid] = {
        "ppid": parent_pid,
        "step": st.session_state.step_counter
    }

    st.session_state.log.append(
        (
            parent_pid,
            new_pid,
            st.session_state.step_counter
        )
    )

    st.session_state.next_pid += 1

    st.session_state.growth.append(
        len(st.session_state.processes)
    )

    return new_pid


def sequential_fork_round():
    """
    Every process that existed BEFORE the current round
    performs exactly one fork().

    Example:

    Before:
        P0

    After round 1:
        P0
        P1

    After round 2:
        P0
        P1
        P2
        P3

    After round 3:
        8 processes
    """

    st.session_state.step_counter += 1

    # IMPORTANT:
    # Take a snapshot before creating children.
    # Newly created children must NOT execute the same fork
    # during the current round.
    current_pids = list(
        st.session_state.processes.keys()
    )

    for parent_pid in current_pids:

        new_pid = st.session_state.next_pid

        st.session_state.processes[new_pid] = {
            "ppid": parent_pid,
            "step": st.session_state.step_counter
        }

        st.session_state.log.append(
            (
                parent_pid,
                new_pid,
                st.session_state.step_counter
            )
        )

        st.session_state.next_pid += 1

    st.session_state.growth.append(
        len(st.session_state.processes)
    )


def build_tree_graph():
    """
    Build the Graphviz process tree.
    """

    dot = Digraph()

    dot.attr(
        bgcolor="transparent"
    )

    dot.attr(
        rankdir="TB"
    )

    dot.attr(
        "node",
        fontname="Arial"
    )

    for pid, data in st.session_state.processes.items():

        if pid == 0:

            label = (
                "P0\n"
                "PID = 0\n"
                "ROOT"
            )

            dot.node(
                str(pid),
                label,
                shape="ellipse",
                style="filled",
                fillcolor="#d9ead3"
            )

        else:

            label = (
                f"P{pid}\n"
                f"PID = {pid}\n"
                f"PPID = {data['ppid']}"
            )

            dot.node(
                str(pid),
                label,
                shape="ellipse",
                style="filled",
                fillcolor="#e8f0fe"
            )

        if data["ppid"] is not None:

            dot.edge(
                str(data["ppid"]),
                str(pid)
            )

    return dot


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">'
    '🌳 Process Tree Visualizer'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Simulation of Process Creation Using Multiple '
    'fork() Calls'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# PROJECT INTRODUCTION
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">
    🎯 Objective
    </div>

    <div class="info-text">

    Visualize process creation and understand
    parent-child relationships using multiple
    fork() calls.

    </div>

    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">
    🌳 Process Hierarchy
    </div>

    <div class="info-text">

    Every process is connected to its parent
    through PID and PPID relationships.

    </div>

    </div>
    """, unsafe_allow_html=True)


with col3:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">
    💻 Technologies
    </div>

    <div class="info-text">

    Python · Streamlit · Graphviz · C

    </div>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Simulation Controls")

mode = st.sidebar.radio(
    "Simulation Mode",
    [
        "Sequential fork()",
        "Custom fork()"
    ]
)


# =========================================================
# SEQUENTIAL FORK MODE
# =========================================================

if mode == "Sequential fork()":

    n_rounds = st.sidebar.number_input(
        "Number of fork() rounds",
        min_value=1,
        max_value=6,
        value=1,
        step=1
    )

    st.sidebar.caption(
        "Each round causes every existing process "
        "to execute fork() once."
    )

    if st.sidebar.button(
        "Execute Next fork() Round",
        use_container_width=True
    ):

        sequential_fork_round()

        st.rerun()


# =========================================================
# CUSTOM FORK MODE
# =========================================================

else:

    pid_options = sorted(
        st.session_state.processes.keys()
    )

    # Make sure selected process still exists
    if (
        "selected_pid" not in st.session_state
        or st.session_state.selected_pid
        not in pid_options
    ):

        st.session_state.selected_pid = 0

    selected_pid = st.sidebar.selectbox(
        "Select process to fork()",
        pid_options,
        index=pid_options.index(
            st.session_state.selected_pid
        ),
        format_func=lambda p: f"P{p}",
        key="custom_process_selector"
    )

    # Save the current selection
    st.session_state.selected_pid = selected_pid

    st.sidebar.caption(
        f"Currently selected process: P{selected_pid}"
    )

    if st.sidebar.button(
        "Fork Selected Process",
        use_container_width=True
    ):

        # Create child under selected process
        fork_process(selected_pid)

        # IMPORTANT:
        # Keep the same process selected after rerun.
        st.session_state.selected_pid = selected_pid

        st.rerun()


# =========================================================
# RESET
# =========================================================

if st.sidebar.button(
    "🔄 Reset Simulation",
    use_container_width=True
):

    reset_state()

    st.rerun()


# =========================================================
# SIDEBAR STATISTICS
# =========================================================

st.sidebar.markdown("---")

st.sidebar.metric(
    "Total Processes",
    len(st.session_state.processes)
)

st.sidebar.metric(
    "Fork Operations",
    st.session_state.step_counter
)


# =========================================================
# MAIN TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🌳 Process Tree",
        "📋 Process Table",
        "📜 Fork Log",
        "📈 Growth Graph",
        "🔍 Process Explorer",
        "💻 C Code"
    ]
)


# =========================================================
# TAB 1 — PROCESS TREE
# =========================================================

with tab1:

    st.markdown(
        '<div class="section-heading">'
        '🌳 Process Tree'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "The tree shows the parent-child relationship "
        "between all currently created processes."
    )

    st.graphviz_chart(
        build_tree_graph(),
        use_container_width=True
    )


# =========================================================
# TAB 2 — PROCESS TABLE
# =========================================================

with tab2:

    st.markdown(
        '<div class="section-heading">'
        '📋 Process Table'
        '</div>',
        unsafe_allow_html=True
    )

    rows = []

    for pid, data in sorted(
        st.session_state.processes.items()
    ):

        children = get_children(pid)

        rows.append(
            {
                "Process": f"P{pid}",

                "PID": pid,

                "PPID": (
                    data["ppid"]
                    if data["ppid"] is not None
                    else "-"
                ),

                "Parent": (
                    f"P{data['ppid']}"
                    if data["ppid"] is not None
                    else "None (Root)"
                ),

                "Children": (
                    ", ".join(
                        f"P{child}"
                        for child in children
                    )
                    if children
                    else "-"
                ),

                "Creation Step": data["step"]
            }
        )

    process_df = pd.DataFrame(rows)

    st.dataframe(
        process_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 3 — FORK EXECUTION LOG
# =========================================================

with tab3:

    st.markdown(
        '<div class="section-heading">'
        '📜 Fork Execution Log'
        '</div>',
        unsafe_allow_html=True
    )

    if st.session_state.log:

        log_df = pd.DataFrame(
            st.session_state.log,
            columns=[
                "Parent PID",
                "Child PID",
                "Step"
            ]
        )

        log_df["Event"] = log_df.apply(
            lambda row:
            f"P{row['Parent PID']} → "
            f"P{row['Child PID']}",
            axis=1
        )

        st.dataframe(
            log_df[
                [
                    "Step",
                    "Event"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No fork() calls have been executed yet."
        )


# =========================================================
# TAB 4 — PROCESS GROWTH
# =========================================================

with tab4:

    st.markdown(
        '<div class="section-heading">'
        '📈 Process Growth'
        '</div>',
        unsafe_allow_html=True
    )

    growth_df = pd.DataFrame(
        {
            "Step": list(
                range(
                    len(
                        st.session_state.growth
                    )
                )
            ),

            "Process Count":
                st.session_state.growth
        }
    )

    st.line_chart(
        growth_df.set_index("Step")
    )

    st.markdown("""
    <div class="info-box">

    <div class="info-title">
    🧮 Process Growth Formula
    </div>

    <div class="info-text">

    For unrestricted sequential fork() calls:

    <br><br>

    <center>

    <b>Number of Processes = 2ⁿ</b>

    </center>

    <br>

    where <b>n</b> is the number of fork() rounds.

    <br><br>

    Example:

    <br>

    1 fork → 2 processes

    <br>

    2 forks → 4 processes

    <br>

    3 forks → 8 processes

    <br>

    4 forks → 16 processes

    </div>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# TAB 5 — PROCESS EXPLORER
# =========================================================

with tab5:

    st.markdown(
        '<div class="section-heading">'
        '🔍 Process Explorer'
        '</div>',
        unsafe_allow_html=True
    )

    pid_choice = st.selectbox(
        "Select a process to inspect",
        sorted(
            st.session_state.processes.keys()
        ),
        format_func=lambda p: f"P{p}",
        key="explorer"
    )

    data = st.session_state.processes[
        pid_choice
    ]

    children = get_children(
        pid_choice
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
            <div class="info-box">

            <div class="info-title">
            Process Information
            </div>

            <div class="info-text">

            <b>Process:</b> P{pid_choice}

            <br><br>

            <b>PID:</b> {pid_choice}

            <br><br>

            <b>PPID:</b>
            {
                data["ppid"]
                if data["ppid"] is not None
                else "None (Root Process)"
            }

            <br><br>

            <b>Creation Step:</b>
            {data["step"]}

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        children_text = (
            ", ".join(
                f"P{child}"
                for child in children
            )
            if children
            else "None (Leaf Process)"
        )

        st.markdown(
            f"""
            <div class="info-box">

            <div class="info-title">
            Parent-Child Relationships
            </div>

            <div class="info-text">

            <b>Parent:</b>
            {
                f"P{data['ppid']}"
                if data["ppid"] is not None
                else "None"
            }

            <br><br>

            <b>Children:</b>
            {children_text}

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# TAB 6 — C PROGRAM
# =========================================================

with tab6:

    st.markdown(
        '<div class="section-heading">'
        '💻 Equivalent C Program'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "This C program demonstrates actual Unix/Linux "
        "fork() process creation. The Streamlit application "
        "itself simulates the process hierarchy."
    )

    c_program = r'''#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {

    printf("Initial Process: PID = %d\n", getpid());

    // First fork()
    pid_t pid1 = fork();

    if (pid1 < 0) {
        printf("First fork failed.\n");
        return 1;
    }

    if (pid1 == 0) {

        printf(
            "Child 1: PID = %d, PPID = %d\n",
            getpid(),
            getppid()
        );

    } else {

        wait(NULL);

        // Second fork() by parent
        pid_t pid2 = fork();

        if (pid2 < 0) {
            printf("Second fork failed.\n");
            return 1;
        }

        if (pid2 == 0) {

            printf(
                "Child 2: PID = %d, PPID = %d\n",
                getpid(),
                getppid()
            );

        } else {

            wait(NULL);

            printf(
                "Parent finished creating children.\n"
            );
        }
    }

    return 0;
}
'''

    st.code(
        c_program,
        language="c"
    )


# =========================================================
# FINAL PROJECT INFORMATION
# =========================================================

st.divider()

st.markdown(
    '<div class="section-heading">'
    '📌 Project Information'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">
    Subject
    </div>

    <div class="info-text">
    Operating Systems
    </div>

    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">
    Topic
    </div>

    <div class="info-text">
    Process Tree Using Multiple fork() Calls
    </div>

    </div>
    """, unsafe_allow_html=True)


with col3:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">
    Primary Concept
    </div>

    <div class="info-text">
    Process Creation and Hierarchy
    </div>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# KEY OBSERVATIONS
# =========================================================

st.markdown(
    '<div class="section-heading">'
    '💡 Key Observations'
    '</div>',
    unsafe_allow_html=True
)

observations = [
    "Every process has a unique PID.",
    "PPID identifies the parent process.",
    "Every child process is connected to its parent.",
    "Multiple fork() calls create a process hierarchy.",
    "In unrestricted sequential fork(), the number of processes doubles after every round.",
    "The process tree makes parent-child relationships easier to understand."
]

for observation in observations:

    st.write(
        f"🔹 {observation}"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        opacity:0.55;
        padding:20px;
        font-size:14px;
    ">

    🌳 <b>Process Tree Visualizer</b>

    <br><br>

    Operating Systems Digital Assignment

    <br>

    Process Creation · fork() · PID · PPID ·
    Parent-Child Hierarchy

    </div>
    """,
    unsafe_allow_html=True
)
# 🌳 Process Tree Visualizer

## Operating Systems Digital Assignment

### Project Title

**Process Tree Visualizer: Simulation of Process Creation Using Multiple `fork()` Calls**

---

## 📌 Overview

Process Tree Visualizer is an interactive educational web application
developed to demonstrate process creation and parent-child relationships
using multiple Unix/Linux `fork()` calls.

The application visually represents how processes are created and
organized into a hierarchical process tree.

It provides an interactive way to understand important Operating System
concepts such as:

- Process creation
- `fork()`
- PID
- PPID
- Parent-child relationships
- Process hierarchy
- Process multiplication
- Process trees

---

# 🎯 Objectives

The main objectives of this project are:

1. To understand the process creation mechanism using `fork()`.

2. To visualize parent-child relationships between processes.

3. To demonstrate PID and PPID relationships.

4. To understand the effect of multiple `fork()` calls.

5. To develop an interactive application for learning process trees.

---

# 📝 Problem Statement

In Operating Systems, processes can create new processes using the
`fork()` system call.

When multiple `fork()` calls are executed, the number of processes
can increase rapidly and the resulting parent-child relationships
can become difficult to understand.

Therefore, an interactive application is developed to simulate
process creation and visualize the resulting process hierarchy.

---

# ⚙️ Features

## 1. Sequential fork() Simulation

The application simulates unrestricted sequential `fork()` calls.

For example:

```text
1 fork() → 2 processes
2 fork() → 4 processes
3 fork() → 8 processes
4 fork() → 16 processes
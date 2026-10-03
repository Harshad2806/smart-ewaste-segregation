# Smart E-Waste Segregation & Recycling System

An end-to-end AI application developed for **Smart India Hackathon** to identify common categories of e-waste from images and provide structured reuse, repair, recovery, and recycling guidance.

## Overview

The system combines **computer vision, a FastAPI backend, a React frontend, a structured e-waste knowledge base, and local LLM reasoning** into a single workflow.

Users can upload an image or use the camera to:

1. Identify the e-waste category
2. View prediction confidence
3. Understand reuse and repair potential
4. Get recycling and recovery recommendations
5. View handling and risk information
6. Review previous analyses through the dashboard

## Supported E-Waste Categories

- Smartphones
- Laptops
- Electrical Cables
- Electronic Chips
- Small Appliances

## System Architecture

```text
                ┌─────────────────────┐
                │   Image / Camera    │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   React Frontend    │
                │    Vite + Tailwind  │
                └──────────┬──────────┘
                           │ HTTP
                           ▼
                ┌─────────────────────┐
                │   FastAPI Backend   │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   YOLO Classifier   │
                │   5 E-Waste Classes │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Confidence /        │
                │ Decision Layer      │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  E-Waste Knowledge  │
                │       Base          │
                └──────────┬──────────┘
                           │
                           ▼
          ┌─────────────────────────────────┐
          │       AI Reasoning Layer        │
          │                                 │
          │  Ollama → Deterministic        │
          │           Fallback              │
          └────────────────┬────────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Recycling / Recovery│
                │ Recommendation      │
                └─────────────────────┘

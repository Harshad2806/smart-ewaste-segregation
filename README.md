\# Smart E-Waste Segregation and Recycling System



AI-based e-waste classification and recycling recommendation system developed for Smart India Hackathon.



\## Overview



This project uses computer vision to classify e-waste images and provide recycling and recovery recommendations through a web application.



\## Features



\- E-waste image classification

\- 5 e-waste categories

\- Image upload and live camera capture

\- Confidence-based predictions

\- Recycling recommendations

\- FastAPI backend

\- React frontend

\- Local LLM integration using Ollama

\- Deterministic fallback for recommendations



\## E-Waste Categories



\- Electrical Cables

\- Electronic Chips

\- Laptops

\- Small Appliances

\- Smartphones



\## Tech Stack



\*\*Backend:\*\* Python, FastAPI, YOLO/Ultralytics, OpenCV



\*\*Frontend:\*\* React, Vite, Tailwind CSS



\*\*AI:\*\* YOLO-based image classification, Ollama



\## Architecture



```text

Image / Camera

&#x20;     ↓

React Frontend

&#x20;     ↓

FastAPI Backend

&#x20;     ↓

YOLO Classifier

&#x20;     ↓

Knowledge Base

&#x20;     ↓

Recommendation Engine

&#x20;     ↓

Ollama / Deterministic Fallback

&#x20;     ↓

Recycling Recommendation


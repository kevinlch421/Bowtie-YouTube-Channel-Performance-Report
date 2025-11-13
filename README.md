# Bowtie YouTube Channel Performance Report

> For more of my projects and data journey, visit my Notion: https://www.notion.so/Insurance-Hong-Kong-YouTube-Report-Resources-2a3e1e052cfc80e58fcdd55775bf2ba0

## Table of Contents
1. [Project Background](#project-background)
2. [Executive Summary](#executive-summary)
3. [Dataset Structure and ERD (Entity Relationship Diagram)](#dataset-structure-and-erd-entity-relationship-diagram)
4. [Insights Deep-Dive](#insights-deep-dive)  
   - [Upload Frequency and Engagement](#upload-frequency-and-engagement)  
   - [Video Duration and Engagement](#video-duration-and-engagement)  
   - [Video Topics and Engagement](#video-topics-and-engagement)
5. [Conclusion](#conclusion)
6. [Credits](#credits)

## Project Background

Bowtie is a Hong Kong–based insurance company founded in 2018. Its YouTube channel has developed strong visibility within the insurance market. Performance analysis indicates opportunities to refine the content strategy—specifically in upload frequency, video length, and topic selection—to improve engagement and audience retention.

This repository analyzes Bowtie’s YouTube strategy using public data from the YouTube API (channels, videos, and comments). A lightweight ETL pipeline (Docker + Airflow) ingests, cleans, and processes data daily at 00:00 into a PostgreSQL database. The report summarizes key insights and offers actionable recommendations.

## Executive Summary

Based on more than 32,000 channel records spanning 2019–2025, Bowtie demonstrates meaningful scale: approximately 86,000 subscribers, an average of around 155,000 views per video, and a consistent monthly publishing cadence. However, three improvement areas emerge:

- Publishing too frequently coincides with lower engagement. During high-output months, average views, likes, comments, and positive comments per video decline versus baseline months. While correlations do not imply causation, the pattern suggests diminishing returns from aggressive posting.
- Longer videos generate stronger engagement from loyal viewers. Video length is positively correlated with likes and comments but shows negligible correlation with views, implying limited contribution to reach/discovery.
- Topics framed around health fears show little benefit. Titles emphasizing negative or threat-based themes exhibit only a weak positive correlation with views and no meaningful lift in likes, comments, or positive sentiment, potentially eroding brand warmth and relatability.

## Dataset Structure and ERD (Entity Relationship Diagram)

The database comprises three tables—channels, videos, and comments—totaling more than 32,000 records. Data is extracted via the YouTube API and loaded into Postgres by a daily Airflow job running in Docker.

<p align="center">
  <img src="https://github.com/user-attachments/assets/c00c99ee-1d5a-4d54-bbc6-6517da7d8363" alt="Database ERD Diagram" width="720">
</p>

For details on the pipeline and data cleaning approach, see: https://www.notion.so/Create-the-Data-Pipeline-from-Scratch-252e1e052cfc80dd8077f6a7d1b9740d

## Insights Deep-Dive

### Upload Frequency and Engagement

Bowtie’s publishing cadence evolved across three phases:
- 2019–Feb 2024: Low-volume period with fewer than five videos per month.
- Mar–Oct 2024: Aggressive period, peaking at 23 videos in a single month—likely intended to improve algorithmic visibility.
- Nov 2024–present: A return to a balanced cadence of roughly 5–7 videos per month.

<p align="center">
  <img src="https://github.com/user-attachments/assets/89fac84e-039c-4d26-bdd1-a1b1216fd906" alt="Monthly Upload Schedule" width="800">
</p>

Correlation analysis indicates that higher upload frequency coincides with weaker per‑video performance during high-output months:
- Views: −13% on average
- Likes: −46% on average
- Comments: −54% on average
- Positive comments: −52% on average

<p align="center">
  <img src="https://github.com/user-attachments/assets/80684652-aeec-4ddd-a787-fda7119d57b4" alt="Upload Frequency vs Engagement Metrics" width="860">
</p>

Recommendations:
- Cap monthly uploads at approximately 6–9 high‑quality videos, with editorial review to ensure clarity of message, storytelling strength, and audience value.
- Structure a steady cadence (e.g., two to three releases per week) to balance recency with audience bandwidth.
- Monitor per‑video engagement and retention; if both decline as volume increases, prioritize quality over quantity.

Note: Correlation does not establish causation; continue A/B testing cadence changes.

---

### Video Duration and Engagement

Bowtie’s content skews long‑form: average length is 9.3 minutes, and roughly 76% of videos exceed 10 minutes. Long‑form supports depth and authority, but many channels increasingly rely on short‑form for reach.

<p align="center">
  <img src="https://github.com/user-attachments/assets/f74411da-a643-493a-9b85-94e99489b418" alt="Video Duration Distribution" width="480">
</p>

Engagement patterns by duration:
- Positive correlation with likes (r = 0.61)
- Positive correlation with comments (r = 0.68)
- Negligible correlation with views (r = −0.045)

<p align="center">
  <img src="https://github.com/user-attachments/assets/7f50d207-e240-4341-84b6-1f313e391da0" alt="Video Duration vs Engagement Metrics" width="900">
</p>

Recommendations:
- Maintain long‑form content for depth and loyalty, but repurpose into 30–90 second highlights for Shorts and social to drive discovery and funnel new audiences to full videos.
- Use clear chaptering, strong hooks in the first 15–30 seconds, and visual pacing to support retention.
- Track completion rates and average view duration; iterate on intros and segment lengths to improve watch‑through.

---

### Video Topics and Engagement

Content frequently centers on serious health themes (e.g., cancer, lung cancer, stomach cancer). While threat‑based framing can attract initial attention, analysis shows limited downstream benefit:
- Slight positive correlation with views (r ≈ 0.115)
- No material lift in likes, comments, or positive sentiment

<p align="center">
  <img src="https://github.com/user-attachments/assets/77777d9e-b4fe-4ac9-a29c-bf8e6b682211" alt="Keyword and Hashtag Analysis" width="900">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/b879f2d7-6a4e-4297-b871-1216ac5998fb" alt="Title Sentiment vs Engagement" width="900">
</p>

Recommendations:
- Shift from fear‑based messaging to solution‑oriented, lifestyle‑driven narratives (prevention, practical wellness, financial literacy for health planning).
- Collaborate with creators who resonate with Bowtie’s target demographic (e.g., mid‑career professionals, young families) and share relatable experiences.
- Balance content pillars:  
  1) Educational deep dives (long‑form)  
  2) Practical tips and explainers (mid‑form)  
  3) Short highlights and FAQs (short‑form)

## Conclusion

Bowtie’s YouTube presence is sizable and consistent, but engagement efficiency declines when posting volume rises too quickly, and fear‑centric topics deliver limited community value. A strategy focused on a steady cadence, multi‑format distribution (long‑form depth plus short‑form reach), and solution‑oriented storytelling is likely to improve engagement quality, audience retention, and brand affinity over time.

## Credits

This project was made possible with the help of the following resources and tutorials:
- YouTube API: Corey Schafer (https://www.youtube.com/watch?v=th5_9woFJmk) and Thu Vu Data Analytics (https://www.youtube.com/watch?v=D56_Cx36oGY). Channel ID finder: https://ytlarge.com/channel-id-finder/channel/UCD5Lx-3KCYZzCzGF2A60STg
- draw.io: Dr. Daniel Soper (https://www.youtube.com/watch?v=lAtCySGDD48)
- VS Code environment setup: NeuralNine (https://www.youtube.com/watch?v=8dlQ_nDE7dQ)
- Docker: Getting started guide (https://docs.docker.com/get-started/workshop/02_our_app/), “Understanding Dockerfile vs Docker Image vs Docker Container” (https://www.youtube.com/watch?v=8nTTACPIISU), and “Data Engineering Course for Beginners” (https://www.youtube.com/watch?v=PHsC_t0j1dU)

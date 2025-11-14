<img width="1792" height="576" alt="cover page v2" src="https://github.com/user-attachments/assets/dee3c222-9d98-46b5-87b0-c0f4738902fc" />

# Bowtie YouTube Channel Performance Report

> For more of my projects and data journey, visit my [Notion](https://www.notion.so/Insurance-Hong-Kong-YouTube-Report-Resources-2a3e1e052cfc80e58fcdd55775bf2ba0)

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

[Bowtie](https://www.bowtie.com.hk/?srsltid=AfmBOooFui_Fsgu9ZRfIuWgS0WEq-GXpLvGAPqopFiwyCXYYfjeqbdLo) is a Hong Kong–based insurance company founded in 2018. Its [YouTube channel](https://www.youtube.com/@Bowtiehongkong) has developed strong visibility within the insurance market. Performance analysis indicates opportunities to refine the content strategy—specifically in upload frequency, video length, and topic selection—to improve engagement and audience retention.

This repository analyzes Bowtie’s YouTube strategy using public data from the [YouTube API](https://developers.google.com/youtube/v3) (channels, videos, and comments). A simple ETL pipeline (Docker + Airflow) ingests, cleans, and processes data daily at 00:00 into a PostgreSQL database. The report summarizes key insights and offers actionable recommendations.

## Executive Summary

Based on more than 32,000 channel records spanning 2019–2025, Bowtie demonstrates meaningful scale: approximately 86,000 subscribers, an average of around 155,000 views per video, and a consistent monthly publishing schedule. However, three areas for improvement emerge. First, Bowtie is ${\color{red}\textbf{NOT}}$ suitable for posting too much; uploading videos too often can lead to -54% comments and -52% fewer positive comments. Second, producing long videos ${\color{green}\textbf{CAN}}$ +61% more likes and +68% more comments, but long video has ${\color{red}\textbf{NO}}$ relationship with views, indicating that long videos can ${\color{red}\textbf{NOT}}$ reach new audiences. Third, negative content such as health concerns commonly appears on the channel, but it has ${\color{red}\textbf{NO}}$ relationship with engagement or views. 

To improve, it is suggested that Bowtie should ${\color{green}\textbf{AVOID}}$ over-posting with under 6 videos per month, shift to creating  ${\color{green}\textbf{MORE}}$ diverse content, and try to ${\color{green}\textbf{CREATE}}$ highlights from those long videos to reach new viewers.

## Dataset Structure and ERD (Entity Relationship Diagram)

The database comprises three tables—channels, videos, and comments—totaling more than 32,000 records. Data is extracted via the YouTube API and loaded into Postgres by a daily Airflow job running in Docker.

<p align="center">
  <img src="https://github.com/user-attachments/assets/c00c99ee-1d5a-4d54-bbc6-6517da7d8363" alt="Database ERD Diagram" width="520">
</p>

> In case you care about the data source and data cleaning, the data is sourced from the YouTube API. We also overcome the problem of manual updates of data using Apache Airflow and Docker. The application allows us to automatically extract, transform, and load data from multiple YouTube channels to our target Postgres database daily at 00:00. For details, see: [Step to Create the ETL Data Pipeline](https://www.notion.so/Create-the-Data-Pipeline-from-Scratch-252e1e052cfc80dd8077f6a7d1b9740d)

## Insights Deep-Dive

### Upload Frequency and Engagement

#### Bowtie’s audience does not like the tight posting schedule

- Suppose frequent uploads should strengthen audience connection and online exposure (Heta Dave, 2025), the effect can **vary** across different channels.
- In our case, the correlation results show that higher upload frequency is hurting performance on the Bowtie YouTube channel.
- During high-output months, Bowtie’s videos achieved, on average:
    - **-13%** fewer views (r=-0.13)
    - **-46%** fewer likes (r=-0.46)
    - **-54%** fewer comments (r=-0.54)
    - **-52%** fewer positive comments (r=-0.52)

 <p align="center">
  <img src="https://github.com/user-attachments/assets/80684652-aeec-4ddd-a787-fda7119d57b4" alt="Upload Frequency vs Engagement Metrics" width="860">
</p>

#### The Bowtie team made the wrong decision in 2019

- All of a sudden on **March–October 2024**, Bowtie's posting pace turned **aggressive**, peaking at **23 videos in a single month**
- During the aggressive period, the views and engagement are underperforming (shown on the above line chart).
- To understand the reason why Bowtie’s audience does not like the tight posting schedule, it is potentially because the channel is:
  - overexposure: make the viewer exhausted
  - low-quality perception: viewers may think the channel rushes the poor content and ignore what they really want to see.
- Time move to **November 2024 until now**, the pace slowed to a consistent 5–7 videos monthly, but the stability is higher with views and engagement. 

<p align="center">
  <img src="https://github.com/user-attachments/assets/89fac84e-039c-4d26-bdd1-a1b1216fd906" alt="Monthly Upload Schedule" width="800">
</p>

### Video Duration and Engagement

#### Bowtie’s audience does enjoy long videos

- Suppose the Long content typically underperforms in algorithmic discovery due to lower completion rates (Smith & Davis, Journal of Digital Media Strategy, 2024). The effect can **vary** across different channels.
- In our case, the correlation results show that longer videos enhance engagement on the Bowtie YouTube channel.
- Longer videos receive, on average:
    - **+61%** correlation with more likes (r=0.61)
    - **+68%** correlation with more comments (r=0.68)
    - **Negligible** impact on views (r=-0.045)

<p align="center">
  <img src="https://github.com/user-attachments/assets/7f50d207-e240-4341-84b6-1f313e391da0" alt="Video Duration vs Engagement Metrics" width="900">
</p>

#### The Bowtie team made the right decision for long-duration video
- The correlation test indicated that Bowties is suitable for making long-duration videos.
- Throughout the years, Bowtie has tried to make long and short videos; here is how they look alike:
<p align="center">
   <img width="850" height="250" alt="long and short example" src="https://github.com/user-attachments/assets/914576ed-47f6-468c-8ccd-5eccc923a29b" />
</p>

- Based on the analysis of the duration, Bowtie has consistently focused on producing long-form content, which is a **correct action**.
    - The average video length is 9.3 minutes, with 76% of videos longer than 10 minutes.
    - A long video is well-suited for in-depth information sharing and detailed discussion.
- But it's still a double-edged sword, long-duration video **fails** to reach a new audience (based on the **Negligible** impact on views).
<p align="center">
  <img src="https://github.com/user-attachments/assets/f74411da-a643-493a-9b85-94e99489b418" alt="Video Duration Distribution" width="480">
</p>

### Video Topics and Engagement

#### Bowtie’s audience is neutral to negative topics (e.g. serious health themes)
- Suppose threat‑based content may briefly capture attention. According to Keller & Lehmann, emotionally negative framing can trigger a natural human response to seek information and solutions to mitigate potential harm (Journal of Health Communication, 2023).
- In our case, it suggests no meaningful benefit from heavily negative themes.
   - Negative tone shows only a **slight positive correlation with views (r = 0.115)**.
   - It shows **no significant link** to likes, comments, or positive audience sentiment.
- This means that while threat‑based content may briefly capture attention, it does **not** translate into sustained engagement or a stronger community connection. Excessive focus on fear messaging risks diminishing Bowtie’s relatable and trustworthy brand image.

<p align="center">
  <img src="https://github.com/user-attachments/assets/b879f2d7-6a4e-4297-b871-1216ac5998fb" alt="Title Sentiment vs Engagement" width="900">
</p>

#### The Bowtie team made the wrong decision in focusing on serious health themes
- The correlation test indicated that Bowties have an issue in allocating resources to making wrong topic.
- Throughout the years, Bowtie has made many videos with topics around health concerns, risk, and danger.
- Here is an example:
  
<p align="center">
<img width="850" height="250" alt="negative title example v2" src="https://github.com/user-attachments/assets/0ca953da-a1ea-40c8-808e-3139ee236c28" />
</p>

- Based on the analysis of the title, we count the appearance of words, which is **too much** topic around health concerns
   - The most frequent topic is **“Cancer” (癌症)**, appearing **17 times**.
   - Within the top ten keywords, **“Lung Cancer” (肺癌)** appears **9 times**.
   - Within the top ten keywords, **“Stomach Cancer” (胃癌)** appears **9 times.**

<p align="center">
  <img src="https://github.com/user-attachments/assets/77777d9e-b4fe-4ac9-a29c-bf8e6b682211" alt="Keyword and Hashtag Analysis" width="900">
</p>

## Recommendations
 
#### Avoid Over-Posting: Build Strong Management
- Over-posting often stems from skipping quality checks. This happens a lot in teams without clear leaders.
- To fix it, **assign a manager** whose job includes:
   - Reviewing each video for quality.
   - Tracking engagement and watch time per video.
   - Capping uploads at **6–9** top-notch videos per month.
   - Adding an editorial check to confirm clear messages, strong stories, and real value for viewers.

#### Keep Long Videos but Add Short Clips
- Stick with in-depth videos to build trust and keep fans loyal.
- But cut them into 30–90 second highlights for Shorts and social media.
- This draws in new people and leads them to the full videos. Your team should:
   - Add clear chapters, **grabby hooks in the first 15–30 seconds**, and lively visuals to hold attention.
   - Watch completion rates and average view time. **Tweak intros** and section lengths to boost full watches.

#### Go for Varied Topics, Not Just Health Worries
- Move away from scary messages. Focus on helpful stories about prevention, everyday wellness, and money smarts for health plans.
- Try **fresh ideas** like vlogs.
- Team up with **other channels** just for fun and reach—no hard sell.
- For example, link with creators who fit your crowd:
   - Mid-career workers.
   - Young parents.
   - Finance-focused channels.
  
## Conclusion

Bowtie’s YouTube presence is sizable and consistent, but engagement efficiency declines when posting volume rises too quickly, and fear‑centric topics deliver limited community value. A strategy focused on a steady cadence, multi‑format distribution (long‑form depth plus short‑form reach), and solution‑oriented storytelling is likely to improve engagement quality, audience retention, and brand affinity over time.

## Credits

This project was made possible with the help of the following resources and tutorials:
- YouTube API: [Corey Schafer](https://www.youtube.com/watch?v=th5_9woFJmk) and [Thu Vu Data Analytics](https://www.youtube.com/watch?v=D56_Cx36oGY). [Channel ID finder](https://ytlarge.com/channel-id-finder/channel/UCD5Lx-3KCYZzCzGF2A60STg)
- draw.io: [Dr. Daniel Soper](https://www.youtube.com/watch?v=lAtCySGDD48)
- VS Code environment setup: [NeuralNine](https://www.youtube.com/watch?v=8dlQ_nDE7dQ)
- Docker: [Getting started guide](https://docs.docker.com/get-started/workshop/02_our_app/), [“Understanding Dockerfile vs Docker Image vs Docker Container”](https://www.youtube.com/watch?v=8nTTACPIISU), and [“Data Engineering Course for Beginners”](https://www.youtube.com/watch?v=PHsC_t0j1dU)

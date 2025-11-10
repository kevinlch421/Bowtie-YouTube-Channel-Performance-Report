# Insurance Hong Kong Youtube Analysis 

> For more of my projects and data journey, visit my [Notion](https://www.notion.so/Insurance-Hong-Kong-YouTube-Report-Resources-2a3e1e052cfc80e58fcdd55775bf2ba0?source=copy_link).


## Table of content
- Project Background
- Executive Summary
- Insights Deep-Dive
- Recommendations
- Assumptions and Caveats
- Credits

## Project Background
Bowtie, a Hong Kong insurance company started in 2018, sells insurance online. It uses famous people to give money tips on their official YouTube channel to make its brand known. This works well but costs a lot. As a data analyst on the marketing team, I am curious whether we could try using small YouTube channels run by insurance agents to save money and still grow the brand.

This repo analysis Bowtie's YouTube marketing plans for insurance. It pulls data on channels, videos, and comments from the YouTube API. It use a simple data flow (ETL) with Docker and Airflow to clean and process it. Data goes into Postgres database. Finally, we make easy charts in PowerBI to see likes, views, and tips for better marketing.


  <p align="right">(<a href="#readme-top">back to top</a>)</p>

## Executive Summary
<img width="545" height="391" alt="DB_ERD drawio" src="https://github.com/user-attachments/assets/c00c99ee-1d5a-4d54-bbc6-6517da7d8363" />

Insurance related Youtube Channel's Dataset ERD

  <p align="right">(<a href="#readme-top">back to top</a>)</p>
 

## Insights Deep-Dive
### Trend of Engagement (like, comment, share)
- Bowtie is a 79800 subscribed channel, with total view of 51204434
- engament increase within 2024-2025 by 60%, because they start invited celebrity to their channel, but other period, their engament are same as other channels
- despite of view, comment are not related to the insurance product, no one cares about the product, when the celebrity talks about some unfortunate things about themselve, it could drive the desire of people for some secure feeling, but not sales directly. on the other hand, 智偉保險理財Talk, 4522 views have 200 comments who show interest about the product.

table:
Engagement Rate ((videos.likes + videos.comments) / videos.views * 100)
Comments-to-Views Ratio (videos.comments / videos.views * 100)
Product-Relevant Comment Percentage
Sentiment Distribution
Seasonal Engagement Index

  <p align="right">(<a href="#readme-top">back to top</a>)</p>
  
## Recommendations
  <p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CREDITS -->
## Credits
This project was made possible with the help of the following resources and tutorials:
- **YouTube API**: Tutorials by [Corey Schafer](https://www.youtube.com/watch?v=th5_9woFJmk) and [Thu Vu data analytics](https://www.youtube.com/watch?v=D56_Cx36oGY). Channelid by [ytlarge](https://ytlarge.com/channel-id-finder/channel/UCD5Lx-3KCYZzCzGF2A60STg)
- **draw.io**: Tutorials by [Dr. Daniel Soper](https://www.youtube.com/watch?v=lAtCySGDD48)
- **vscode**: env setup by [NeuralNine](https://www.youtube.com/watch?v=8dlQ_nDE7dQ)
- **docker**: doc by [geting start guide](https://docs.docker.com/get-started/workshop/02_our_app/), [
Understanding Dockerfile vs Docker Image vs Docker Container](https://www.youtube.com/watch?v=8nTTACPIISU), and [Data Engineering Course for Beginners]https://www.youtube.com/watch?v=PHsC_t0j1dU

  <p align="right">(<a href="#readme-top">back to top</a>)</p>

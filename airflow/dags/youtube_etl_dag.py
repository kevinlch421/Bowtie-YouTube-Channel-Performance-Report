# --------------------------------------------------------------
#  dags/youtube_etl_dag.py
# --------------------------------------------------------------
import os
import re
import time
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import psycopg2
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator  # Fixed import for Airflow 3.x
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime, text
from sqlalchemy.dialects.postgresql import insert
from io import StringIO  # For fixing JSON warning
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon (one-time; safe in DAG context)
nltk.download('vader_lexicon', quiet=True)

# -------------------------- CONFIG --------------------------
HOST_NAME = "social_media_db"   # Docker service name
DATABASE = "social_media_db"
USER_NAME = "postgres"
PASSWORD = "postgres"
PORT_ID = 5432  # inside container → 5432

# YouTube API
YOUTUBE_API_KEY = "AIzaSyB--eckt7AXDEzEp5zV2agASUWtpbuES5g"
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# HK finance / insurance channels
CHANNEL_IDS = [
    "UCD5Lx-3KCYZzCzGF2A60STg",  # @Bowtiehongkong
    "UC8OVLoXv7B1BdOVV44Dz3ig",  # @projectumbrellahk
    "UCCjW9xzAsCSKIzDYCx8CuxA",  # @CW.talkinsurfp
    "UC7OUGIPx0HIB5HA2OSL-Zhg",  # @MW31
    "UCFfbH3zDLa47d4nfotQ349Q",  # @easy_investment
    "UCxQfqaw1i39eBQG1YJDbDkw",  # @utopiahk1406
]

# Mounted host folder (available inside every Airflow container)
BASE_DIR = "/opt/airflow/host_data"
RAW_DIR = os.path.join(BASE_DIR, "data/raw")
os.makedirs(RAW_DIR, exist_ok=True)

# ----------------------- DEFAULT ARGS -----------------------
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "depends_on_past": False,
}

# ---------------------------- DAG ----------------------------
with DAG(
    dag_id="youtube_hk_finance_etl",
    default_args=default_args,
    description="Extract → Transform → Load YouTube HK finance channels",
    schedule=timedelta(days=1),
    start_date=datetime(2025, 11, 1),
    catchup=False,
    tags=["youtube", "etl"],
) as dag:

    # ------------------------------------------------------------------
    # 1. EXTRACT CHANNELS
    # ------------------------------------------------------------------
    def _extract_channel_stats(**context):
        """Fetch channel stats → save raw CSV + push DataFrame to XCom"""
        all_data = []
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=",".join(CHANNEL_IDS),
        )
        response = request.execute()

        for item in response.get("items", []):
            data = {
                "channel_id": item["id"],
                "channel_name": item["snippet"]["title"],
                "views": int(item["statistics"]["viewCount"]),
                "total_videos": int(item["statistics"]["videoCount"]),
                "subscribers": int(item["statistics"]["subscriberCount"]),
            }
            all_data.append(data)

        df = pd.DataFrame(all_data)
        raw_path = os.path.join(RAW_DIR, "channels_raw.csv")
        df.to_csv(raw_path, index=False)
        print(f"Channels saved to {raw_path}")

        # push for downstream tasks
        return df.to_json(orient="records")

    extract_channels = PythonOperator(
        task_id="extract_channels",
        python_callable=_extract_channel_stats,
    )

    # ------------------------------------------------------------------
    # Helper Functions
    # ------------------------------------------------------------------
    def get_video_ids(youtube, playlist_id: str):
        video_ids = []
        next_page = None
        while True:
            try:
                req = youtube.playlistItems().list(
                    part="contentDetails",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page,
                )
                resp = req.execute()
                video_ids.extend(
                    [i["contentDetails"]["videoId"] for i in resp.get("items", [])]
                )
                next_page = resp.get("nextPageToken")
                if not next_page:
                    break
                time.sleep(1.0)  # Rate limit buffer (1s between pages)
            except HttpError as e:
                print(f"HTTP Error fetching playlist IDs for {playlist_id}: {e}")
                if e.resp.status == 403:
                    print(f"Quota exceeded or access denied for playlist {playlist_id}")
                break  # Stop on error, return partial
            except Exception as e:
                print(f"Unexpected error fetching playlist IDs for {playlist_id}: {e}")
                break
        print(f"Fetched {len(video_ids)} video IDs for playlist {playlist_id}")
        return video_ids

    def get_video_details(youtube, video_ids, channel_id, channel_name):
        all_info = []
        for i in range(0, len(video_ids), 50):
            try:
                req = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=",".join(video_ids[i : i + 50]),
                )
                resp = req.execute()
                for v in resp.get("items", []):
                    info = {
                        "video_id": v["id"],
                        "channel_id": channel_id,
                        "channel_name": channel_name,
                        "title": v["snippet"]["title"],
                        "published_at": v["snippet"]["publishedAt"],
                        "duration": v["contentDetails"]["duration"],  # ISO string—parsed in transform
                        "view_count": int(v["statistics"].get("viewCount", 0)),
                        "like_count": int(v["statistics"].get("likeCount", 0)),
                        "comment_count": int(v["statistics"].get("commentCount", 0)),
                    }
                    all_info.append(info)
                time.sleep(1.0)  # Rate limit buffer between batches
            except HttpError as e:
                print(f"HTTP Error fetching video details for IDs {video_ids[i:i+50]}: {e}")
                if e.resp.status == 403:
                    print(f"Quota exceeded for video details—skipping batch for channel {channel_name}")
                continue  # Skip batch, try next
            except Exception as e:
                print(f"Unexpected error fetching video details for channel {channel_name}: {e}")
                continue  # Skip batch
        df = pd.DataFrame(all_info)
        print(f"Fetched details for {len(df)} videos from channel {channel_name}")
        return df

    def _extract_videos(**context):
        try:
            channel_json = context["ti"].xcom_pull(task_ids="extract_channels")
            channel_df = pd.read_json(channel_json, orient="records")

            channel_df["playlist_id"] = channel_df["channel_id"].apply(lambda x: f"UU{x[2:]}")

            all_videos = []
            for _, row in channel_df.iterrows():
                print(f"Fetching videos for channel {row['channel_name']} (playlist {row['playlist_id']})")
                v_ids = get_video_ids(youtube, row["playlist_id"])
                if v_ids:
                    df = get_video_details(youtube, v_ids, row["channel_id"], row["channel_name"])
                    all_videos.append(df)
                else:
                    print(f"No videos found for channel {row['channel_name']}")

            videos_df = pd.concat(all_videos, ignore_index=True) if all_videos else pd.DataFrame()
            raw_path = os.path.join(RAW_DIR, "videos_raw.csv")
            videos_df.to_csv(raw_path, index=False)
            print(f"Videos saved to {raw_path} (total {len(videos_df)} videos)")

            return videos_df.to_json(orient="records")
        except Exception as e:
            print(f"Unexpected error in extract_videos: {e}")
            return pd.DataFrame().to_json(orient="records")  # Fallback empty DF—don't crash DAG

    extract_videos = PythonOperator(
        task_id="extract_videos",
        python_callable=_extract_videos,
    )

    # ------------------------------------------------------------------
    # EXTRACT COMMENTS
    # ------------------------------------------------------------------
    def get_video_comments(youtube, videos_df: pd.DataFrame) -> pd.DataFrame:
        """Fetch comments for all videos in the provided DataFrame.
        Returns: DataFrame with comment details"""
        comments_ls = []
        for video_id in videos_df["video_id"].values:
            next_page_token = None
            for attempt in range(3):  # Retry up to 3 times
                try:
                    while True:  # Fetch comments using YouTube CommentThreads API
                        comments_data = youtube.commentThreads().list(
                            part="snippet",
                            videoId=video_id,
                            maxResults=100,
                            pageToken=next_page_token
                        ).execute()

                        # Process each comment
                        for comment in comments_data.get("items", []):
                            comment_dict = {
                                "comment_id": comment["snippet"]["topLevelComment"]["id"],
                                "video_id": comment["snippet"]["topLevelComment"]["snippet"]["videoId"],
                                "channel_id": comment["snippet"]["topLevelComment"]["snippet"]["channelId"],
                                "comment_text": comment["snippet"]["topLevelComment"]["snippet"]["textOriginal"],
                                "published_at": datetime.strptime(
                                    comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"],
                                    "%Y-%m-%dT%H:%M:%SZ"
                                )
                            }
                            comments_ls.append(comment_dict)

                        # Get next page token
                        next_page_token = comments_data.get("nextPageToken")
                        if not next_page_token:
                            print(f"Processed comments for video {video_id}")
                            break
                        time.sleep(1.0)  # Delay to avoid rate-limiting
                    break  # Exit retry loop on success
                except HttpError as e:
                    print(f"HTTP Error for video {video_id}: {e}")
                    if e.resp.status == 403:
                        print(f"Comments disabled for video {video_id}")
                        break
                except TimeoutError:
                    print(f"Timeout for video {video_id}, retrying ({attempt + 1}/3)...")
                    time.sleep(2.0)
                    continue
                except Exception as e:
                    print(f"Error for video {video_id}: {e}")
                    break

        # Convert to DataFrame
        comments_df = pd.DataFrame(comments_ls)
        # Drop empty comments and duplicates
        comments_df = comments_df[comments_df["comment_text"] != ""].drop_duplicates()
        raw_path = os.path.join(RAW_DIR, "comments_raw.csv")
        comments_df.to_csv(raw_path, index=False)
        print(f"Comments saved to {raw_path}")
        return comments_df.to_json(orient="records")

    def _extract_comments(**context):
        video_json = context["ti"].xcom_pull(task_ids="extract_videos")
        videos_df = pd.read_json(video_json, orient="records")
        if not videos_df.empty:
            comments_json = get_video_comments(youtube, videos_df)
            return comments_json
        else:
            print("No videos to extract comments from")
            return pd.DataFrame().to_json(orient="records")

    extract_comments = PythonOperator(
        task_id="extract_comments",
        python_callable=_extract_comments,
    )

    # ------------------------------------------------------------------
    # 2. TRANSFORM CHANNELS & VIDEOS
    # ------------------------------------------------------------------
    def convert_iso8601_duration(duration):
        """Convert YouTube ISO 8601 duration (e.g., 'PT4M36S') to seconds.
        Returns: Duration in seconds, or input if already numeric"""
        # If duration is numeric (float or int) or NaN, return as-is or 0
        if isinstance(duration, (int, float)) and not np.isnan(duration):
            return int(duration)
        if not duration or pd.isna(duration):
            return 0
        # Process ISO 8601 string
        time_extractor = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        extracted = time_extractor.match(str(duration))
        if extracted:
            hours = int(extracted.group(1)) if extracted.group(1) else 0
            minutes = int(extracted.group(2)) if extracted.group(2) else 0
            seconds = int(extracted.group(3)) if extracted.group(3) else 0
            return hours * 3600 + minutes * 60 + seconds
        return 0

    def _transform(**context):
        # Pull JSONs
        channel_json = context["ti"].xcom_pull(task_ids="extract_channels")
        video_json = context["ti"].xcom_pull(task_ids="extract_videos")

        ch_df = pd.read_json(StringIO(channel_json), orient="records")
        vid_df = pd.read_json(StringIO(video_json), orient="records") if video_json else pd.DataFrame()

        # ---------- Channels ----------
        ch_df["views"] = ch_df["views"].astype("int64")
        ch_df["total_videos"] = ch_df["total_videos"].astype("int64")
        ch_df["subscribers"] = ch_df["subscribers"].astype("int64")
        ch_df["updated_at"] = datetime.utcnow()

        # ---------- Videos ----------
        if not vid_df.empty:
            vid_df["published_at"] = pd.to_datetime(vid_df["published_at"])
            # Convert duration from ISO string to seconds (int)
            vid_df["duration"] = vid_df["duration"].apply(convert_iso8601_duration)
            vid_df["view_count"] = vid_df["view_count"].astype("int64")
            vid_df["like_count"] = vid_df["like_count"].astype("int64")
            vid_df["comment_count"] = vid_df["comment_count"].astype("int64")

        # Save transformed files
        transformed_dir = os.path.join(BASE_DIR, "data/transformed")
        os.makedirs(transformed_dir, exist_ok=True)
        ch_df.to_csv(os.path.join(transformed_dir, "channels.csv"), index=False)
        if not vid_df.empty:
            vid_df.to_csv(os.path.join(transformed_dir, "videos.csv"), index=False)

        # Push for load
        context["ti"].xcom_push(key="channels_df", value=ch_df.to_json(orient="records"))
        context["ti"].xcom_push(key="videos_df", value=vid_df.to_json(orient="records"))

    transform = PythonOperator(
        task_id="transform",
        python_callable=_transform,
    )

    # ------------------------------------------------------------------
    # TRANSFORM COMMENTS (Sentiment Analysis)
    # ------------------------------------------------------------------
    def analyze_comments_sentiment(comments_json: str) -> str:
        """Apply VADER sentiment analysis to comments JSON.
        Returns: Transformed JSON for load."""
        comments_df = pd.read_json(StringIO(comments_json), orient="records") if comments_json else pd.DataFrame()

        # Initialize VADER
        vader_sia = SentimentIntensityAnalyzer()

        # Sentiment scoring
        def get_sentiment(text):
            return vader_sia.polarity_scores(text)["compound"] if isinstance(text, str) else 0.0

        # Sentiment categorization
        def categorize_sentiment(score):
            if score > 0.05:
                return "positive"
            elif score < -0.05:
                return "negative"
            return "neutral"

        # Apply sentiment analysis if DataFrame is not empty
        if not comments_df.empty:
            comments_df["vader_score"] = comments_df["comment_text"].apply(get_sentiment)
            comments_df["vader_sentiment"] = comments_df["vader_score"].apply(categorize_sentiment)
            print(f"Processed sentiment for {len(comments_df)} comments")
        else:
            print("No comments to process.")

        # Ensure columns exist (for empty DF)
        comments_df = comments_df.reindex(columns=[
            "comment_id", "video_id", "channel_id", "comment_text", "published_at",
            "vader_score", "vader_sentiment"
        ])

        # Save transformed
        transformed_dir = os.path.join(BASE_DIR, "data/transformed")
        os.makedirs(transformed_dir, exist_ok=True)
        comments_df.to_csv(os.path.join(transformed_dir, "comments.csv"), index=False)

        return comments_df.to_json(orient="records")

    def _transform_comments(**context):
        comments_json = context["ti"].xcom_pull(task_ids="extract_comments")
        transformed_comments_json = analyze_comments_sentiment(comments_json)
        context["ti"].xcom_push(key="comments_df", value=transformed_comments_json)

    transform_comments = PythonOperator(
        task_id="transform_comments",
        python_callable=_transform_comments,
    )

    # ------------------------------------------------------------------
    # 3. LOAD (Incremental)
    # ------------------------------------------------------------------
    def _load(**context):
        try:
            engine = create_engine(
                f"postgresql+psycopg2://{USER_NAME}:{PASSWORD}@{HOST_NAME}:{PORT_ID}/{DATABASE}"
            )

            print("Connected to social_media_db successfully")

            ch_json = context["ti"].xcom_pull(key="channels_df", task_ids="transform")
            vid_json = context["ti"].xcom_pull(key="videos_df", task_ids="transform")
            com_json = context["ti"].xcom_pull(key="comments_df", task_ids="transform_comments")

            ch_df = pd.read_json(StringIO(ch_json), orient="records") if ch_json else pd.DataFrame()
            vid_df = pd.read_json(StringIO(vid_json), orient="records") if vid_json else pd.DataFrame()
            com_df = pd.read_json(StringIO(com_json), orient="records") if com_json else pd.DataFrame()

            # Upsert channels
            if not ch_df.empty:
                metadata = MetaData()
                channels_table = Table('channels', metadata,
                    Column('channel_id', String, primary_key=True),
                    Column('channel_name', String),
                    Column('views', Integer),
                    Column('total_videos', Integer),
                    Column('subscribers', Integer),
                    Column('updated_at', DateTime)
                )
                stmt = insert(channels_table).values(ch_df.to_dict('records'))
                stmt = stmt.on_conflict_do_update(
                    index_elements=['channel_id'],
                    set_={
                        'channel_name': stmt.excluded.channel_name,
                        'views': stmt.excluded.views,
                        'total_videos': stmt.excluded.total_videos,
                        'subscribers': stmt.excluded.subscribers,
                        'updated_at': stmt.excluded.updated_at,
                    }
                )
                with engine.begin() as conn:
                    conn.execute(stmt)
                print(f"Upserted {len(ch_df)} channels")

            # Incremental videos: Append only new
            new_videos_added = 0
            if not vid_df.empty:
                existing_vids = pd.read_sql_query(text("SELECT video_id FROM videos"), engine)['video_id'].tolist()
                new_vids_df = vid_df[~vid_df['video_id'].isin(existing_vids)]
                print(f"Found {len(vid_df)} fetched videos; {len(existing_vids)} existing; {len(new_vids_df)} new")
                if not new_vids_df.empty:
                    new_vids_df.to_sql("videos", engine, if_exists="append", index=False, method="multi")
                    new_videos_added = len(new_vids_df)
                    print(f"Appended {new_videos_added} new videos")
                else:
                    print("No new videos—all fetched already exist in DB (incremental success)")
            else:
                print("No video data to load")

            # Incremental comments: Append only new
            new_comments_added = 0
            if not com_df.empty:
                existing_comments = pd.read_sql_query(text("SELECT comment_id FROM comments"), engine)['comment_id'].tolist()
                new_com_df = com_df[~com_df['comment_id'].isin(existing_comments)]
                print(f"Found {len(com_df)} fetched comments; {len(existing_comments)} existing; {len(new_com_df)} new")
                if not new_com_df.empty:
                    new_com_df.to_sql("comments", engine, if_exists="append", index=False, method="multi")
                    new_comments_added = len(new_com_df)
                    print(f"Appended {new_comments_added} new comments")
                else:
                    print("No new comments—all fetched already exist in DB (incremental success)")
            else:
                print("No comment data to load")

            # Success summary (always green, even 0 new)
            print(f"Load complete: {len(ch_df) if not ch_df.empty else 0} channels upserted, {new_videos_added} new videos appended, {new_comments_added} new comments appended")

        except Exception as e:
            print(f"LOAD FAILED: {e}")
            raise  # Raise only on true errors

    load = PythonOperator(
        task_id="load",
        python_callable=_load,
    )

    # ----------------------- TASK ORDER -----------------------
    extract_channels >> extract_videos >> extract_comments >> transform >> transform_comments >> load
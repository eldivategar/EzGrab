from fastapi import FastAPI, HTTPException, Query, APIRouter, Path, BackgroundTasks
from fastapi.responses import FileResponse
from pytubefix import YouTube, Search
from dotenv import load_dotenv
from middleware.cors import add_cors_middleware
from utils.sanitize_filename import sanitize_filename
from utils.storage_dir import youtube_storage_dir
import os

load_dotenv()

app = FastAPI(
    title="Youtube Downloader API",
    description="Simple API to download Youtube videos",
    version="1.0.0"
)
api_router = APIRouter(prefix="/api")
add_cors_middleware(app)

@api_router.get("/search")
async def search_video_on_youtube(
    query: str = Query(..., min_length=1, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(8, ge=1, le=50)
):
    search = Search(query, use_oauth=True, allow_oauth_cache=True)
    results = search.videos
    videos = []
    
    
    # Paginasi
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_results = results[start_index:end_index]
    
    for result in paginated_results:
        videos.append({
            "video_id": result.video_id,
            "title": result.title,
            "thumbnail": result.thumbnail_url,
            "length": result.length,
            "views": result.views,
            "rating": result.rating,
            "author": result.author,
            "publish_date": result.publish_date,
            "description": result.description,
        })

    return {
        "page": page,
        "page_size": page_size,
        "total_results": len(results),
        "total_pages": (len(results) + page_size - 1) // page_size,
        "results": videos
    }

# API for detail video
@api_router.get("/video/{video_id}")
async def get_video_detail(video_id: str = Path(..., min_length=1, max_length=100)):
    url = f"https://www.youtube.com/watch?v={video_id}"
    video = YouTube(url=url, use_oauth=True, allow_oauth_cache=True)
    return {
        "video_id": video.video_id,
        "title": video.title,
        "thumbnail": video.thumbnail_url,
        "length": video.length,
        "views": video.views,
        "rating": video.rating,
        "author": video.author,
        "publish_date": video.publish_date,
        "description": video.description,
        "streams": [stream.__dict__ for stream in video.streams],
        "audio_streams": [stream.__dict__ for stream in video.streams.filter(only_audio=True)],
        "video_streams": [stream.__dict__ for stream in video.streams.filter(only_video=True)]
    }

# API for download video/audio
@api_router.get("/download/{video_id}/{itag}")
async def download_video(
    video_id: str = Path(..., min_length=1, max_length=100),
    itag: int = Path(..., ge=1),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    url = f"https://www.youtube.com/watch?v={video_id}"
    video = YouTube(url=url, use_oauth=True, allow_oauth_cache=True)
    stream = video.streams.get_by_itag(itag)
    
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    title = stream.title
    resolution = stream.resolution if stream.type == "video" else stream.abr
    extension = stream.subtype if stream.type == "video" else "mp3"
    
    # Define filename and path
    filename = sanitize_filename(f"{title}-{resolution}.{extension}")
    output_path = youtube_storage_dir(video_id)
    full_path = os.path.join(output_path, filename)

    try:
        # Download the file
        stream.download(output_path=output_path, filename=filename)
        
        background_tasks.add_task(os.remove, full_path)
        
        # Serve the file
        response = FileResponse(
            full_path, 
            media_type="application/octet-stream",
            filename=filename,
        )
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)

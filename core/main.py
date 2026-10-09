from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, APIRouter, Depends, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from core.settings import settings
from core.llm.routes import LLM_router
from core.alert.routes import alerts_router
from core.telegram_client.routes import air_tg
from core.telegram_client.client import tg_client
from core.logger import get_logger
from core.services import speed_test, get_api_key
from core.models import HelloResponse, SpeedtestResponse
from core.limiter import limiter

from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to Telegram...")
    await tg_client.start()
    yield
    logger.info("Disconnecting Telegram...")
    await tg_client.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Async API that combines LLM analysis with Telegram and air-alert data.",
    lifespan=lifespan,
    docs_url="/api/v1/docs" if settings.LOCAL_DEV else None,
    redoc_url=None,
    openapi_url="/api/v1/openapi.json" if settings.LOCAL_DEV else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(LLM_router)
v1_router.include_router(air_tg)
v1_router.include_router(alerts_router)

origins = settings.CORS_ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@v1_router.get(
    "/hello/", response_model=HelloResponse, dependencies=[Depends(get_api_key)]
)
@limiter.limit("1/second")
async def hello(request: Request):
    """
    Health check endpoint.
    """
    return {"message": f"Hello! I'm {settings.PROJECT_NAME}"}


@v1_router.get(
    "/speedtest/", response_model=SpeedtestResponse, dependencies=[Depends(get_api_key)]
)
@limiter.limit("1/second")
async def speedtest(request: Request, in_bytes: bool = False):
    """
    Get server download and upload speed + ping.
    """
    result = await asyncio.to_thread(speed_test, in_bytes)
    return result


app.include_router(v1_router)

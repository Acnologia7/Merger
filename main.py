# import multiprocessing
# import asyncio
# import signal

# import uvicorn

# from app.core.config import get_settings
# from app.core.scheduler import setup_scheduler

# settings = get_settings()

# # Global references
# scheduler = None
# loop = None
# app_process = None
# shutdown_event = asyncio.Event()


# def run_fastapi_app():
#     uvicorn.run(
#         "app.server:app",
#         host=settings.APP_HOST,
#         port=settings.APP_PORT,
#         workers=settings.WORKERS_COUNT,
#     )


# async def shutdown():
#     global scheduler, app_process

#     print("🛑 Gracefully shutting down...")

#     if scheduler and scheduler.running:
#         print("⏹️  Stopping scheduler...")
#         scheduler.shutdown(wait=False)

#     if app_process:
#         print("🛑 Terminating FastAPI app...")
#         app_process.terminate()
#         app_process.join()

#     print("✅ All services stopped.")

#     shutdown_event.set()  # signal main() to exit


# def install_signal_handlers():
#     def handle_signal(sig, frame):
#         print("\n🔻 Caught termination signal")
#         # Safely schedule shutdown coroutine from within running loop
#         loop.call_soon_threadsafe(lambda: asyncio.create_task(shutdown()))

#     signal.signal(signal.SIGINT, handle_signal)
#     signal.signal(signal.SIGTERM, handle_signal)


# async def async_main():
#     global scheduler, loop, app_process

#     loop = asyncio.get_running_loop()
#     install_signal_handlers()

#     app_process = multiprocessing.Process(target=run_fastapi_app)
#     app_process.start()

#     scheduler = await setup_scheduler(loop)
#     scheduler.start()

#     print("✅ App and scheduler running. Press Ctrl+C to stop.")

#     # Wait until shutdown is triggered
#     await shutdown_event.wait()


# def main():
#     asyncio.run(async_main())


# if __name__ == "__main__":
#     main()


import asyncio
from asyncio import AbstractEventLoop
import signal
import uvicorn
from multiprocessing import Process
from app.core.config import get_settings, Settings
from app.core.scheduler import setup_scheduler


# class AppManager:
#     def __init__(self, settings):
#         self.settings: Settings = settings
#         self.scheduler = None
#         self.app_process = None
#         self.shutdown_event = asyncio.Event()

#     def run_fastapi_app(self):
#         uvicorn.run(
#             "app.server:app",
#             host=self.settings.APP_HOST,
#             port=self.settings.APP_PORT,
#             workers=self.settings.WORKERS_COUNT,
#         )

#     async def shutdown(self):
#         print("🛑 Gracefully shutting down...")

#         if self.scheduler and self.scheduler.running:
#             print("⏹️  Stopping scheduler...")
#             self.scheduler.shutdown(wait=False)

#         if self.app_process:
#             print("🛑 Terminating FastAPI app...")
#             self.app_process.terminate()
#             self.app_process.join()

#         print("✅ All services stopped.")
#         self.shutdown_event.set()

#     def install_signal_handlers(self, loop: AbstractEventLoop):
#         def handle_signal(sig, frame):
#             print("\n🔻 Caught termination signal")
#             loop.call_soon_threadsafe(lambda: asyncio.create_task(self.shutdown()))

#         signal.signal(signal.SIGINT, handle_signal)
#         signal.signal(signal.SIGTERM, handle_signal)

#     async def async_main(self):
#         loop = asyncio.get_running_loop()
#         self.install_signal_handlers(loop)

#         self.app_process = Process(target=self.run_fastapi_app)
#         self.app_process.start()

#         self.scheduler = await setup_scheduler(loop)
#         self.scheduler.start()

#         print("✅ App and scheduler running. Press Ctrl+C to stop.")
#         await self.shutdown_event.wait()

#     def run(self):
#         asyncio.run(self.async_main())


# if __name__ == "__main__":
#     settings = get_settings()
#     app_manager = AppManager(settings)
#     app_manager.run()


class AppManager:
    """
    Manages the lifecycle of the FastAPI application and its associated scheduler.

    The `AppManager` handles the initialization, startup, and graceful shutdown of
    the FastAPI app and its scheduler. It includes functionality to handle termination
    signals and perform cleanup tasks.

    Attributes:
        settings (Settings): The application settings containing configurations like host, port, and worker count.
        scheduler (Optional[AsyncIOScheduler]): The scheduler instance that runs periodic tasks.
        app_process (Optional[Process]): The process that runs the FastAPI application.
        shutdown_event (asyncio.Event): An event used to signal the shutdown of the app.
    """

    def __init__(self, settings):
        """
        Initializes the AppManager with application settings.

        Args:
            settings (Settings): The application settings used for configuring the FastAPI app and scheduler.
        """
        self.settings: Settings = settings
        self.scheduler = None
        self.app_process = None
        self.shutdown_event = asyncio.Event()

    def run_fastapi_app(self):
        """
        Runs the FastAPI app using uvicorn.

        This method starts the FastAPI app with configurations for host, port, and number of workers
        defined in the application settings.

        Args:
            None
        """
        uvicorn.run(
            "app.server:app",
            host=self.settings.APP_HOST,
            port=self.settings.APP_PORT,
            workers=self.settings.WORKERS_COUNT,
        )

    async def shutdown(self):
        """
        Gracefully shuts down the FastAPI app and the scheduler.

        This method stops the scheduler (if running), terminates the FastAPI app process,
        and signals the shutdown event.

        Args:
            None
        """
        print("🛑 Gracefully shutting down...")

        if self.scheduler and self.scheduler.running:
            print("⏹️  Stopping scheduler...")
            self.scheduler.shutdown(wait=False)

        if self.app_process:
            print("🛑 Terminating FastAPI app...")
            self.app_process.terminate()
            self.app_process.join()

        print("✅ All services stopped.")
        self.shutdown_event.set()

    def install_signal_handlers(self, loop: AbstractEventLoop):
        """
        Installs signal handlers for termination signals.

        This method listens for termination signals (SIGINT and SIGTERM) and triggers
        the shutdown process when received.

        Args:
            loop (AbstractEventLoop): The asyncio event loop used for handling signals.
        """

        def handle_signal(sig, frame):
            print("\n🔻 Caught termination signal")
            loop.call_soon_threadsafe(lambda: asyncio.create_task(self.shutdown()))

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    async def async_main(self):
        """
        The main asynchronous entry point for the application.

        This method sets up the signal handlers, starts the FastAPI app process, and initializes
        and starts the scheduler. It also waits for the shutdown event to be set when the app
        is ready to stop.

        Args:
            None
        """
        loop = asyncio.get_running_loop()
        self.install_signal_handlers(loop)

        self.app_process = Process(target=self.run_fastapi_app)
        self.app_process.start()

        self.scheduler = await setup_scheduler(loop)
        self.scheduler.start()

        print("✅ App and scheduler running. Press Ctrl+C to stop.")
        await self.shutdown_event.wait()

    def run(self):
        """
        Starts the application by running the asynchronous main method.

        This method is the entry point for running the application, which sets up the event loop
        and starts the app and scheduler.

        Args:
            None
        """
        asyncio.run(self.async_main())


if __name__ == "__main__":
    settings = get_settings()
    app_manager = AppManager(settings)
    app_manager.run()

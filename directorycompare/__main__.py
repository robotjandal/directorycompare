"""
    Invokes directorycompare as a script.

    Arguments are required see help for details.
"""
from directorycompare import app

if __name__ == "__main__":
    import time
    start_time = time.process_time()
    app.run()
    print(f"Rough program time: {time.process_time() - start_time}")

import uvicorn
import time
LOG = 'debug'

if __name__ == '__main__':
    try:
        if LOG == 'debug':
            uvicorn.run(
                "api:app",
                host='0.0.0.0',
                port=8080,
                workers=1,
                log_level='info',
                reload=True,
            )
        else:
            uvicorn.run(
                "api:app",
                host='0.0.0.0',
                port=8080,
                workers=5,
                log_level='warning',
                reload=False,
            )
    except KeyboardInterrupt:
        print('\nExiting\n')
    except Exception as errormain:
        print('Failed to Start API')
        print('='*100)
        print(str(errormain))
        print('='*100)
        print('Exiting\n')
    while True:
        time.sleep(1)  # Keep the process running to handle requests
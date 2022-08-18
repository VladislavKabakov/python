import asyncio
import aiofiles

async def async_read_large_file():
    async with aiofiles.open('..\\data\\a_file.txt', 'r') as f:
        return await f.read()

def count_words(text):
    return len(text.aplit(' '))

async def async_main():
    text = await async_read_large_file()
    print(count_words(text))

if __name__ == '__main__':
    asyncio.run(async_main())
    

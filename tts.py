import asyncio, json, sys, os
import edge_tts
VOICES = sys.argv[1].split(",")
RATE = sys.argv[2] if len(sys.argv) > 2 else "+0%"
scenes = json.load(open("scenes.json"))
os.makedirs("out", exist_ok=True)
async def one(s, voice):
    c = edge_tts.Communicate(s["text"], voice, rate=RATE, boundary="WordBoundary")
    words = []
    with open(f"out/{voice}/{s['id']}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] in ("WordBoundary", "SentenceBoundary"):
                words.append({"t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7, "w": ch["text"]})
    json.dump(words, open(f"out/{voice}/{s['id']}.json", "w"), ensure_ascii=False)
async def main():
    for v in VOICES:
        os.makedirs(f"out/{v}", exist_ok=True)
        for s in scenes:
            for attempt in range(4):
                try:
                    await one(s, v); break
                except Exception as e:
                    print("retry", s["id"], e); await asyncio.sleep(3)
            print("ok", v, s["id"])
asyncio.run(main())


from io import BytesIO
from fastapi import FastAPI
from fastapi.responses import Response
import torch


app = FastAPI()


@app.get(
    "/imagine",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def generate(prompt: str, img_size: int = 512):
    assert len(prompt), "prompt parameter cannot be empty"
    sd = StableDiffusionV2()
    image = await sd.generate(prompt, img_size=img_size)
    file_stream = BytesIO()
    image.save(file_stream, "PNG")
    return Response(content=file_stream.getvalue(), media_type="image/png")


class StableDiffusionV2:
    def __init__(self):
        from diffusers import EulerDiscreteScheduler, StableDiffusionPipeline

        model_id = "stabilityai/stable-diffusion-2"

        scheduler = EulerDiscreteScheduler.from_pretrained(
            model_id, subfolder="scheduler"
        )
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id, scheduler=scheduler, revision="fp16", torch_dtype=torch.float16
        )
        self.pipe = self.pipe.to("cuda")

    async def generate(self, prompt: str, img_size: int = 512):
        assert len(prompt), "prompt parameter cannot be empty"

        with torch.autocast("cuda"):
            image = self.pipe(prompt, height=img_size, width=img_size).images[0]
            return image

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

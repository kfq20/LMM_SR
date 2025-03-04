from huggingface_hub import hf_hub_download

file_path = hf_hub_download(
    repo_id="Fancylalala/ViSR",
    filename="data/video.zip",
    repo_type="dataset"
)

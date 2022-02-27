#!/usr/bin/env python3
import boto3
import boto3.s3
from botocore.exceptions import ClientError
import json
import logging
import os
import random
import re
import string
import time
import urllib.request
import yaml

# Credentials: https://docs.aws.amazon.com/sdk-for-php/v3/developer-guide/guide_credentials_profiles.html


def transcribe(
    job_name: str,
    s3_object_url: str,
    region: str,
    media_format: str = "wav",
    language_code: str = "en-US",
):
    # Build transcribe client object
    transcribe = boto3.client("transcribe", region_name=region)
    job_name = job_name
    job_uri = s3_object_url
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": job_uri},
        MediaFormat=media_format,
        LanguageCode=language_code,
    )

    # Get to work
    print("Transcribing .", end="")
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status["TranscriptionJob"]["TranscriptionJobStatus"] in ["COMPLETED", "FAILED"]:
            break
        print(".", end="")
        time.sleep(5)
    print()

    # Inspect the results
    transcript_file_uri = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    with urllib.request.urlopen(transcript_file_uri) as url:
        data = json.loads(url.read().decode())
        transcripts = data["results"]["transcripts"]
        items = data["results"]["items"]
        first_tscr = transcripts[0]["transcript"]
        first_tscr_alts = [i for i in items if i["type"] == "pronunciation"][0]["alternatives"][0]
        first_tscr_alt_confidence = first_tscr_alts["confidence"]

        print(f'Result: "{first_tscr}" (First transcript), confidence: {first_tscr_alt_confidence}')
        # print(yaml.dump(data))


def upload_file(file_name, bucket_name, object_name, region) -> str:
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client("s3", region_name=region)
    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        logging.error(e)
        return ""

    bucket_location = boto3.client("s3").get_bucket_location(Bucket=bucket_name)
    return "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        bucket_location["LocationConstraint"],
        bucket_name,
        object_name,
    )


def main():
    # Input audio file, transcribe supports loads of extensions
    # You could argparse this if so inclined
    audio_file_name = "poacher_full.mp3"
    audio_file_format = re.match(r".*\.(\S+)$", audio_file_name).group(1)

    # settings is a yaml file with keys:
    #   bucket_name<str>
    #   region<str>
    settings = yaml.safe_load(open("creds.yaml").read())
    bucket_name = settings["bucket_name"]
    region = settings["region"]

    # Random string stamp to identify the uploaded file and the transcribe job (it's ID)
    rstamp = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    object_name = f"{rstamp}-audio.{audio_file_format}"
    job_name = f"job-{rstamp}"

    print("Uploading to S3 ... ", end="")

    object_url = upload_file(
        file_name=audio_file_name,
        bucket_name=bucket_name,
        object_name=object_name,
        region=region,
    )

    print("done!")

    transcribe(
        job_name=job_name,
        s3_object_url=object_url,
        media_format=audio_file_format,
        region=region,
    )


if __name__ == "__main__":
    main()

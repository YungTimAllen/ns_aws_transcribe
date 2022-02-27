**Using AWS Transcribe for Speech-to-Text on Number Station recordings**

## Example

* Input file was `poacher_full.mp3`

```commandline
Uploading to S3 ... done!
Transcribing .......
Result: "Yeah. Yeah. Yeah. 397153971539715397152. Mhm. Mhm. Mhm. 6647566475." (First transcript), confidence: 0.2741
```

For the given audio file, whilst the transcribing service interpreted the music/tones as speech, the numbers are
transcribed almost correctly (Theres an erroneous '2' after the opening 5-symbol groups)

### References

* Audio Source: https://priyom.org/